import uvicorn

from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import (
    ChatCompletion, Request, Response
)

from tasks.t4_stage_and_state.t2_calculator_agent.agent import CalculatorAgent
from tasks.t4_stage_and_state.t2_calculator_agent.calculator_tool import CalculateTool


class CalculatorAgentApplication(ChatCompletion):

    async def chat_completion(self, request: Request, response: Response) -> None:
        with response.create_single_choice() as choice:
            await CalculatorAgent(
                dial_core_url="http://localhost:8080",
                tools=[
                    CalculateTool()
                ],
            ).handle_request(
                deployment_name="gpt-5.2",
                choice=choice,
                request=request
            )


app = DIALApp()
app.add_chat_completion("calculator-agent", CalculatorAgentApplication())

if __name__ == "__main__":
    uvicorn.run(app, port=5028, host="0.0.0.0")
