from typing import Union

from aidial_client import AsyncDial

from aidial_sdk.chat_completion import ChatCompletion, Request, Response
from aidial_sdk.deployment.configuration import ConfigurationRequest, ConfigurationResponse

SYSTEM_PROMPT = """You are an essay-focused assistant. Respond to every request by writing a **short essay** of up to 100 tokens.

**Structure:**
- Clear introduction with thesis
- Body paragraphs with supporting points
- Concise conclusion

**Rules:**
- Always write in essay format regardless of topic
- Keep responses analytical and structured
- Use formal, academic tone
- Include specific examples when relevant
- Maintain logical flow between paragraphs
"""


class EssayAssistantApplication(ChatCompletion):

    def __init__(self, model: str):
        self.model = model

    async def chat_completion(self, request: Request, response: Response) -> None:
        client: AsyncDial = AsyncDial(
            base_url="http://localhost:8080",
            api_key="dial_api_key",
            api_version="2025-01-01-preview"
        )

        print(request.messages[-1])

        with response.create_single_choice() as choice:
            chunks = await client.chat.completions.create(
                deployment_name=self.model,
                stream=True,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": request.messages[-1].content
                    }
                ],
            )

            async for chunk in chunks:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        choice.append_content(delta.content)

    async def configuration(self, request: ConfigurationRequest) -> Union[ConfigurationResponse, dict]:
        return {
            "type": "object",
            "properties": {
                "conversation_starter_button": {
                    "description": "Conversation starters",
                    "type": "number",
                    "dial:widget": "buttons",
                    "oneOf": [
                        {
                            "const": 1,
                            "title": "About elephant in space",
                            "dial:widgetOptions": {"populateText": "Generate me one about elephant in space"}
                        },
                        {
                            "const": 2,
                            "title": "About dog that can sing",
                            "dial:widgetOptions": {"populateText": "Generate essay about dog that can sing"}
                        }
                    ]
                }
            }
        }
