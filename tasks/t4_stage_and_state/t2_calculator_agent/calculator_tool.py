import ast
import json
import operator
from typing import Any

from aidial_client.types.chat import ToolParam, FunctionParam

from aidial_sdk.chat_completion import Message, Role, ToolCall
from aidial_sdk.chat_completion.stage import Stage


_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}


def _eval_node(node) -> int | float:
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        return _ALLOWED_OPS[op](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in _ALLOWED_OPS:
            raise ValueError(f"Unsupported operator: {op.__name__}")
        return _ALLOWED_OPS[op](_eval_node(node.operand))
    raise ValueError(f"Unsupported expression node: {type(node).__name__}")


class CalculateTool:

    @property
    def name(self) -> str:
        return "calculate"

    @property
    def description(self) -> str:
        return "Evaluates a mathematical expression and returns the numeric result."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "A mathematical expression to evaluate, e.g. '2 + 2', '10 * (3 + 5) / 2'"
                }
            },
            "required": ["expression"]
        }

    @property
    def schema(self) -> ToolParam:
        return ToolParam(
            type="function",
            function=FunctionParam(
                name=self.name,
                description=self.description,
                parameters=self.parameters
            )
        )

    async def execute(self, tool_call: ToolCall, stage: Stage) -> Message:
        args = json.loads(tool_call.function.arguments)
        expression = args["expression"]

        stage.append_name(f": {expression}")

        stage.append_content(f"## Expression:\n```\n{expression}\n```\n\n")
        result = self._calculate(expression)
        stage.append_content(f"## Result:\n`{result}`\n")

        return Message(
            role=Role.TOOL,
            content=result,
            tool_call_id=tool_call.id,
        )

    def _calculate(self, expression: str) -> str:
        try:
            tree = ast.parse(expression.strip(), mode="eval")
            return str(_eval_node(tree.body))
        except Exception as e:
            return f"Error evaluating '{expression}': {e}"
