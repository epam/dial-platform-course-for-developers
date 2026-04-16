# Start DIAL Platform main services

## 1. Add DIAL Core Service:

Open [docker-compose.yml](/docker-compose.yml) and add:
1. Redis service:
   ```yaml
     redis:
       image: redis:latest
       # platform: linux/amd64
       restart: always
       ports:
         - "6379:6379"
       command: >
         redis-server
         --maxmemory 2000mb
         --maxmemory-policy volatile-lfu
         --save ""
         --appendonly no
         --loglevel warning
       mem_limit: 2200M
   ```

2. [DIAL Core service](https://hub.docker.com/r/epam/ai-dial-core/tags):
   ```yaml
     core:
       user: ${UID:-root}
       ports:
         - "8080:8080"
       image: epam/ai-dial-core:latest
       #platform: linux/amd64
       environment:
         'AIDIAL_SETTINGS': '/opt/settings/settings.json'
         'JAVA_OPTS': '-Dgflog.config=/opt/settings/gflog.xml'
         'LOG_DIR': '/app/log'
         'STORAGE_DIR': '/app/data'
         'aidial.config.files': '["/opt/config/models.json", "/opt/config/applications.json", "/opt/config/models-keys.json", "/opt/config/api-keys-and-roles.json"]'
         'aidial.storage.overrides': '{ "jclouds.filesystem.basedir": "data" }'
         'aidial.redis.singleServerConfig.address': 'redis://redis:6379'
         'aidial.config.reload': 5000
       depends_on:
         - redis
       volumes:
         - ./settings:/opt/settings
         - ${DIAL_DIR:-.}/core:/opt/config
         - ${DIAL_DIR:-.}/core-logs/:/app/log
         - ${DIAL_DIR:-.}/core-data/:/app/data
   ```

> Please take a look at `'aidial.config.files'` parameter, it applies array of core configuration files, for now we have: 
> - [models.json](/core/models.json) with public version of models configuration. 
> - [applications.json](/core/applications.json) with configurations for applications.
> - [api-keys-and-roles.json](/core/api-keys-and-roles.json) with DIAL API keys and Roles configuration, in this course we won't practice with them and will work only with default role and general dial_api_key.
> - `models-keys.json` (will add later) where we will persist [upstreams](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/models.md#modelsmodel_nameupstreams) configurations fro models.

> Please take a look at `'aidial.config.reload'`, in here you can configure reload time in milliseconds for DIAL Core configuration. 
> It is set as `5000` milliseconds == 5 seconds, so every 5 seconds DIAL Core will fetch configurations defined in `'aidial.config.files'` parameter.

**Important: all DIAL Core configurations can be persisted in one single file, like `config.json` but we split them for more comfortable management later**

## 2. DIAL Chat UI Service with Themes:

1. [DIAL Chat Themes](https://hub.docker.com/r/epam/ai-dial-chat-themes/tags):
   ```yaml
     themes:
       image: epam/ai-dial-chat-themes:latest
       #platform: linux/amd64
       ports:
         - "3001:8080"
   ```
2. [DIAL Chat UI Service](https://hub.docker.com/r/epam/ai-dial-chat/tags):
   ```yaml
     chat:
       ports:
         - "3000:3000"
       image: epam/ai-dial-chat:latest
       #platform: linux/amd64
       depends_on:
         - themes
         - core
       environment:
         NEXTAUTH_SECRET: "secret"
         THEMES_CONFIG_HOST: "http://themes:8080"
         DIAL_API_HOST: "http://core:8080"
         DIAL_API_KEY: "dial_api_key"
         ENABLED_FEATURES: "conversations-section,prompts-section,top-settings,top-clear-conversation,top-chat-info,top-chat-model-settings,empty-chat-settings,header,footer,request-api-key,report-an-issue,likes,conversations-sharing,prompts-sharing,input-files,attachments-manager,conversations-publishing,prompts-publishing,custom-logo,input-links,custom-applications,message-templates,marketplace,code-apps"
         KEEP_ALIVE_TIMEOUT: ${CHAT_KEEP_ALIVE_TIMEOUT:-20000}
   ```

## 4. Create `models-keys.json` file to hide API keys:

Later on we will add models configurations in the [models.json](/core/models.json), and we will need to provide URL and API Key to access a model.
In DIAL, we usually have 2 files with configurations:
- Public: [models.json](/core/models.json), in here we provide models configurations
- Private: `models-keys.json` where we provide [upstreams](https://github.com/epam/ai-dial-core/blob/development/docs/dynamic-settings/models.md#modelsmodel_nameupstreams) configurations for models with URLs and API keys

1. **Create in [core folder](/core) `models-keys.json` file. We will save your keys in here, and it is added to [.gitignore](/.gitignore) and will be ignored by git**
2. Add to `models-keys.json` created file:
    ```json
    {
      "models": {}
    }
    ```

## 3. For Mac users:

Uncomment `#platform: linux/amd64` -> `platform: linux/amd64`

## 4. Run [docker-compose.yml](/docker-compose.yml)

```bash
docker compose up -d
```

## 5. Open Chat UI in browser:

Open [Open Chat UI in browser](http://localhost:3000/marketplace)

## Final result:

You will get empty marketplace, but don't worry, in the next tasks we will add models and applications
![](/tasks/t1_start_platform/_screenshots/marketplace.png)

---

## 🛠️ Troubleshooting

If your Core service is not started, and you see in logs of Core service:
- `File not found: /opt/config/models-keys.json` it means that you forgot to add `models-keys.json` file to [core folder](/core), add it please
- `No content to map due to end-of-input` it means that you need to add `{"models": {}}` to `models-keys.json` file that core will be able to parse it successfully.