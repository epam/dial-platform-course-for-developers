# Final Task: Multi-Tool Agent

In this final task you will build a production-style DIAL agent equipped with three tools: an essay generator, an image
generator, and a microwave manual RAG assistant. The agent follows the same recursive-loop-plus-state pattern from t4,
now generalised to any number of tools via a tool registry. You will wire together streaming, parallel tool execution,
DIAL's unified API, and multi-turn state persistence — all in one application.

---

## File Map

| File                                                                                                    | Role                                                                      |
|---------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| [app/agent.py](app/agent.py)                                                                          | Core agentic loop — streaming, tool dispatch, recursion, state            |
| [app/tools/base.py](app/tools/base.py)                                                                | `BaseTool` abstract class — execute wrapper with error handling           |
| [app/tools/deployment/base.py](app/tools/deployment/base.py)                                          | `DeploymentTool` — calls any DIAL deployment as a tool                    |
| [app/tools/deployment/essay_generation_tool.py](app/tools/deployment/essay_generation_tool.py)        | Essay tool definition                                                     |
| [app/tools/deployment/image_generation_tool.py](app/tools/deployment/image_generation_tool.py)        | Image generation tool + inline image display                              |
| [app/tools/deployment/microwave_rag_tool.py](app/tools/deployment/microwave_rag_tool.py)              | Microwave RAG tool definition                                             |
| [app/app.py](app/app.py)                                                                              | DIAL app wiring                                                           |
| [core/applications.json](../../core/applications.json)                                                | Application registration                                                  |
| [app/utils.py](app/utils.py)                                                                          | **Provided — no changes.** `StageProcessor` and `unpack_messages` helpers |
| [app/tools/models.py](app/tools/models.py)                                                            | **Provided — no changes.** `ToolCallParams` dataclass                     |

---

## Steps

### 1. Read the provided helpers (no TODO)

Before writing any code, read these two files — they are provided and require no changes.

- [app/utils.py](app/utils.py) — identical to t4: `StageProcessor.open_stage` / `close_stage_safely` for stage
  lifecycle, and `unpack_messages` which reconstructs the full message sequence (including tool exchanges saved in
  state) before each LLM call.
- [app/tools/models.py](app/tools/models.py) — defines `ToolCallParams`, the dataclass passed into every tool's
  `execute()` method. It bundles the raw `ToolCall`, an open `Stage`, the `Choice`, and the `api_key`.

---

### 2. Implement the TODO in `app/agent.py`

[app/agent.py](app/agent.py) is the heart of the agent. It owns `handle_request()`, which calls the LLM, processes the
streamed response, dispatches tools, and recurses until the model produces a final answer.

**Streaming and tool call assembly**

The LLM streams its response in delta chunks. Each chunk may carry `delta.content` (plain text) or `delta.tool_calls`
(tool call fragments). Tool calls arrive in pieces: the first chunk for a given index carries the call's `.id` and
`.function.name`; subsequent chunks carry more `.function.arguments`. You must accumulate both content and arguments
correctly — the `tool_call_index_map` (keyed by index) is the right structure for this.

**After the stream ends**

Build an `assistant_message` from the accumulated content and completed tool call objects. Then branch:

- **Tool calls present** — dispatch every tool concurrently with `asyncio.gather`. After all results are back, append
  the assistant message and tool result messages to `self.state[_TOOL_CALL_HISTORY_KEY]`, then call `handle_request`
  again. On this recursive call, `_prepare_messages` will inject the saved history via `unpack_messages`, so the LLM
  receives the full context and can produce its final answer.
- **No tool calls** — the model produced the final answer. Call `choice.set_state(self.state)` to persist the tool
  call history for the next turn, then return.

---

### 3. Implement the TODO in `app/tools/base.py`

[app/tools/base.py](app/tools/base.py) defines `BaseTool`, the abstract base class for all tools.

`execute()` is the **public entry point** called by the agent. It must:

1. Construct a base `Message` with `role=Role.TOOL`, the tool name, and the `tool_call_id` from `ToolCallParams`.
2. Call `self._execute(tool_call_params)` and populate `msg.content` with the result (if the result is already a
   `Message`, use it directly).
3. Catch any exception, set `msg.content` to a descriptive error string, and append the error to the stage — so the
   agent can continue rather than crash.

Individual tools only need to implement `_execute()`. Error handling lives here, once.

---

### 4. Implement the TODO in `app/tools/deployment/base.py`

[app/tools/deployment/base.py](app/tools/deployment/base.py) is the most conceptually important file.

> **Key concept — DIAL's unified API**
>
> Every model and every application registered in DIAL Core is reachable via the same OpenAI-compatible endpoint:
>
> ```
> POST /openai/deployments/{deployment_name}/chat/completions
> ```
>
> Whether `deployment_name` is a raw LLM (`gpt-5.2`), an image model (`gpt-image-1.5`), or a custom application
> (`essay-assistant-gpt`, `microwave-rag`) — the call is identical. `AsyncDial` (or any OpenAI SDK client pointed at
> DIAL Core) works transparently for all of them. This is why `DeploymentTool` can turn any registered deployment into
> a tool without any adapter code.

`_execute()` must:

1. Create an `AsyncDial` client pointed at `self.endpoint` with the request's `api_key`.
2. Parse the tool call arguments. Extract `"prompt"` (used as the user message content); the remaining fields are
   forwarded as `extra_body={"custom_fields": {"configuration": {...}}}` — this is how deployment-specific parameters
   (e.g. image `size`) reach the downstream application.
3. Stream the response. For each chunk: accumulate `delta.content` into a string and append it to the stage; collect
   any `delta.custom_content.attachments` and mirror them to the stage via `stage.add_attachment`.
4. Return a `Message` with `role=Role.TOOL`, the accumulated content, the collected `custom_content` (attachments),
   and the `tool_call_id`.

---

### 5. Implement the TODOs in the three tool files

Each tool is a subclass of `DeploymentTool` and only needs to declare four properties. The base class handles all
execution.

**[app/tools/deployment/essay_generation_tool.py](app/tools/deployment/essay_generation_tool.py)**

- `deployment_name` → `"essay-assistant-gpt"` (the custom application registered in `core/applications.json`)
- `name` → identifier the LLM uses when it wants to call this tool
- `description` → plain-English explanation of what this tool does; the LLM reads this to decide when to use it
- `parameters` → JSON Schema object describing the tool's inputs (at minimum a `"prompt"` string)

**[app/tools/deployment/image_generation_tool.py](app/tools/deployment/image_generation_tool.py)**

- `deployment_name` → `"gpt-image-1.5"` — this is a **model**, not an application, which shows that the same
  `DeploymentTool` pattern works for both
- `description` — be precise: describe available sizes, when to use this tool, and what is out of scope
- `parameters` — include both `"prompt"` and `"size"` (with an enum of supported resolutions); `"size"` is optional

This tool also overrides `_execute()`: after calling `super()._execute()`, it extracts image URLs from the returned
attachments and appends a markdown image reference directly to `choice`. This makes the image appear inline in the
chat message. Without this override the image would only be accessible as an attachment.

**[app/tools/deployment/microwave_rag_tool.py](app/tools/deployment/microwave_rag_tool.py)**

- `deployment_name` → `"microwave-rag"` (the RAG application from t8)
- `parameters` — a single `"prompt"` string describing what to search for in the microwave manual

---

### 6. Implement the TODO in `app/app.py`

[app/app.py](app/app.py) wires everything together:

- Create a `DIALApp` instance.
- Register `FinalTaskAgentApplication()` under deployment name `"final-task-agent"` using
  `app.add_chat_completion("final-task-agent", FinalTaskAgentApplication())`.
- Start with `uvicorn.run(app, port=5032, host="0.0.0.0")`.

---

### 7. Register in [core/applications.json](/core/applications.json)

Add a configuration for this agent to [core/applications.json](/core/applications.json):

### 8. Run and test

> **Note:** Before running this agent, make sure the dependent applications are already running:
> - [tasks/t3_add_applications/essay/app_gpt.py](../t3_add_applications/essay/app_gpt.py) — the essay assistant (port 5025)
> - [tasks/t8_rag/app/app.py](../t8_rag/app/app.py) — the microwave RAG app (port 5030)
>
> If either is not running, DIAL Core will return a **502 Bad Gateway** when the agent tries to call that tool.

1. Run [app/app.py](app/app.py).

2. Open [DIAL Chat](http://localhost:3000/marketplace) and find **Final task Agent**. Try each tool:
    - `"Write an essay about the history of artificial intelligence"` — triggers `essay_generation_tool`
    - `"Generate a picture with 3 small red dots on a white background"` — triggers `image_generation_tool`
    - `"How do I set the clock on my microwave?"` — triggers `microwave_rag_tool`
    - `"Write an essay about microwaves AND generate an image of a microwave"` — triggers both tools in parallel

3. Verify that each response shows a collapsible stage named after the tool, the arguments used, and the tool output.

4. You can also test directly via DIAL Core:

```bash
curl --location 'http://localhost:8080/openai/deployments/final-task-agent/chat/completions' \
  --header 'Api-Key: dial_api_key' \
  --header 'Content-Type: application/json' \
  --data '{
    "stream": false,
    "messages": [{"role": "user", "content": "Write a short essay about space exploration"}]
  }'
```

In the response look for `"custom_content": {"stages": [...], "state": {"tool_call_history": [...]}}` inside the
assistant message.
