# Set up Claude and Bedrock models

Documentation for [adapter-dial-bedrock](https://github.com/epam/ai-dial-adapter-bedrock)

## Anthropic API

1. Open the [models.json](/core/models.json)
2. Add such config to `models`:
   ```json
      "claude-sonnet-4-6": {
         "displayName": "Claude Sonnet 4.6",
         "description": "Claude Sonnet 4.6 model",
         "endpoint": "http://adapter-dial-bedrock:5000/openai/deployments/claude-sonnet-4-6/chat/completions",
         "icon_url": "http://localhost:3001/anthropic.svg",
         "type": "chat"
      }
   ```
3. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
      "claude-sonnet-4-6": {
         "upstreams": [
            {
               "key": "${ANTHROPIC_API_KEY}",
               "extraData": {
                  "compatible_model_id": "anthropic.claude-sonnet-4-6"
               }
            }
         ]
      }
   ```
   Replace `${ANTHROPIC_API_KEY}` with your [Anthropic API Key](https://console.anthropic.com/settings/keys)
4. Open root [docker-compose.yml](/docker-compose.yml) and add such service:
    ```yaml
      adapter-dial-bedrock:
        image: epam/ai-dial-adapter-bedrock:latest
        #platform: linux/amd64
        environment:
          DIAL_URL: "http://core:8080"
          LOG_LEVEL: "INFO"
    ```
5. Start service
6. Test it

---

## Bedrock

Add Claude model from [AWS Bedrock](https://aws.amazon.com/bedrock/). You need to generate [AWS Access Key in IAM](https://repost.aws/knowledge-center/create-access-key)

1. Open the [models.json](/core/models.json)
2. Add such config to `models`:
   ```json
      "claude-haiku-4-5": {
         "displayName": "Claude Haiku 4.5",
         "description": "Claude Haiku 4.5 Bedrock model",
         "endpoint": "http://adapter-dial-bedrock:5000/openai/deployments/eu.anthropic.claude-haiku-4-5-20251001-v1:0/chat/completions",
         "icon_url": "http://localhost:3001/anthropic.svg",
         "type": "chat"
      }
   ```
   Pay attention that we need to provide region before model name, in the sample I'm accession model in EU `eu.` region `eu.anthropic.claude-haiku-4-5-20251001-v1:0`.
3. Open the [models-keys.json](/core/models-keys.json) and add into `"models"` section:
   ```json
       "claude-haiku-4-5": {
         "upstreams": [
           {
             "extraData": {
               "region": "eu-central-1",
               "aws_access_key_id": "${AWS_ACCESS_KEY_ID_STARTS_WITH_AKIA}",
               "aws_secret_access_key": "${AWS_SECRET_ACCESS_KEY}"
             }
           }
         ]
       }
   ```
   Replace `${AWS_ACCESS_KEY_ID_STARTS_WITH_AKIA}` and `${AWS_SECRET_ACCESS_KEY}` with AWS Keys
4. Restart DIAL Core service
5. Test it