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

Open [app/agent.py](app/agent.py) and implement the **TODO blocks** in `handle_request()`:
- **TODO 1** — process each streaming delta: accumulate text content and assemble the `tool_call_index_map`
- **TODO 2a / 2b** — after the stream ends: dispatch tools or finalize with `choice.set_state()`

---

### 3. Implement the TODO in `app/tools/base.py`

Open [app/tools/base.py](app/tools/base.py) and implement the **TODO** in `execute()`.

---

### 4. Implement the TODO in `app/tools/deployment/base.py`

Open [app/tools/deployment/base.py](app/tools/deployment/base.py) and implement the **TODO** in `_execute()`.

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

---

### 5. Implement the TODOs in the three tool files

Each tool subclass only needs to declare four properties — the base class handles all execution.

- Open [app/tools/deployment/essay_generation_tool.py](app/tools/deployment/essay_generation_tool.py) and implement the **4 property TODOs**
- Open [app/tools/deployment/image_generation_tool.py](app/tools/deployment/image_generation_tool.py) and implement the **4 property TODOs** and the **`_execute()` override TODO**
- Open [app/tools/deployment/microwave_rag_tool.py](app/tools/deployment/microwave_rag_tool.py) and implement the **4 property TODOs**

---

### 6. Implement the TODO in `app/app.py`

Open [app/app.py](app/app.py) and implement the **TODO blocks** — wire up `FinalTaskAgentApplication` and start uvicorn.

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

