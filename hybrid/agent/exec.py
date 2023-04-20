import json
from typing import Optional
from hybrid.llm import llm_chat
from hybrid.logger import logger


def agent_exec(objective: str, kr: dict) -> Optional[dict]:
    command_format = {"name": "command name", "args": {"arg name": "value"}}
    command_format = json.dumps(command_format, indent=2)

    commands = [
        ("Google Search", "google", {"input": "<search>"}),
        # ("Website Summary", "website_summary", {"url": "<url>"}),
        (
            "Browse Website",
            "browse_website",
            {"url": "<url>", "question": "<what_you_want_to_find_on_website>"},
        ),
        ("Write to file", "write_to_file", {
         "file": "<file>", "text": "<text>"}),
        ("Read file", "read_file", {"file": "<file>"}),
        ("Append to file", "append_to_file", {
         "file": "<file>", "text": "<text>"}),
        ("Delete file", "delete_file", {"file": "<file>"}),
        ("Search Files", "search_files", {"directory": "<directory>"}),
        ("ToDo Complete", "todo_complete", {"reason": "<reason>"}),
    ]
    commands_str = "\n".join(
        str(i + 1) + ". " + generate_command_string(cmd)
        for i, cmd in enumerate(commands)
    )

    system_prompt = (
        f"You are an autonomous OKR execution AI. You have the following objective `{objective}`.\n"
        f"Your current KR is: {kr['kr']}\n"
        "A list of todo for this KR:\n"
        f"{generate_number_list(kr['todo'])}\n"
        "The CURRENT todo sequence number you NEED TO complete is 1.\n\n"
        "Commands:\n"
        f"{commands_str}\n\n"
        'Exclusively use the commands listed in double quotes e.g. "command name"\n'
        "You should only respond in JSON format as described below:\n"
        f"{command_format}\n"
        "Ensure the response and can be parsed by Python json.loads and NOTHING ELSE:"
    )

    logger.debug("---------- EXEC PROMPT BEGIN ----------")
    logger.debug(system_prompt)
    logger.debug("---------- EXEC PROMPT END ----------")

    messages = [{"role": "system", "content": system_prompt}]

    try:
        response = llm_chat(messages=messages, temperature=0.5)
        command = json.loads(response)
        # TODO: validate command
        return command
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON response: {response}")
        return None
    except Exception as e:
        logger.error(e)
        return None


def generate_command_string(command: tuple) -> str:
    args_string = ", ".join(
        f'"{key}": "{value}"' for key, value in command[2].items())
    return f'{command[0]}: "{command[1]}", args: {args_string}'


def generate_number_list(array: list[str]) -> str:
    return "\n".join(
        str(i + 1) + ". " + s for i, s in enumerate(array)
    )
