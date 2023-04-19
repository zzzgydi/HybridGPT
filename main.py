import os
import json
import openai
from dotenv import load_dotenv
from hybrid.logger import logger

load_dotenv(verbose=True)


# openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_command_string(command: tuple) -> str:
    args_string = ", ".join(f'"{key}": "{value}"' for key, value in command[2].items())
    return f'{command[0]}: "{command[1]}", args: {args_string}'


def execute_task(objective: str, tasks: list[dict], current: int):
    tasks_str = "\n".join(
        str(i + 1) + ". " + task["description"] for i, task in enumerate(tasks)
    )

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
        ("Write to file", "write_to_file", {"file": "<file>", "text": "<text>"}),
        ("Read file", "read_file", {"file": "<file>"}),
        ("Append to file", "append_to_file", {"file": "<file>", "text": "<text>"}),
        ("Delete file", "delete_file", {"file": "<file>"}),
        ("Search Files", "search_files", {"directory": "<directory>"}),
        ("Task Complete", "task_complete", {"reason": "<reason>"}),
    ]

    commands_str = "\n".join(
        str(i + 1) + ". " + generate_command_string(cmd)
        for i, cmd in enumerate(commands)
    )

    cur_task = tasks[current]
    exec_prompt = (
        f"You are an autonomous task execution AI. You have the following objective `{objective}`.\n"
        "You have the following tasks:\n"
        f"{tasks_str}\n\n"
        "Here is your current task that you should focus on:\n"
        f"Task Description: {cur_task['description']}\n"
        f"Task Action: {cur_task['action']}\n\n"
        "If you are unsure how you previously did something or want to recall past"
        " events, thinking about similar events will help you remember.\n"
        "Commands:\n"
        f"{commands_str}\n\n"
        'Exclusively use the commands listed in double quotes e.g. "command name"\n'
        "Return the command in JSON format as described below:\n"
        f"{command_format}\n"
        "Ensure the response and can be parsed by Python json.loads:"
    )

    # logger.debug("---------- EXEC TASK PROMPT BEGIN ----------")
    # logger.debug(exec_prompt)
    # logger.debug("---------- EXEC TASK PROMPT END ----------")

    logger.info(f"Task Description: {cur_task['description']}")
    logger.info(f"Task Action: {cur_task['action']}")

    messages = [
        {"role": "system", "content": exec_prompt},
        {
            "role": "user",
            "content": "Determine which next command to use, and respond using the format specified above:",
        },
    ]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
    )["choices"][0]["message"]["content"]

    logger.info(f"Task Response: {response}")


if __name__ == "__main__":
    task_format = {
        "description": "task description",
        "action": "how to achieve this task",
    }
    formatted_response = json.dumps(task_format, indent=2)
    objective = "write a blog post about the GPT-3"
    task_prompt = (
        f"You are an autonomous task creation AI. You have the following objective `{objective}`.\n"
        "Create a list of tasks to be completed by the AI system WITHOUT user assistance such that your objective is more closely reached or completely reached.\n"
        "The AI system has and ONLY has the following abilities:\n"
        "1. Internet access for searches and information gathering.\n"
        "2. Long Term memory management.\n"
        "3. Text Analysis and Summarization.\n"
        "4. File System access for storing and retrieving data.\n\n"
        # "Make sure that each task can be completed by the AI system WITHOUT user assistance.\n"
        "Return the response as a list[task] in JSON format as described below:\n"
        f"[{formatted_response}]\n"
        "Ensure the response and can be parsed by Python json.loads:"
    )

    messages = [{"role": "system", "content": task_prompt}]

    logger.debug(task_prompt)

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.5,
    )["choices"][0]["message"]["content"]

    logger.debug(response)

    try:
        tasks = json.loads(response)
        # for i, task in enumerate(tasks):
        #     print(str(i + 1) + ". D: " + task["description"])
        #     print("   O: " + task["action"])
        for i, task in enumerate(tasks):
            execute_task(objective, tasks, i)
    except Exception as e:
        logger.error(e)
