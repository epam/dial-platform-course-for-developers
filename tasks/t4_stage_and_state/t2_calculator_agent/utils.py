import copy
from typing import Any

from aidial_sdk.chat_completion import Choice, Message
from aidial_sdk.chat_completion import Role
from aidial_sdk.chat_completion.stage import Stage


class StageProcessor:
    @staticmethod
    def open_stage(choice: Choice, name: str) -> Stage:
        stage = choice.create_stage(name)
        stage.open()
        return stage

    @staticmethod
    def close_stage_safely(stage: Stage) -> None:
        try:
            stage.close()
        except Exception:
            pass


def unpack_messages(messages: list[Message], current_state_history: list[dict[str, Any]], tool_call_history_key: str) -> \
list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for message in messages:
        if message.role == Role.ASSISTANT:
            if custom_content := message.custom_content:
                # Unpack tool call history from Assistant message State
                state = custom_content.state
                if state and isinstance(state, dict):
                    tool_call_history = state.get(tool_call_history_key)
                    if tool_call_history and isinstance(tool_call_history, list):
                        for history_msg in tool_call_history:
                            if history_msg.get("role") == Role.TOOL.value:
                                result.append(
                                    {
                                        "role": Role.TOOL.value,
                                        "content": history_msg.get("content"),
                                        "tool_call_id": history_msg.get("tool_call_id"),
                                    }
                                )
                            else:
                                result.append(history_msg)

                    msg = copy.deepcopy(message)
                    msg.custom_content = None
                    result.append(msg.dict(exclude_none=True))
        else:
            content = message.content or ''
            result.append(
                {
                    "role": message.role,
                    "content": content
                }
            )

    if current_state_history:
        for history_msg in current_state_history:
            if history_msg.get("custom_content"):
                del history_msg['custom_content']
            result.append(history_msg)

    return result
