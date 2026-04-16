# Files and Attachments

In this task you will work with DIAL file attachments — reading images sent by users, displaying them in stages, and
returning audio output as an attachment the user can play back in Chat.

---

## Files Assistant — Images In, Audio Out

The Files Assistant accepts image attachments, forwards them to a multimodal LLM, and converts the text response to
speech using a TTS model — attaching the resulting audio file to the reply.

### Application flow

```
User message + image attachment(s)
        │
        ▼
[1] Show raw message in a stage
[2] Show image preview(s) in stage(s)     ← TODO1
[3] Call multimodal LLM (image URL passed as-is)
[4] Stream text response to choice
[5] Call TTS model with the text content
[6] Attach audio to stage and choice      ← TODO2
        │
        ▼
Assistant reply + audio attachment
```

---

### Steps

1. **Read [t5_files/files_assistant.py](t5_files/files_assistant.py) in full first**

   Key methods:

   | Method | Description |
      |--------|-------------|
   | `chat_completion` | Main handler — orchestrates all steps |
   | `show_message_stage(name, choice, message)` | Creates a stage that renders the message as JSON |
   | `show_attachments_in_stage(choice, request)` | Reads incoming attachments; renders image previews in stages |
   | `response_to_audio(client, content, choice)` | Calls TTS model; forwards audio attachment to `choice` |

2. **Implement the TODO blocks in [files_assistant.py](files_assistant.py)**

   - Implement **TODO1** — `show_attachments_in_stage()`
   - Implement **TODO2** — audio attachment forwarding inside `response_to_audio()`

3. **Open [core/applications.json](/core/applications.json) and add such app config**:
   ```json
   "files-assistant": {
     "displayName": "Files Agent",
     "description": "AI assistant that can answer general questions, works with pictures as input content, and converts answers to audio",
     "endpoint": "http://host.docker.internal:5029/openai/deployments/files-assistant/chat/completions",
     "inputAttachmentTypes": [
       "image/png",
       "image/jpg"
     ],
     "maxInputAttachments": 3
   }
   ```
   
4. **Run [t5_files/files_assistant.py](t5_files/files_assistant.py)**

5. **Open [DIAL Chat](http://localhost:3000/marketplace) and test Files Agent**:
    - Click the paperclip / attachment icon in the chat input
    - Upload a PNG or JPEG image (or this image [attachment-info.png](attachment-info.png))
    - Send a message such as `"What is in this image?"`
    - Verify that:
        - A stage shows the raw message JSON
        - A stage shows the image preview (rendered inline via markdown)
        - The text answer streams in
        - An audio file appears as an attachment below the reply and can be played back

6. **Inspect local file storage** — after uploading, browse to:
   [/core-data/dial...](/core-data/dial/Keys/DIAL-COURSE-FOR-DEVELOPERS/files/uploads/)
   The uploaded image is stored here. This local filesystem path is the DIAL bucket for the development environment.
   In production this would be replaced by cloud blob storage (AWS S3, Google Cloud Storage, or Azure Blob Storage).

7. **Explore the DIAL Files API directly**

   Get your bucket name:
   ```bash
   curl --location 'http://localhost:8080/v1/bucket' \
     --header 'Api-Key: dial_api_key'
   ```

   List metadata for the uploads folder:
   ```bash
   curl --location 'http://localhost:8080/v1/metadata/files/{bucket}/uploads/' \
     --header 'Api-Key: dial_api_key'
   ```

<details><summary>Final result:</summary>

![Answer](/tasks/t5_files/_screenshots/response.png)
![User message with image attachment](/tasks/t5_files/_screenshots/user_message.png)
![Full response with audio attachment](/tasks/t5_files/_screenshots/full_answer.png)
![Local storage on disk](/tasks/t5_files/_screenshots/local-storage.png)

</details>

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. `custom_content` is `None` when no attachments

Not every message carries attachments. Accessing `.attachments` directly on `None` raises `AttributeError`.

```python
# WRONG — crashes when there are no attachments
for att in request.messages[-1].custom_content.attachments:
    ...

# CORRECT — guard both levels
if custom_content := request.messages[-1].custom_content:
    if attachments := custom_content.attachments:
        for attachment in attachments:
            ...
```

---

### 2. Attachment URL is a DIAL-internal path, not a public HTTP URL

When a user uploads a file through DIAL Chat, the `attachment.url` value is a **relative DIAL path** such as
`files/{bucket}/uploads/image.png`. It is NOT a full HTTP URL. You can pass it directly to models
via DIAL Core (Core resolves it internally), but you cannot open it in a browser without the `Api-Key` header and the
full base URL prefix.

```python
# Passing to a model through DIAL Core — works as-is
message.dict(exclude_none=True)  # url is resolved by Core

# Rendering in a stage — Chat proxies it
stage.append_content(f"![image]({attachment.url})")  # Chat resolves the relative path
```

---

### 3. Stage not closed after the attachment loop

If an exception is raised mid-loop, the last opened stage stays open and the HTTP response hangs. Always close in
`finally`:

```python
stage: Stage | None = None
try:
    for attachment in attachments:
        stage = _StageProcessor.open_stage(choice, "Attachment content: ")
        stage.append_content(...)
except Exception as e:
    print(e)
finally:
    if stage:
        _StageProcessor.close_stage_safely(stage)
```

---

### 4. `inputAttachmentTypes` missing — no attachment button in Chat

Without `inputAttachmentTypes` in `applications.json`, DIAL Chat does not show the file-picker button for this
application at all. The field explicitly tells Chat which MIME types to accept.

---

### 5. `model_dump()` vs `dict(exclude_none=True)`

DIAL SDK attachment objects have a `model_dump()` method (Pydantic v2). When forwarding attachments to `add_attachment`,
use `**attachment.model_dump()`. Do not use the older `.dict()` on Pydantic v2 models — it still works but is
deprecated.

---

### 6. Port mismatch

| App                  | Port |
|----------------------|------|
| `files_assistant.py` | 5029 |

The port in `uvicorn.run(app, port=5029)` must match the port in the `endpoint` URL in `applications.json`.

</details>
