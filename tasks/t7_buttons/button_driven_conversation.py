from typing import Union

import uvicorn

from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response, Message
from aidial_sdk.deployment.configuration import ConfigurationRequest, ConfigurationResponse

NEW_ORDER = 'new_order'
CHECK_ORDER_INFO = 'check_order_info'
CONVERSATION_STARTED_BUTTON = 'conversation_starter_button'
ORDER_BUTTON = 'order_button'
SUBMIT_ORDER_BUTTON = 'submit_order_button'
NOTHING_MORE = 'nothing_more'
FINISH_ORDER = 'finish_order'
DELETE_ORDER = 'delete_order'


class ButtonsSampleApplication(ChatCompletion):

    def __init__(self):
        self.item_buttons = [
            {"const": "Pencil", "title": "Pencil", "dial:widgetOptions": {"submit": True}},
            {"const": "Notebook", "title": "Notebook", "dial:widgetOptions": {"submit": True}}
        ]

        self.items_buttons_with_stop = [
            {"const": NOTHING_MORE, "title": "Nothing more, make order", "dial:widgetOptions": {"submit": True}}
        ]
        self.items_buttons_with_stop.extend(self.item_buttons)

        self.finish_delete_order = [
            {"const": FINISH_ORDER, "title": "Finish order", "dial:widgetOptions": {"confirmationMessage": "Are you sure that you want to proceed with order?", "submit": True}},
            {"const": DELETE_ORDER,"title": "Delete order","dial:widgetOptions": {"confirmationMessage": "Are you sure you delete order items?","submit": True}}
        ]

        self.order_items: dict[str, int] = {}

    async def chat_completion(
            self, request: Request, response: Response
    ) -> None:
        last_user_message = request.messages[-1]
        print(last_user_message)

        with (response.create_single_choice() as choice):

            if ((not last_user_message.custom_content or not last_user_message.custom_content.form_value)
                    and request.custom_fields.configuration):
                # for FIRST user message the value is stored in configuration field
                configuration = request.custom_fields.configuration

                if configuration is not None and isinstance(configuration, dict):
                    starter_button_value = configuration.get(CONVERSATION_STARTED_BUTTON)
                    if starter_button_value == NEW_ORDER:
                        choice.set_form_schema(
                            {
                                "type": "object",
                                "dial:chatMessageInputDisabled": True,
                                "properties": {
                                    ORDER_BUTTON: {
                                        "description": "Choose the items",
                                        "type": "string",
                                        "dial:widget": "buttons",
                                        "oneOf": self.item_buttons
                                    }
                                }
                            }
                        )
                    elif starter_button_value == CHECK_ORDER_INFO:
                        choice.append_content("Provide order number")

            elif custom_content := last_user_message.custom_content:
                if form_value_dict := custom_content.form_value:
                    if isinstance(form_value_dict, dict):
                        order_button = form_value_dict.get(ORDER_BUTTON)
                        submit_order_button = form_value_dict.get(SUBMIT_ORDER_BUTTON)
                        if order_button:
                            if order_button == NOTHING_MORE:
                                info = self._prepare_order_info(last_user_message)
                                choice.append_content(info)
                                choice.set_form_schema(
                                    {
                                        "type": "object",
                                        "dial:chatMessageInputDisabled": True,
                                        "properties": {
                                            SUBMIT_ORDER_BUTTON: {
                                                "description": "Check the order and submit it",
                                                "type": "string",
                                                "dial:widget": "buttons",
                                                "oneOf": self.finish_delete_order
                                            }
                                        }
                                    }
                                )
                            else:
                                info = self._prepare_order_info(last_user_message)
                                choice.append_content(info)
                                choice.set_form_schema(
                                    {
                                        "type": "object",
                                        "dial:chatMessageInputDisabled": True,
                                        "properties": {
                                            ORDER_BUTTON: {
                                                "description": "Choose the items",
                                                "type": "string",
                                                "dial:widget": "buttons",
                                                "oneOf": self.items_buttons_with_stop
                                            }
                                        }
                                    }
                                )
                        elif submit_order_button:
                            if submit_order_button == FINISH_ORDER:
                                choice.append_content("Congratulations, you have successfully submitted order🎉\n\r")
                                info = self._prepare_order_info(last_user_message)
                                choice.append_content(info)
                                choice.set_form_schema(
                                    {
                                        "type": "object",
                                        "dial:chatMessageInputDisabled": True,
                                        "properties": {}
                                    }
                                )
                            else:
                                self.order_items = {}
                                choice.append_content("We have deleted order items.")
                                choice.set_form_schema(
                                    {
                                        "type": "object",
                                        "dial:chatMessageInputDisabled": True,
                                        "properties": {
                                            ORDER_BUTTON: {
                                                "description": "Choose the items",
                                                "type": "string",
                                                "dial:widget": "buttons",
                                                "oneOf": self.item_buttons
                                            }
                                        }
                                    }
                                )


            else:
                choice.append_content(f"Echo✨\n\r{last_user_message.content}")

    async def configuration(self, request: ConfigurationRequest) -> Union[ConfigurationResponse, dict]:
        return {
            "type": "object",
            "dial:chatMessageInputDisabled": True,
            "properties": {
                CONVERSATION_STARTED_BUTTON: {
                    "description": "Choose the flow",
                    "type": "string",
                    "dial:widget": "buttons",
                    "oneOf": [
                        {
                            "const": NEW_ORDER,
                            "title": "New order",
                            "dial:widgetOptions": {
                                "submit": True
                            }
                        },
                        {
                            "const": CHECK_ORDER_INFO,
                            "title": "Check order info",
                            "dial:widgetOptions": {
                                "submit": True
                            }
                        }
                    ]
                }
            }
        }

    def _prepare_order_info(self, last_message: Message) -> str:
        if last_message.custom_content and last_message.custom_content.form_value:
            form_value_info = last_message.custom_content.form_value
            if isinstance(form_value_info, dict):
                order_info = form_value_info.get(ORDER_BUTTON)
                if order_info and not order_info == NOTHING_MORE:
                    if self.order_items.get(order_info):
                        self.order_items[order_info] += 1
                    else:
                        self.order_items[order_info] = 1

        csv_lines = ["|Item name|quantity|", "|----------------|-------------|"]
        csv_lines.extend([f"{item}|{qty}" for item, qty in self.order_items.items()])
        csv_output = "\n".join(csv_lines)

        return f"Order info:\n{csv_output}"


app = DIALApp()
app.add_chat_completion("buttons-sample", ButtonsSampleApplication())

if __name__ == "__main__":
    import sys

    if 'pydevd' in sys.modules:
        config = uvicorn.Config(app, port=5031, host="0.0.0.0")
        server = uvicorn.Server(config)
        import asyncio

        asyncio.run(server.serve())
    else:
        uvicorn.run(app, port=5031, host="0.0.0.0")
