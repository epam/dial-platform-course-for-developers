# Buttons and Configuration Endpoint

In this task you will learn how to expose a **configuration endpoint** in a DIAL application and use it to render
interactive **buttons** in DIAL Chat. You will extend the Essay Assistant with conversation starter buttons, then
explore a fully button-driven ordering flow.

---

## Task 1: Add Conversation Starter Buttons to Essay Assistant

> A configuration endpoint lets DIAL Chat show buttons or form controls **before** the first message. The JSON Schema
> you return is rendered automatically in the Chat UI as interactive widgets.

### Steps

1. **Open [t3_add_applications/essay/essay_assistant.py](../t3_add_applications/essay/essay_assistant.py)**

   Add a `configuration` method to the `EssayAssistantApplication` class after `chat_completion`. The method must
   return a JSON Schema dict that renders conversation starter buttons in DIAL Chat.

   First, add these imports at the top of the file:
   ```python
   from typing import Union
   from aidial_sdk.deployment.configuration import ConfigurationRequest, ConfigurationResponse
   ```

   The method signature:
   ```python
   async def configuration(self, request: ConfigurationRequest) -> Union[ConfigurationResponse, dict]:
   ```

   The returned schema must have:
   - `"type": "object"` and a `"properties"` section
   - A property using `"dial:widget": "buttons"` with a `"oneOf"` list of button definitions
   - Each button entry has `"const"`, `"title"`, and `"dial:widgetOptions": {"populateText": "..."}`

   Below is a two-button skeleton to get you started. **Your task: add a third button** —
   *"About a cat that plays guitar"* — with a suitable `populateText` value:

   ```python
   async def configuration(self, request: ConfigurationRequest) -> Union[ConfigurationResponse, dict]:
       return {
           "type": "object",
           "properties": {
               "conversation_starter_button": {
                   "description": "Conversation starters",
                   "type": "number",
                   "dial:widget": "buttons",
                   "oneOf": [
                       {
                           "const": 1,
                           "title": "About elephant in space",
                           "dial:widgetOptions": {"populateText": "Generate me one about elephant in space"}
                       },
                       {
                           "const": 2,
                           "title": "About dog that can sing",
                           "dial:widgetOptions": {"populateText": "Generate essay about dog that can sing"}
                       }
                       # TODO: add a third button here — "About a cat that plays guitar"
                   ]
               }
           }
       }
   ```

   **Experiment 1:** Change one of the buttons from `populateText` to `"submit": True`. Notice how the behavior differs:
   `populateText` fills the chat input for editing before sending; `submit: True` sends the form immediately on click.

   **Experiment 2:** Add `"dial:chatMessageInputDisabled": True` at the top level of the returned schema (alongside
   `"type"` and `"properties"`). This hides the free-text input and forces button-only interaction.

2. **Open [core/applications.json](/core/applications.json) and add `configurationEndpoint`** to both essay assistant
   entries:

   ```json
   "essay-assistant-gpt": {
   ...
     "features": {
       "configurationEndpoint": "http://host.docker.internal:5025/openai/deployments/essay-assistant-gpt/configuration"
     }
   },
   "essay-assistant-sonnet": {
   ...
     "features": {
       "configurationEndpoint": "http://host.docker.internal:5026/openai/deployments/essay-assistant-sonnet/configuration"
     }
   }
   ```

3. **Restart the Essay Assistant apps** (both `app_gpt.py` and `app_sonnet.py` must be restarted to pick up the new
   `configuration` method)

4. **Open [DIAL Chat](http://localhost:3000/marketplace) and test Essay Assistant** — when you start a new
   conversation, starter buttons should appear above the chat input

5. **Test the configuration endpoint directly via DIAL Core:**
   ```bash
   curl --location 'http://localhost:8080/v1/deployments/essay-assistant-gpt/configuration' \
     --header 'Api-Key: dial_api_key'
   ```
   You should receive the raw JSON Schema your `configuration()` method returns.

<details><summary>Final result:</summary>

![Essay Assistant with starter buttons](/tasks/t7_buttons/_screenshots/essay-assistant-with-starter-buttons.png)

</details>

---

## Task 2: Register and Explore the Button-Driven Conversation App

> [button_driven_conversation.py](button_driven_conversation.py) is a **pre-built** application demonstrating a
> multi-step, fully button-driven ordering flow. You do not need to implement anything — read the code, register the
> app, and explore the behavior in Chat.

### Steps

1. **Read [button_driven_conversation.py](button_driven_conversation.py)** and pay attention to:
    - How `configuration()` returns the initial starter buttons with `"submit": True` and
      `"dial:chatMessageInputDisabled": True`
    - How `chat_completion()` dispatches based on `request.custom_fields.configuration` (first message) vs
      `last_user_message.custom_content.form_value` (subsequent messages)
    - How `choice.set_form_schema()` injects the next set of buttons after each step
    - How `self.order_items` accumulates items across turns using the stateful class instance

2. **Open [core/applications.json](/core/applications.json) and confirm or add the following entry:**

   ```json
   "buttons-sample": {
     "displayName": "Button-Driven Application",
     "description": "Demonstrates DIAL buttons capabilities",
     "endpoint": "http://host.docker.internal:5031/openai/deployments/buttons-sample/chat/completions",
     "features": {
       "configurationEndpoint": "http://host.docker.internal:5031/openai/deployments/buttons-sample/configuration"
     }
   }
   ```

3. **Run [button_driven_conversation.py](button_driven_conversation.py)**

4. **Open [DIAL Chat](http://localhost:3000/marketplace) and test Button-Driven Application:**
    - Click **"New order"** → pick items (Pencil, Notebook) → click **"Nothing more, make order"** → review the
      order summary → click **"Finish order"** or **"Delete order"** (notice the confirmation dialog)
    - Start a new conversation and click **"Check order info"** to see the plain-text response path (no buttons)
    - Notice how the chat text input remains disabled throughout the entire ordering flow

<details><summary>Final result:</summary>

![Button-driven ordering flow](/tasks/t7_buttons/_screenshots/button-driven-app-usage-sample.png)

</details>

---

<details><summary>Pitfalls & Common Mistakes</summary>

### 1. Configuration endpoint registered but `configuration()` not implemented

If `configurationEndpoint` is set in `applications.json` but your Python class does not implement `configuration()`,
or if the method raises an exception, DIAL Chat will display an error when the user tries to open the application.

Fix: always implement `configuration()` when you register a `configurationEndpoint`. If you want no configuration UI,
return a minimal empty schema:

```python
async def configuration(self, request: ConfigurationRequest) -> Union[ConfigurationResponse, dict]:
    return {"type": "object", "properties": {}}
```

---

### 2. Reading the button value from the wrong field

The button value from the **configuration panel** (first turn) arrives in `request.custom_fields.configuration`.
The button value from **mid-conversation buttons** (subsequent turns via `set_form_schema`) arrives in
`message.custom_content.form_value`. Mixing these up produces `None` where a value is expected.

```python
# First turn — configuration panel value
configuration = request.custom_fields.configuration
value = configuration.get("my_field")  # ← here

# Subsequent turns — form button value
form_value = message.custom_content.form_value
value = form_value.get("my_field")  # ← here
```

---

### 3. `dial:chatMessageInputDisabled` placed inside a property

The flag must be at the **root level** of the schema object:

```json
// CORRECT — at schema root
{
  "type": "object",
  "dial:chatMessageInputDisabled": true,
  "properties": {
    ...
  }
}

// WRONG — inside a property; has no effect
{
  "type": "object",
  "properties": {
    "my_field": {
      "dial:chatMessageInputDisabled": true
    }
  }
}
```

---

### 4. `populateText` vs `submit` confusion

`populateText` fills the chat text input and waits for the user to press Send — the user can edit the text first.
`submit: true` sends the form immediately on button click, skipping the text field entirely. Do not set both; `submit`
takes precedence when combined.

---

### 5. Port mismatch

| App                             | Port |
|---------------------------------|------|
| `essay/app_gpt.py`              | 5025 |
| `essay/app_sonnet.py`           | 5026 |
| `button_driven_conversation.py` | 5031 |

The port in `uvicorn.run(app, port=PORT)` must match the port in `endpoint` URL in `applications.json`.

</details>
