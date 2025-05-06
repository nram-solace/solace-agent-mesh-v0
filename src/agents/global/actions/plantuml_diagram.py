"""PlantUML diagram"""

import platform
import os
import tempfile
import uuid
import shutil
import subprocess

from solace_ai_connector.common.log import log
from ....common.action import Action
from ....common.action_response import ActionResponse
from ....services.file_service import FileService

PLANTUML_PROMPT = """Generate a PlantUML markup language for the given description by the user. Supports sequence diagrams, class diagrams, use case diagrams, activity diagrams, component diagrams, state diagrams, and timing diagrams. Newlines must be escaped with a backslash and put quotes around participants names. Respond only with PlantUML markup, do not include any other text, symbols or quotes.

Rules to follow for all diagrams:
- Always include @startuml at the beginning and @enduml at the end
- Use simple quotes for names, not double quotes
- Avoid using <<stereotype>> syntax in state diagrams unless absolutely necessary
- For state diagrams, use simple state names without spaces (like LoginScreen instead of "Login Screen")
- If you need descriptive names, use the 'as' keyword (e.g., [*] --> LoginScreen as "Login Screen")
- Don't use variables if they are not declared
- Never skip lines
- For notes in all diagrams:
    - Use the simple syntax: `note over Participant: Text` without any positioning numbers
    - Do not use positioning numbers (like `at 25`) in note commands
    - Never combine multiple participants in a single note

Rules for sequence diagrams:
- Only use notes to cover one or two participants per line
- Do not use the `activate` or `deactivate` commands directly after a delay notation (`...`), whether directly or with a note in between
- Do not use the `activate` or `deactivate` commands twice in a row, whether directly or with a note in between

Rules for activity diagrams:
- Do not use the `backward:` keyword for loops or returning to previous steps
- Instead, use the label and goto pattern:
  1. Add a label to the target activity: `label label_name`
  2. Use goto to reference that label: `goto label_name`
- Always place labels immediately after the activity they refer to
- Labels should use lowercase with underscores for readability (e.g., `label browse_products`)

Rules for state diagrams:
- Use simple state names without spaces and without quotes
- When stereotypes are absolutely necessary, use the correct syntax:
  - For existing states: `state StateName <<stereotype>>`
  - For new states with descriptions: `state "Description" as StateName <<stereotype>>`
- Always place stereotypes after the state name, not before
- If using skinparam for stereotype styling, ensure it's properly defined: `skinparam state \{ BackgroundColor<<stereotype>> Color\}
- For notes in state diagrams:
  - Do NOT use `note over StateName` syntax (this is for sequence diagrams)
  - Instead use directional positioning: `note left of StateName`, `note right of StateName`, `note top of StateName`, or `note bottom of StateName`
  - Example: `note left of OrderCreated : Initial customer order`

Rules for timing diagrams:
- Never include notes
- For 'robust' participants, use named states instead of symbolic states
   - CORRECT: `PS is "ON"` or `PS is ON`
   - INCORRECT: `PS is {+}` or `PS is {-}`
- For 'concise' participants, use numeric values (e.g., `BP is 10`)
"""


class PlantUmlDiagram(Action):

    def __init__(self, **kwargs):
        super().__init__(
            {
                "name": "plantuml",
                "prompt_directive": (
                    "Generate PlantUML diagrams using description. Supports sequence diagrams, class diagrams, "
                    "use case diagrams, activity diagrams, component diagrams, state diagrams, and timing diagrams."
                ),
                "params": [
                    {
                        "name": "diagram_description",
                        "desc": "The detailed description of the diagram to be generated in natural English language.",
                        "type": "string",
                    }
                ],
                "required_scopes": ["global:plantuml:read"],
            },
            **kwargs,
        )

    def invoke(self, params, meta={}) -> ActionResponse:
        # Do a local command to run plantuml -tpng
        description = params.get("diagram_description")
        agent = self.get_agent()
        messages = [
            {"role": "system", "content": PLANTUML_PROMPT},
            {"role": "user", "content": description},
        ]
        agent = self.get_agent()
        try:
            response = agent.do_llm_service_request(messages=messages)
            expression = response.get("content")
        except TimeoutError as e:
            log.error("LLM request timed out: %s", str(e))
            return ActionResponse(message="LLM request timed out")
        except Exception as e:
            log.error("Failed to process content with LLM: %s", str(e))
            return ActionResponse(message="Failed to process content with LLM")

        # Surround expression with @startuml and @enduml if missing
        if not expression.startswith("@startuml"):
            expression = f"@startuml\n{expression}"
        if not expression.endswith("@enduml"):
            expression = f"{expression}\n@enduml"
        log.debug("PlantUML expression: %s", expression)
        files = []

        try:
            temp_dir = tempfile.mkdtemp()
            # Create a unique filename with .puml extension
            diagram_id = str(uuid.uuid4())
            puml_filename = f"diagram_{diagram_id}.puml"
            puml_path = os.path.join(temp_dir, puml_filename)
            png_path = os.path.join(temp_dir, f"diagram_{diagram_id}.png")

            # Write PlantUML content to input file
            with open(puml_path, 'w', encoding='utf-8') as f:
                f.write(expression)

            # Run PlantUML
            subprocess.run(
                ["plantuml", "-tpng", puml_path, "-o", temp_dir],
                shell=platform.system() == "Windows",
                check=True,
                capture_output=True,
                text=True,
            )

            # Upload the generated image
            file_service = FileService()
            file_meta = file_service.upload_from_file(
                png_path,
                meta.get("session_id"),
                data_source="Global Agent - PlantUML Action",
            )
            files.append(file_meta)

        except FileNotFoundError as e:
            log.error("PlantUML executable not found: %s", str(e))
            return ActionResponse(
                message="PlantUML executable not found. Please ensure PlantUML is installed and available in PATH.",
            )
        except subprocess.CalledProcessError as e:
            log.error("Subprocess failed with stderr: %s", str(e))
            return ActionResponse(
                message=f"Failed to create diagram: {str(e)}",
            )
        finally:
            if 'temp_dir' in locals() and os.path.exists(temp_dir):
                try:
                    shutil.rmtree(temp_dir)  # Remove directory and all contents
                except:
                    pass

        return ActionResponse(
            message=f"diagram created with the plantUML: \n```\n{expression}\n```",
            files=files,
        )
