from typing import Union

import uvicorn

from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import (
    ChatCompletion, Request, Response
)
from aidial_sdk.deployment.configuration import ConfigurationRequest, ConfigurationResponse

from tasks.t8_agent.app.agent import Agent
from tasks.t8_agent.app.tools.deployment.essay_generation_tool import EssayGenerationTool
from tasks.t8_agent.app.tools.deployment.image_generation_tool import ImageGenerationTool
from tasks.t8_agent.app.tools.deployment.microwave_rag_tool import MicrowaveRagTool

_DIAL_CORE_URL="http://localhost:8080"

class FinalTaskAgentApplication(ChatCompletion):

    async def chat_completion(self, request: Request, response: Response) -> None:
        with response.create_single_choice() as choice:
            await Agent(
                dial_core_url=_DIAL_CORE_URL,
                tools=[
                    ImageGenerationTool(_DIAL_CORE_URL),
                    EssayGenerationTool(_DIAL_CORE_URL),
                    MicrowaveRagTool(_DIAL_CORE_URL),
                ],
            ).handle_request(
                deployment_name="gpt-5.2",
                choice=choice,
                request=request
            )

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
                            "title": "Calculate 3943232/4902*323",
                            "dial:widgetOptions": {"populateText": "Calculate 3943232/4902*323"}
                        },
                        {
                            "const": 2,
                            "title": "Generate 3 red dots",
                            "dial:widgetOptions": {"populateText": "Generate picture with 3 small red dots on the white background"}
                        }
                    ]
                }
            }
        }


app = DIALApp()
app.add_chat_completion("final-task-agent", FinalTaskAgentApplication())

if __name__ == "__main__":
    uvicorn.run(app, port=5032, host="0.0.0.0")
