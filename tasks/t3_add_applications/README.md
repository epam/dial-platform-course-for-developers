# Add Applications to DIAL

In this task we will build and register two custom applications in DIAL using the DIAL SDK.

---

## 1. Add Echo Application

> The Echo app is already provided at [echo/echo_app.py](echo/echo_app.py). It demonstrates the minimal DIAL SDK
> pattern — no external model calls, just echoes the user's message back.

1. Open [applications.json](/core/applications.json) and add to the `"applications"` section:
   ```json
     "echo": {
       "displayName": "My Echo App",
       "description": "Simple application that repeats user's message",
       "endpoint": "http://host.docker.internal:5022/openai/deployments/echo/chat/completions"
     }
   ```
2. Run [echo/echo_app.py](echo/echo_app.py)
3. Open [DIAL Chat](http://localhost:3000/marketplace) and test **My Echo App**

> No Docker restart needed — DIAL Core hot-reloads `applications.json` every 5 seconds.
> The Python app runs on your machine; `host.docker.internal` lets Docker containers reach it.

<details><summary>Final result:</summary>

![Echo test](/tasks/t3_add_applications/_screenshots/echo.png)

</details>

---

## 2. Add Essay Assistant (GPT)

**DIAL allows you to call other models from within your application. `EssayAssistantApplication` uses DIAL Client to
forward requests to an LLM deployed in DIAL Core — your app acts as a middleware.**

1. Open [essay/essay_assistant.py](essay/essay_assistant.py) and implement the **TODO blocks**.

2. Open [essay/app_gpt.py](essay/app_gpt.py) and implement the **TODO**.

3. Open [applications.json](/core/applications.json) and add to the `"applications"` section:
   ```json
     "essay-assistant-gpt": {
       "displayName": "Essay Assistant",
       "description": "Essay Assistant. Always answers with essay.",
       "endpoint": "http://host.docker.internal:5025/openai/deployments/essay-assistant-gpt/chat/completions"
     }
   ```
4. Run [essay/app_gpt.py](essay/app_gpt.py)
5. Open [DIAL Chat](http://localhost:3000/marketplace) and test **Essay Assistant**
6. You can also test it directly via DIAL Core:
   ```bash
   curl --location 'http://localhost:8080/openai/deployments/essay-assistant-gpt/chat/completions' \
   --header 'Api-Key: dial_api_key' \
   --header 'Content-Type: application/json' \
   --data '{
       "stream": false,
       "messages": [
           {"role": "user", "content": "About microwave"}
       ]
   }'
   ```

<details><summary>Final result:</summary>

![Essay Assistant test](/tasks/t3_add_applications/_screenshots/essay-result-gpt.png)

</details>

---

## 3. Add Essay Assistant (Sonnet)

**DIAL is vendor-agnostic — switching from GPT to Claude Sonnet requires zero changes to the application logic
in `essay_assistant.py`. Only the model name and port differ.**

1. Open [essay/app_sonnet.py](essay/app_sonnet.py) and implement the **TODO**.

2. Open [applications.json](/core/applications.json) and add to the `"applications"` section:
   ```json
     "essay-assistant-sonnet": {
       "displayName": "Essay Assistant",
       "description": "Essay Assistant. Always answers with essay.",
       "endpoint": "http://host.docker.internal:5026/openai/deployments/essay-assistant-sonnet/chat/completions"
     }
   ```
3. Run [essay/app_sonnet.py](essay/app_sonnet.py)
4. Open [DIAL Chat](http://localhost:3000/marketplace) and test **Essay Assistant** (Sonnet version)

---

## 4. Merge Essay Assistants in Marketplace

**When two applications share the same `displayName` but have different `displayVersion` values, DIAL Chat merges them
into a single marketplace card with a version selector dropdown.**

1. Open [applications.json](/core/applications.json) and add `displayVersion` to both essay entries:
   ```json
     "essay-assistant-gpt": {
       "displayName": "Essay Assistant",
       "displayVersion": "gpt-5.2",
       "description": "Essay Assistant. Always answers with essay.",
       "endpoint": "http://host.docker.internal:5025/openai/deployments/essay-assistant-gpt/chat/completions"
     },
     "essay-assistant-sonnet": {
       "displayName": "Essay Assistant",
       "displayVersion": "sonnet-4.6",
       "description": "Essay Assistant. Always answers with essay.",
       "endpoint": "http://host.docker.internal:5026/openai/deployments/essay-assistant-sonnet/chat/completions"
     }
   ```
2. Open [DIAL Chat](http://localhost:3000/marketplace) — the two Essay Assistant cards merge into one with a version
   dropdown

<details><summary>Final result:</summary>

![Essay Assistant merged in marketplace](/tasks/t3_add_applications/_screenshots/essay-merged-marketplace.png)
![Essay Assistant version dropdown](/tasks/t3_add_applications/_screenshots/essay-merged-chat.png)

</details>

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. Python app not running

DIAL Core routes requests to `host.docker.internal:PORT`. If nothing is listening on that port, the request fails
immediately.

Symptom: error in Chat when sending a message to the app.

Fix: make sure the Python file is running before testing in Chat.

---

### 2. Port mismatch between Python app and `applications.json`

The port in `uvicorn.run(app, port=PORT)` must exactly match the port in the `endpoint` URL in `applications.json`.

| App             | Port |
|-----------------|------|
| `echo_app.py`   | 5022 |
| `app_gpt.py`    | 5025 |
| `app_sonnet.py` | 5026 |

---

### 3. Deployment name mismatch

Three places must use the **exact same** deployment name:

```
applications.json key          →  "essay-assistant-gpt"
add_chat_completion(name=...)  →  "essay-assistant-gpt"
endpoint URL segment           →  .../deployments/essay-assistant-gpt/...
```

A mismatch at any one of these causes a 404 from the app or a routing error from Core.

---

### 4. Wrong `base_url` in `AsyncDial`

Local Python apps run **outside Docker**, so they must reach Core via `localhost`, not the Docker service name.

```python
# WRONG — only works inside Docker containers
AsyncDial(base_url="http://core:8080", ...)

# CORRECT — from a local Python process
AsyncDial(base_url="http://localhost:8080", ...)
```

---

### 5. Forgetting to guard against `None` content in streaming chunks

Not every chunk contains content. Always check before appending:

```python
# WRONG — crashes when delta.content is None
choice.append_content(chunk.choices[0].delta.content)

# CORRECT
delta = chunk.choices[0].delta
if delta and delta.content:
    choice.append_content(delta.content)
```

</details>
