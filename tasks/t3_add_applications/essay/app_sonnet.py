import uvicorn

from aidial_sdk import DIALApp

from tasks.t3_add_applications.essay.essay_assistant import EssayAssistantApplication

app: DIALApp = DIALApp()

app.add_chat_completion(deployment_name="essay-assistant-sonnet", impl=EssayAssistantApplication("claude-sonnet-4-6"))

if __name__ == "__main__":
    uvicorn.run(app, port=5026, host="0.0.0.0")