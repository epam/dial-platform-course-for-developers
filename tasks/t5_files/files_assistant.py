import json

import uvicorn
from aidial_client import AsyncDial
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response, Choice, Stage

SYSTEM_PROMPT = """You are a helpful assistant. Answer questions clearly and concisely. 
Be honest when you don't know something. 
Stay friendly, professional, and avoid harmful or misleading content.
"""


class _StageProcessor:
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


class FilesAssistantApplication(ChatCompletion):

    def __init__(self, model: str):
        self.model = model

    async def chat_completion(self, request: Request, response: Response) -> None:
        client: AsyncDial = AsyncDial(
            base_url="http://localhost:8080",
            api_key="dial_api_key",
            api_version="2025-01-01-preview"
        )

        message = request.messages[-1]
        print(message)

        with response.create_single_choice() as choice:

            self.show_message_stage(
                name="User message",
                choice=choice,
                message=message.dict(exclude_none=True)
            )
            self.show_attachments_in_stage(choice=choice, request=request)

            chunks = await client.chat.completions.create(
                deployment_name=self.model,
                stream=True,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    message.dict(exclude_none=True)
                ]
            )

            content: list[str] = []
            async for chunk in chunks:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        choice.append_content(delta.content)
                        content.append(delta.content)

            await self.response_to_audio(client, content, choice)

    def show_message_stage(self, name: str, choice: Choice, message: dict):
        stage = _StageProcessor.open_stage(choice, f"Message: {name}")
        stage.append_content(
            f"## Arguments:\n```json\n"
            f"{json.dumps(message, indent=2)}\n"
            f"```\n\n"
        )
        _StageProcessor.close_stage_safely(stage)

    def show_attachments_in_stage(self, choice: Choice, request: Request):
        if custom_content := request.messages[-1].custom_content:
            if attachments := custom_content.attachments:
                stage: Stage | None = None
                try:
                    for attachment in attachments:
                        stage = _StageProcessor.open_stage(choice, "Attachment content: ")
                        if attachment.title:
                            stage.append_name(attachment.title)

                        if attachment.type in ["image/png", "image/jpg"]:
                            stage.append_content(f"\n\r![image]({attachment.url})\n\r")
                        else:
                            stage.append_content(f"Unsupported attachment type: {attachment.type}")
                except Exception as e:
                    print(e)
                finally:
                    if stage:
                        _StageProcessor.close_stage_safely(stage)

    async def response_to_audio(self, client: AsyncDial, content: list[str], choice: Choice, ):
        audio_content = await client.chat.completions.create(
            deployment_name="gpt-4o-mini-tts",
            messages=[
                {
                    "role": "user",
                    "content": "".join(content)
                }
            ]
        )
        stage = _StageProcessor.open_stage(choice, "Response to audio content")

        self.show_message_stage(
            name="Audio message",
            choice=choice,
            message=audio_content.choices[0].message.model_dump(exclude_none=True)
        )

        try:
            if custom_content := audio_content.choices[0].message.custom_content:
                if attachments := custom_content.attachments:
                    for attachment in attachments:
                        stage.add_attachment(**attachment.model_dump())
                        choice.add_attachment(**attachment.model_dump())
        except Exception as e:
            print(e)
        finally:
            _StageProcessor.close_stage_safely(stage)


app: DIALApp = DIALApp()

app.add_chat_completion(deployment_name="files-assistant", impl=FilesAssistantApplication("gpt-5.2"))

if __name__ == "__main__":
    uvicorn.run(app, port=5029, host="0.0.0.0")
