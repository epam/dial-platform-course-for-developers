from typing import Any

from tasks.t8_agent.app.tools.deployment.base import DeploymentTool


class EssayGenerationTool(DeploymentTool):

    @property
    def deployment_name(self) -> str:
        return "essay-assistant-gpt"

    @property
    def name(self) -> str:
        return "essay_generation_tool"

    @property
    def description(self) -> str:
        return "Generates assay on demand."

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "Extensive description of the essay that should be generated."
                }
            },
            "required": [
                "prompt"
            ]
        }
