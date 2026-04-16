# Stages and State

In this task you will learn two DIAL SDK primitives that extend the standard chat response with **Stage** and **State**

---

## Task 1: Poem Assistant — Working with Stages

A stage is a collapsible panel in DIAL Chat. Its lifecycle is:

```
choice.create_stage(name) → .open() → .append_content(...) → .close()
```

You must always close a stage — even when an error occurs — otherwise the response will hang.

---

### Steps

1. Open [t1_simple/poem_assistant.py](t1_simple/poem_assistant.py) and implement the **two TODO blocks**.

2. Open [core/applications.json](/core/applications.json) and confirm the following entry is present in the
   `"applications"` section (add it if missing):
   ```json
   "poem-assistant": {
     "displayName": "Poem Assistant",
     "description": "Poem Assistant. Always answers with poem.",
     "endpoint": "http://host.docker.internal:5027/openai/deployments/poem-assistant/chat/completions"
   }
   ```

3. Run [t1_simple/poem_assistant.py](t1_simple/poem_assistant.py)

4. Open [DIAL Chat](http://localhost:3000/marketplace) and test **Poem Assistant** — send any message and verify that
   two stages appear below the poem: **"Greeting Stage"** and **"Usage: gpt-5.2"**

5. You can also test directly via DIAL Core:
   ```bash
   curl --location 'http://localhost:8080/openai/deployments/poem-assistant/chat/completions' \
     --header 'Api-Key: dial_api_key' \
     --header 'Content-Type: application/json' \
     --data '{
       "stream": false,
       "messages": [{"role": "user", "content": "Write a poem about the DIAL platform"}]
     }'
   ```
   In the JSON response look for `"custom_content": {"stages": [...]}` inside the assistant message — that is the
   serialised stage data.


<details><summary>Final result:</summary>

![](/tasks/t4_stage_and_state/_screenshots/poem_chat.png)
![](/tasks/t4_stage_and_state/_screenshots/poem_terminal.png)

</details>

---

## Task 2: Calculator Agent — Stages + State

This task implements a multi-turn agentic calculator. The agent calls an LLM with a `calculate` tool. When the model
requests the tool, the agent executes it, saves the exchange to **state**, and recurses until the model gives a final
text answer.

**Why state is needed:** DIAL works in strict user ↔ assistant format. Tool messages cannot be included in the DIAL
response. But on the next turn, the LLM needs those tool exchanges to reason correctly. The solution: persist tool call
history in state → Core sends it back → the app unpacks it server-side and injects it into the LLM context.

### File map

| File                 | Role                                                                                 |
|----------------------|--------------------------------------------------------------------------------------|
| `agent.py`           | Core agentic loop — **TODO1** (stages) and **TODO2** (state)                         |
| `calculator_tool.py` | Calculator tool execution — **TODO1** (stage content)                                |
| `app.py`             | DIAL app wiring — **TODO** (wire up and run)                                         |
| `utils.py`           | Provided helper — `StageProcessor` and `unpack_messages`. Read it, no changes needed |

---

### Steps

1. **Read [t2_calculator_agent/utils.py](t2_calculator_agent/utils.py) first (no TODO)**

    - `StageProcessor.open_stage(choice, name)` — creates a stage, opens it, returns it
    - `StageProcessor.close_stage_safely(stage)` — closes without raising
    - `unpack_messages(messages, current_state_history, tool_call_history_key)` — iterates the incoming message list;
      when it finds an assistant message it reads `custom_content.state` and injects the saved tool/assistant messages
      back into the sequence so the LLM receives the full history

2. **Implement the TODO in [t2_calculator_agent/calculator_tool.py](t2_calculator_agent/calculator_tool.py) — `execute()` method**

3. **Implement TODO1 in [t2_calculator_agent/agent.py](t2_calculator_agent/agent.py) — `_process_tool_call()` method**

4. **Implement TODO2 in [t2_calculator_agent/agent.py](t2_calculator_agent/agent.py) — `handle_request()` method** (state saving and `choice.set_state()`)

5. **Implement the TODO in [t2_calculator_agent/app.py](t2_calculator_agent/app.py)**

6. Open [core/applications.json](/core/applications.json) and confirm the following entry is present (add it if
   missing):
   ```json
   "calculator-agent": {
     "displayName": "Calculator Agent",
     "description": "AI assistant that can answer general questions and perform mathematical calculations.",
     "endpoint": "http://host.docker.internal:5028/openai/deployments/calculator-agent/chat/completions"
   }
   ```

7. Run [t2_calculator_agent/app.py](t2_calculator_agent/app.py)

8. Open [DIAL Chat](http://localhost:3000/marketplace) → test **Calculator Agent**:
    - Send `"What is 123 * 456 + 789?"` — verify a `calculate` stage appears, showing arguments, expression, and result
    - Follow up with `"Now divide that result by 3"` — verify a second `calculate` stage appears and the answer is
      correct, confirming that state preserved the previous tool call history

9. Test directly via DIAL Core:
   ```bash
   curl --location 'http://localhost:8080/openai/deployments/calculator-agent/chat/completions' \
     --header 'Api-Key: dial_api_key' \
     --header 'Content-Type: application/json' \
     --data '{
       "stream": false,
       "messages": [{"role": "user", "content": "What is 15 * 7?"}]
     }'
   ```
   In the response look for `"custom_content": {"state": {"tool_call_history": [...]}}` — that is the persisted tool
   call history.

<details><summary>Final result:</summary>

![](/tasks/t4_stage_and_state/_screenshots/calc-agent-chat.png)
![](/tasks/t4_stage_and_state/_screenshots/calc-agent-chat-2.png)
![](/tasks/t4_stage_and_state/_screenshots/calc-agent-terminal.png)

</details>

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. Stage not closed — response hangs

If you forget to call `stage.close()` the SDK waits for the stage to finish and the HTTP response never completes.

Fix: always wrap the stage body in `try/finally` and call `close` in the `finally` block.

---

### 2. `append_content` with dict vs string

`append_content` accepts only `str` (rendered as markdown).

---

### 3. Forgetting `choice.set_state(self.state)` — multi-turn memory breaks

If `set_state` is never called the state is `None` on the next turn. `unpack_messages` finds nothing to inject, so the
LLM loses all tool call history. The second query will appear as if it were the first.

---

### 4. Tool messages cannot appear in a DIAL response

DIAL follows the Azure OpenAI Chat Completions spec where every response is an assistant message. Returning a tool-role
message causes a validation error. Tool call exchanges must be saved to state and re-injected server-side on the next
request.

---

### 5. State lives in `custom_content.state`, not `message.state`

When reading incoming state from a previous turn:

```python
# CORRECT
state = message.custom_content.state

# WRONG — AttributeError
state = message.state
```

---

### 6. Port mismatch

The port in `uvicorn.run(app, port=PORT)` must match the port in the `endpoint` URL in `applications.json`.

| App                         | Port |
|-----------------------------|------|
| `poem_assistant.py`         | 5027 |
| `app.py` (calculator agent) | 5028 |

</details>
