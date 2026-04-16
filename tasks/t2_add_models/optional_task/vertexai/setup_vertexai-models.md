# Set up Google VertexAI Models

You can use different models from [Google VertexAI](https://console.cloud.google.com/vertex-ai/publishers/google/model-garden)

Documentation for [adapter-dial-vertexai](https://github.com/epam/ai-dial-adapter-vertexai)

1. Create API Key in [Google AI Studio](https://aistudio.google.com/app/api-keys)
2. Open the core [models.json](/core/models.json) and add such config to `models`:
   ```json
       "gemini-3.1-flash-lite-preview": {
         "displayName": "Gemini 3.1 Flash Lite",
         "description": "Gemini 3.1 Flash Lite model",
         "endpoint": "http://adapter-dial-vertexai:5000/openai/deployments/gemini-3.1-flash-lite-preview/chat/completions",
         "iconUrl": "http://localhost:3001/Gemini-Pro-Vision.svg",
         "type": "chat"
       }
   ```
3. 3. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
      "gemini-3.1-flash-lite-preview": {
         "upstreams": [
            {
               "key": "${API_KEY}"
            }
         ]
      }
   ```
   Replace `${API_KEY}` with generated API key
4. Open [docker-compose.yml](/docker-compose.yml) and add such service:
    ```yaml
      adapter-dial-vertexai:
        image: epam/ai-dial-adapter-vertexai:latest
        #platform: linux/amd64
        environment:
          DIAL_URL: "http://core:8080"
          LOG_LEVEL: "DEBUG"
    ```
5. Start VertexAI adapter service
6. Test it in DIAL Chat

