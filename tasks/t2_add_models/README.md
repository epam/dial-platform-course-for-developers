# Add models to DIAL

In this task we will add different models to DIAL

## 1. Add OpenAI LLM:

1. Open the [models.json](/core/models.json) and add into `"models"` section:
   ```json
     "gpt-5.2": {
       "displayName": "GPT 5.2",
       "description": "GPT‑5.2 is OpenAI’s most capable and efficient frontier model, built to deliver faster, more reliable results across complex professional and agentic workflows.",
       "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-5.2/chat/completions",
       "iconUrl": "http://localhost:3001/gpt3",
       "type": "chat"
     }
   ```
2. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
     "gpt-5.2": {
       "upstreams": [
         {
           "endpoint": "https://api.openai.com/v1/responses",
           "key": "${OPENAI_API_KEY}"
         }
       ]
     }
   ```
3. Replace `${OPENAI_API_KEY}` with your OpenAI API Key
4. Add `adapter-dial-openai` service to [docker compose](/docker-compose.yml) :
   ```yaml
     adapter-dial-openai:
       image: epam/ai-dial-adapter-openai:latest
       #platform: linux/amd64
       environment:
         DIAL_URL: "http://core:8080"
         LOG_LEVEL: "INFO"
         DIAL_USE_FILE_STORAGE: "True"
         GPT_IMAGE_1_DEPLOYMENTS: gpt-image-1.5, gpt-image-1, gpt-image-1-mini
   ```
   > For Mac uncomment `platform: linux/amd64`
   
   > `GPT_IMAGE_1_DEPLOYMENTS` is needed for later steps when we configure Image Gen models

5. Rerun docker-compose to fetch configs immediately and start OpenAI adapter service:
      ```bash
      docker compose stop && docker compose up -d --build
      ```

6. Open in browser [local dial chat](http://localhost:3000/marketplace) and test it:
    ```text
    Hi, what can you?
    ```
   
<details><summary>Final result:</summary>

![](/tasks/t2_add_models/_screenshots/marketplace.png)
![](/tasks/t2_add_models/_screenshots/chat.png)

</details>

---

## 2. Support Responses API for OpenAI LLM:

DIAL Follows [Azure OpenAI Spec](https://learn.microsoft.com/en-us/azure/foundry/openai/reference) and support both
[/chat/completions](https://learn.microsoft.com/en-us/azure/foundry/openai/latest#create-chat-completion) API and 
[/responses](https://learn.microsoft.com/en-us/azure/foundry/openai/latest#create-response) API.

Now, let's add support for responses API in DIAL Core:
1. Open the [models.json](/core/models.json) and refactor `"models"` -> `gpt-5.2` section, add there 
   ```json
     "overrideName": "gpt-5.2",
     "responsesEndpoint": "http://adapter-dial-openai:5000/openai/v1/responses",
   ```
   Final config:
   ```json
       "gpt-5.2": {
         "displayName": "GPT 5.2",
         "description": "GPT‑5.2 is OpenAI’s most capable and efficient frontier model, built to deliver faster, more reliable results across complex professional and agentic workflows.",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-5.2/chat/completions",
         "overrideName": "gpt-5.2",
         "responsesEndpoint": "http://adapter-dial-openai:5000/openai/v1/responses",
         "iconUrl": "http://localhost:3001/gpt3.svg",
         "type": "chat"
       }
   ```
2. Open the [models-keys.json](/core/models-keys.json) and refactor `"models"` -> `gpt-5.2` -> `upstreams` section, and add there:
   ```json
   "responsesEndpoint": "https://api.openai.com/v1/responses",
   ```
   Final config:
   ```json
     "gpt-5.2": {
       "upstreams": [
         {
           "endpoint": "https://api.openai.com/v1/responses",
           "responsesEndpoint": "https://api.openai.com/v1/responses",
           "key": "${OPENAI_API_KEY}"
         }
       ]
     }
   ```

3. Test it with such a request:
   ```json
   curl --location 'http://localhost:8080/openai/v1/responses' \
   --header 'Api-Key: dial_api_key' \
   --header 'Content-Type: application/json' \
   --data '{
       "stream": false,
       "model": "gpt-5.2",
       "input": [
           {
               "role": "user",
               "content": "Can I add `strict`: true, when using anthropic models?"
           }
       ]
   }'
   ```

---

## 3. Add OpenAI Image Gen model:

1. Open the [models.json](/core/models.json) and add into `"models"` section:
   ```json
      "gpt-image-1.5": {
         "displayName": "GPT Image 1.5",
         "description": "GPT Image 1.5 is OpenAI’s most capable model for Image generation.",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-image-1.5/chat/completions",
         "iconUrl": "http://localhost:3001/gpt3.svg",
         "type": "chat"
      }
   ```
2. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
      "gpt-image-1.5": {
         "upstreams": [
            {
               "endpoint": "https://api.openai.com/v1/images/generations",
               "key": "${OPENAI_API_KEY}"
            }
         ]
      }
   ```
   > Pay attention that we are going to `/v1/images/generations` endpoint in here.
3. Replace `${OPENAI_API_KEY}` with your OpenAI API Key

4. Open in browser [local dial chat](http://localhost:3000/marketplace) and test it:
    ```text
    I need 3 small red dots on the white background
    ```
   > Pay attention that Image Gen models are quite expensive!

<details><summary>Final result:</summary>

![](/tasks/t2_add_models/_screenshots/image_gen_model.png)

</details>

---

## 4. Add OpenAI TTS (Text-To-Speech) model:

1. Open the [models.json](/core/models.json) and add into `"models"` section:
   ```json
      "gpt-4o-mini-tts": {
         "displayName": "GPT 4o Mini TTS",
         "description": "Converts Text to Audio (speech)",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-4o-mini-tts/chat/completions",
         "iconUrl": "http://localhost:3001/gpt3.svg",
         "type": "chat"
      }
   ```
2. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
   {
      "upstreams": [
         {
            "endpoint": "https://api.openai.com/v1/audio/speech",
            "key": "${OPENAI_API_KEY}"
         }
      ]
   }
   ```
   > Pay attention that we are going to `/v1/audio/speech` endpoint in here.
3. Replace `${OPENAI_API_KEY}` with your OpenAI API Key

4. Open in browser [local dial chat](http://localhost:3000/marketplace) and test it:
    ```text
    Hello from DIAL Dev course!
    ```

<details><summary>Final result:</summary>

![](/tasks/t2_add_models/_screenshots/tts.png)

</details>

---

## 5. Add OpenAI STT (Speech-To-Text) model:

1. Open the [models.json](/core/models.json) and add into `"models"` section:
   ```json
      "gpt-4o-mini-transcribe": {
         "displayName": "GPT 4o Mini STT",
         "description": "Transcribes Audio to Text",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-4o-mini-transcribe/chat/completions",
         "iconUrl": "http://localhost:3001/gpt3.svg",
         "type": "chat",
         "inputAttachmentTypes": [
            "audio/mpeg"
         ]
      }
   ```
2. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
   {
      "gpt-4o-mini-transcribe": {
         "upstreams": [
            {
               "endpoint": "https://api.openai.com/v1/audio/transcriptions",
               "key": "${OPENAI_API_KEY}"
            }
         ]
      }
   }
   ```
   > Pay attention that we are going to `/v1/audio/transcriptions` endpoint in here.
3. Replace `${OPENAI_API_KEY}` with your OpenAI API Key

4. Open in browser [local dial chat](http://localhost:3000/marketplace) and test it with this [question.mp3](/tasks/t2_add_models/question.mp3) file

<details><summary>Final result:</summary>

![](/tasks/t2_add_models/_screenshots/stt.png)

</details>

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. Model ID mismatch between `models.json` key and endpoint URL

The key in the `"models"` object and the `<model-id>` segment in the `endpoint` URL must be identical:

```json
// WRONG — key is "gpt-5.2" but URL says "gpt5-2"
"gpt-5.2": {
  "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt5-2/chat/completions"
}

// CORRECT
"gpt-5.2": {
  "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-5.2/chat/completions"
}
```

Symptom: Core routes correctly, but the adapter cannot find the model and returns a 404 or 400.

---

### 2. Wrong upstream endpoint for the model type

Each OpenAI model category uses a different vendor URL. A TTS model pointing to the chat completions endpoint will get a 400 from OpenAI.

```json
// WRONG — TTS model pointing to LLM endpoint
"gpt-4o-mini-tts": {
  "upstreams": [{ "endpoint": "https://api.openai.com/v1/responses", "key": "sk-..." }]
}

// CORRECT
"gpt-4o-mini-tts": {
  "upstreams": [{ "endpoint": "https://api.openai.com/v1/audio/speech", "key": "sk-..." }]
}
```

---

### 3. Forgetting to add the adapter service to `docker-compose.yml`

If you add a model with `endpoint: http://adapter-dial-openai:5000/...` but the `adapter-dial-openai` service is not in your `docker-compose.yml`, Core will forward the request and immediately get a connection refused error.

Symptom: `502 Bad Gateway` or `upstream connect error` in Core logs.

Fix: Add the adapter service definition and run `docker compose stop && docker compose up -d --build`.

---

### 4. Not restarting Docker after adding a new adapter

Config-only changes (new model in `models.json`) are picked up by Core's hot-reload within ~3 seconds. But a new adapter is a new Docker container — it does not exist until you restart Compose.

| Change | Restart needed? |
|---|---|
| New model entry in `models.json` | No — hot-reload |
| Updated API key in `models-keys.json` | No — hot-reload |
| New adapter service in `docker-compose.yml` | **Yes** — `docker compose stop && docker compose up -d --build` |

---

### 5. Committing `models-keys.json` (or any keys file)

The file `core/models-keys.json` contains real API keys. It is listed in `.gitignore` for this reason. If you commit it accidentally, **rotate your API keys immediately** — assume the key is compromised the moment it hits a git remote.

---

### 6. `iconUrl` using `localhost` — works in Chat, fails in Docker-internal contexts

In this course, `iconUrl: "http://localhost:3001/gpt3.svg"` works because the Chat UI renders icons in the **browser**, which resolves `localhost` correctly. But if any server-side component tries to fetch that icon URL from inside a container, `localhost` resolves to the container itself — not your machine.

For production: use `http://themes:3001/gpt3.svg` (the Docker service name). In this course, `localhost:3001` is fine for the Chat browser client.

---

### 7. Missing `inputAttachmentTypes` for multimodal models

If you omit `inputAttachmentTypes` from a model that accepts file input (STT, vision, document), the Chat UI will not display the attachment button, and Core will reject any requests with attachments.

```json
// STT model WITHOUT inputAttachmentTypes — attachment button never appears
"gpt-4o-mini-transcribe": {
  "type": "chat",
  "endpoint": "..."
}

// CORRECT — Chat now shows an audio attachment button
"gpt-4o-mini-transcribe": {
  "type": "chat",
  "endpoint": "...",
  "inputAttachmentTypes": ["audio/mpeg"]
}
```

---

### 8. Expecting `type: "chat"` to drive vendor API selection

`"type": "chat"` vs `"type": "embedding"` in `models.json` tells Core which **DIAL API schema** to apply (`/chat/completions` vs `/embeddings`). It does **not** tell the adapter which vendor endpoint to call — that is determined by the `upstreams[].endpoint` in `keys.json`.

An image generation model, a TTS model, and a regular LLM all use `"type": "chat"` in DIAL. The difference is entirely in the upstream endpoint you configure in `models-keys.json`.

</details>