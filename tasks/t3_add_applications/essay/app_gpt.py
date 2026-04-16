import uvicorn

from aidial_sdk import DIALApp

from tasks.t3_add_applications.essay.essay_assistant import EssayAssistantApplication

app: DIALApp = DIALApp()

app.add_chat_completion(deployment_name="essay-assistant-gpt", impl=EssayAssistantApplication("gpt-5.2"))

if __name__ == "__main__":
    uvicorn.run(app, port=5025, host="0.0.0.0")