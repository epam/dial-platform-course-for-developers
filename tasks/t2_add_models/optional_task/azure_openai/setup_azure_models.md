# Set up Azure OpenAI Models

You can use different models from [Azure OpenAI](https://azure.microsoft.com/en-us/products/ai-foundry/models/openai)

Documentation for [adapter-dial-openai](https://github.com/epam/ai-dial-adapter-openai)

In this section we will use [OpenAI Responses API](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/how-to/responses?tabs=python-key) with DIAL:

1. Deploy in Azure `gpt-5.4-nano` model in [AI Azure OpenAI](https://ai.azure.com/resource/models).
2. Open the core [models.json](/core/models.json) and add such config to `models`:
   ```json
       "gpt-5.4-nano": {
         "displayName": "GPT 5.4 nano",
         "description": "GPT-5.4 nano is designed for tasks where speed and cost matter most like classification, data extraction, ranking, and sub-agents",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/gpt-5.4-nano/chat/completions",
         "iconUrl": "http://localhost:3001/gpt3.svg",
         "type": "chat"
       }
   ```
   Pay attention that to work with models in Azure OpenAI you need to add `ai-dial-adapter-openai`
3. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
       "gpt-5.4-nano": {
         "upstreams": [
           {
             "endpoint": "https://${AZURE_OPENAI_SERVICE_NAME}.cognitiveservices.azure.com/openai/v1/responses",
             "key": "${API_KEY}"
           }
         ]
       }
   ```
   - Replace `${AZURE_OPENAI_SERVICE_NAME}` with proper service name, sample:
     - Target URI: https://khahs-mhullmkq-eastus2.cognitiveservices.azure.com/openai/responses?api-version=2025-04-01-preview
     - `${AZURE_OPENAI_SERVICE_NAME}`: `khahs-mhullmkq-eastus2`
     - Final result: `https://khahs-mhullmkq-eastus2.cognitiveservices.azure.com/openai/v1/responses`
   - Replace `${API_KEY}` with endpoint in Azure and generated API key
4. Restart DIAL Core service (or wait reload time till DIAL Core fetches updates from core config.json) and test it