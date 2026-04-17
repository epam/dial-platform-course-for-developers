import asyncio
import json
from typing import Any

from aidial_client import AsyncDial
from aidial_sdk.chat_completion import Choice, Message, Role, Request, ToolCall

from tasks.t8_agent.app.tools.base import BaseTool
from tasks.t8_agent.app.tools.models import ToolCallParams
from tasks.t8_agent.app.utils import StageProcessor, unpack_messages

_TOOL_CALL_HISTORY_KEY = "tool_call_history"

_SYSTEM_PROMPT = "You are a helpful AI assistant. Your task is to assist user with their questions."


class Agent:

    def __init__(self, dial_core_url: str, tools: list[BaseTool]):
        self.dial_core_url = dial_core_url
        self.tools = tools
        self._tools_dict: dict[str, Any] = {tool.name: tool for tool in tools}
        self.state: dict = {_TOOL_CALL_HISTORY_KEY: []}

    async def handle_request(
            self, deployment_name: str, choice: Choice, request: Request
    ) -> Message:
        client: AsyncDial = AsyncDial(
            base_url=self.dial_core_url,
            api_key=request.api_key,
            api_version="2025-01-01-preview"
        )

        chunks = await client.chat.completions.create(
            messages=self._prepare_messages(request.messages),
            tools=[tool.schema for tool in self.tools],
            stream=True,
            deployment_name=deployment_name,
        )

        tool_call_index_map: dict = {}
        content = ""

        async for chunk in chunks:
            if not (chunk.choices and len(chunk.choices) > 0):
                continue
            delta = chunk.choices[0].delta
            if not delta:
                continue

            if delta.content:
                choice.append_content(delta.content)
                content += delta.content

            if delta.tool_calls:
                for tc_delta in delta.tool_calls:
                    if tc_delta.id:
                        # First chunk for this tool call — store it keyed by index
                        tool_call_index_map[tc_delta.index] = tc_delta
                    else:
                        # Subsequent chunks — accumulate arguments
                        tc = tool_call_index_map[tc_delta.index]
                        if tc_delta.function:
                            tc.function.arguments += tc_delta.function.arguments or ""

        assistant_message = Message(
            role=Role.ASSISTANT,
            content=content,
            tool_calls=[ToolCall.validate(tc) for tc in tool_call_index_map.values()] or None,
        )

        if assistant_message.tool_calls:
            tasks = [
                self._process_tool_call(tool_call=tc, choice=choice, api_key=request.api_key)
                for tc in assistant_message.tool_calls
            ]
            tool_messages: list[dict] = await asyncio.gather(*tasks)

            self.state[_TOOL_CALL_HISTORY_KEY].append(assistant_message.dict(exclude_none=True))
            self.state[_TOOL_CALL_HISTORY_KEY].extend(tool_messages)

            # Recurse: let the model produce its final answer using the tool results
            return await self.handle_request(
                deployment_name=deployment_name,
                choice=choice,
                request=request
            )

        choice.set_state(self.state)
        return assistant_message

    def _prepare_messages(self, messages: list[Message]) -> list[dict]:
        unpacked_messages = unpack_messages(
            messages=messages,
            current_state_history=self.state[_TOOL_CALL_HISTORY_KEY],
            tool_call_history_key=_TOOL_CALL_HISTORY_KEY
        )
        unpacked_messages.insert(
            0,
            {
                "role": Role.SYSTEM.value,
                "content": _SYSTEM_PROMPT,
            }
        )

        print("\nHistory:")
        for msg in unpacked_messages:
            print(f"     {json.dumps(msg)}")

        print(f"{'-' * 100}\n")

        return unpacked_messages

    async def _process_tool_call(self, tool_call: ToolCall, choice: Choice, api_key: str) -> dict:
        stage = StageProcessor.open_stage(choice, tool_call.function.name)
        try:
            tool = self._tools_dict[tool_call.function.name]
            stage.append_content(
                f"## Arguments:\n```json\n"
                f"{json.dumps(json.loads(tool_call.function.arguments), indent=2)}\n"
                f"```\n\n"
            )
            tool_message = await tool.execute(
                ToolCallParams(
                    tool_call=tool_call,
                    stage=stage,
                    choice=choice,
                    api_key=api_key
                )
            )
        except Exception as e:
            tool_message = Message(
                role=Role.TOOL,
                content=f"Error: {e}",
                tool_call_id=tool_call.id,
            )
        finally:
            StageProcessor.close_stage_safely(stage)

        return tool_message.dict(exclude_none=True)
