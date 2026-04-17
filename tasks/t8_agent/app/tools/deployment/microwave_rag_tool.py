from typing import Any

from tasks.t8_agent.app.tools.deployment.base import DeploymentTool


class MicrowaveRagTool(DeploymentTool):

    @property
    def deployment_name(self) -> str:
        return "microwave-rag"

    @property
    def name(self) -> str:
        return "microwave_rag_tool"

    @property
    def description(self) -> str:
        return "Searches through microwave manual requested information."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "What to search."
                }
            },
            "required": [
                "prompt"
            ]
        }
