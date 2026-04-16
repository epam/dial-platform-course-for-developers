# Embeddings and Frameworks

In this task you will build a **RAG (Retrieval-Augmented Generation) application** that answers questions about a
microwave oven manual. The application uses LangChain's Azure OpenAI integration to call DIAL's embedding model and LLM
— demonstrating that any OpenAI-compatible framework works with DIAL without modification.

---

## Microwave RAG Application

The application embeds the user's query, finds the most relevant passages from the microwave manual, and passes them as
context to the LLM for a grounded answer.

### Application flow

```
User message
      │
      ▼
[1] Embed query → similarity search in FAISS vectorstore     ← TODO 3
    (text-embedding-3-small via AzureOpenAIEmbeddings)
[2] Show retrieved context in a RAG Search stage
      │
      ▼
[3] Build RAG prompt: SystemMessage + HumanMessage(context + query)  ← TODO 4
[4] Stream answer from gpt-5.2 via AzureChatOpenAI                   ← TODO 4
      │
      ▼
Assistant reply
```

---

## Steps

1. **Read [rag_app.py](rag_app.py) in full first**

   Key methods and their roles:

   | Method | Description |
      |--------|-------------|
   | `__init__` | Stores clients; calls `_setup_vectorstore` |
   | `_setup_vectorstore` | Loads the pre-built FAISS index from `microwave_faiss_index/` |
   | `_create_new_index` | Builds a new FAISS index from `microwave_manual.txt` (only if index is missing) |
   | `retrieve_context` | Embeds the query, searches FAISS, formats and returns the context string |
   | `chat_completion` | Main handler — retrieves context, builds messages, streams LLM response |

   > The `microwave_faiss_index/` directory is already committed. `_setup_vectorstore` will load it on startup without
   > making any embedding API calls.

2. **Implement TODO 1 — `AzureOpenAIEmbeddings`** (at the bottom of `rag_app.py`, inside `MicrowaveRagApp(...)`)

   Create the embedding client pointing at DIAL's `text-embedding-3-small` deployment:

   ```python
   AzureOpenAIEmbeddings(
       deployment='text-embedding-3-small',   # DIAL deployment name
       dimensions=784,                         # must match the pre-built index
       azure_endpoint=_DIAL_URL,
       api_key=SecretStr(_API_KEY),
   )
   ```

   > `dimensions=784` must match the value used when the FAISS index was built. Changing it would corrupt similarity
   > search and force a full index rebuild.

3. **Implement TODO 2 — `AzureChatOpenAI`** (at the bottom of `rag_app.py`, inside `MicrowaveRagApp(...)`)

   Create the LLM client:

   ```python
   AzureChatOpenAI(
       azure_deployment='gpt-5.2',
       azure_endpoint=_DIAL_URL,
       api_key=SecretStr(_API_KEY),
       api_version="2025-01-01-preview",
   )
   ```

4. **Implement TODO 3 — body of `retrieve_context`** in [rag_app.py](rag_app.py)

5. **Implement TODO 4 — body of `chat_completion`** in [rag_app.py](rag_app.py)

6. **Open [core/applications.json](/core/applications.json) and add this app config**:

   ```json
   "microwave-rag": {
     "displayName": "Microwave RAG",
     "description": "RAG assistant that can answer questions about microwave usage.",
     "endpoint": "http://host.docker.internal:5030/openai/deployments/microwave-rag/chat/completions"
   }
   ```

7. **Open [core/models.json](/core/models.json) and add this model config**:
   ```json
       "text-embedding-3-small": {
         "type": "embedding",
         "overrideName": "text-embedding-3-small",
         "endpoint": "http://adapter-dial-openai:5000/openai/deployments/text-embedding-3-small/embeddings"
       }
   ```

8. **Open [core/models-keys.json](/core/models-keys.json) and add this model config**:
   ```json
       "text-embedding-3-small": {
         "upstreams": [
           {
             "endpoint": "https://api.openai.com/v1/embeddings",
             "key": "${OPENAI_API_KEY}"
           }
         ]
       }
   ```
   Replace `${OPENAI_API_KEY}` with your OpenAI API Key
   **Pay attention that we are using `/v1/embeddings` endpoint**

9. **Run [rag_app.py](rag_app.py)**

   On startup you should see:
   ```
   🔄 Initializing Microwave Manual RAG System...
   ✅ Loaded existing FAISS index
   ```

   If you see `📖 Loading text document...` instead, the FAISS index is being rebuilt from scratch — this is normal
   only if `microwave_faiss_index/` was deleted.

10. **Open [DIAL Chat](http://localhost:3000/marketplace) and test Microwave RAG**
    Expand the `RAG Search` stage to inspect the retrieved context for each query. Try:

- `What safety precautions should be taken to avoid exposure to excessive microwave energy?`
- `What are the steps to set the clock time on the DW 395 HCG microwave oven?`
- `What materials are safe to use in this microwave during both microwave and grill cooking modes?`
- `What is the ECO function on this microwave and how do you activate it?`
- `How should you clean the glass tray of the microwave oven?`
- `How does the multi-stage cooking feature work, and what types of cooking programs cannot be included in it?`

Then test out-of-scope behaviour — the model should refuse to answer:
- `What is the capital of France?`


11. **Test directly via DIAL Core**:

   ```bash
   curl --location 'http://localhost:8080/openai/deployments/microwave-rag/chat/completions' \
     --header 'Api-Key: dial_api_key' \
     --header 'Content-Type: application/json' \
     --data '{
       "stream": false,
       "messages": [{"role": "user", "content": "How should you clean the glass tray?"}]
     }'
   ```

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. `dimensions` mismatch corrupts similarity search

The pre-built FAISS index was created with `dimensions=784`. Using a different value gives embedding vectors of a
different size — FAISS will either crash or return meaningless results.

If you need to change dimensions: delete the `microwave_faiss_index/` folder, update `AzureOpenAIEmbeddings`, then
restart the app to trigger a fresh rebuild.

---

### 2. `score_threshold` too high — no context returned

The default `score_threshold=0.3` is intentionally permissive. Raising it to `0.7` or higher may filter out all
results for legitimate questions, causing the model to respond "I cannot answer this question" even when relevant text
exists in the manual.

Lower the threshold if retrieval seems too strict; raise it if irrelevant passages are leaking into the context.

---

### 3. `api_version` is required by LangChain but not DIAL SDK

`AzureChatOpenAI` and `AzureOpenAIEmbeddings` will raise a validation error if `api_version` is omitted.
`AsyncDial` (used in previous tasks) handles versioning internally and does not require it.

---

### 4. Do not delete the pre-built FAISS index

`microwave_faiss_index/` is already committed to the repository. Deleting it triggers a full rebuild inside
`_create_new_index`, which makes many embedding API calls (one per document chunk) and can take several seconds.

---

### 5. Port mismatch

| App          | Port |
|--------------|------|
| `rag_app.py` | 5030 |

The port in `uvicorn.run(app, port=5030)` must match the port in the `endpoint` URL in `applications.json`.

</details>
