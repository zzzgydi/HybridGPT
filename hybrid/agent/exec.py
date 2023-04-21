import re
import json
from typing import Optional
from duckduckgo_search import ddg
from urllib.request import urlopen
from bs4 import BeautifulSoup
from hybrid.llm import llm_chat
from hybrid.logger import logger
from hybrid.memory import memory
from hybrid.spinner import Spinner
from hybrid.token import count_message_tokens


INSTRUCTIONS = """
Carefully consider your next command.
Supported commands are: web_search, web_summary, write_file, or done

web_search: Search the link relevant to the objective.
web_summary: Browser the link and summary the website.
write_file: Write the content to a file.
done: finish the todo.

The mandatory response format is:

<reason>[YOUR_REASONING]</reason>
<command>[COMMAND]</command>
<argument>[ARGUMENT]</argument>

Send a separate "done" command *after* the todo or kr was achieved.
RESPOND WITH PRECISELY ONE THOUGHT/COMMAND/ARGUMENT COMBINATION.
DO NOT CHAIN MULTIPLE COMMANDS.
DO NOT INCLUDE EXTRA TEXT BEFORE OR AFTER THE COMMAND.

Examples:

<reason>Search for websites relevant to salami pizza.</reason>
<command>web_search</command>
<argument>salami pizza</argument>

<reason>Scrape information about Apples.</reason>
<command>web_summary</command>
<argument>https://en.wikipedia.org/wiki/Apple </argument>

<reason>Write 'Hello, world!' to file</reason>
<command>write_file</command>
<argument>Hello, world!</argument>

<reason>I have gathered enough information.</reason>
<command>done</command>
"""


def agent_exec(objective: str, kr: dict) -> Optional[dict]:
    # command_format = {
    #     "reason": "reason for why choose this command",
    #     "name": "command name",
    #     "args": {"arg name": "value"},
    # }
    # command_format = json.dumps(command_format, indent=2)

    # commands = [
    #     ("Web Search", "web_search", {"search": "<search>"}),
    #     ("Web scrape", "web_scrape", {"url": "<url>"}),
    #     ("Write File", "write_file", {"file": "<file>", "text": "<text>"}),
    #     ("Read File", "read_file", {"file": "<file>"}),
    #     ("Append File", "append_file", {"file": "<file>", "text": "<text>"}),
    #     ("Todo Complete", "done", {"reason": "<reason>"}),
    # ]
    # commands_str = generate_number_list(
    #     generate_command_string(cmd) for cmd in commands
    # )

    for todo in kr["todo"]:
        short_term = []
        step_count = 0
        while True:
            role_prompt = (
                f"You are an autonomous agent.\n"
                "You has and ONLY has the following abilities:\n"
                "1. Internet access for searches and information gathering.\n"
                "2. Long Term memory management.\n"
                "3. Text Summarization.\n"
                "4. File System access for storing and retrieving data."
            )
            system_prompt = (
                # f"OBJECTIVE: {objective}\n"
                f"Key Result: {kr['kr']}\n"
                f"Current TODO: {todo}"
                # f"Current step: {step_count + 1}\n\n"
                # 'IMPORTANT:\nBe sure to send a separate "done" command within 5 steps.'
            )

            constraint_prompt = (
                "Constraints:\n"
                # "Performance Evaluation:\n"
                # '1. MUST send a "done" command *after* the todo was achieved.\n'
                "1. Continuously review and analyze your actions to ensure you are performing to the best of your abilities.\n"
                "2. Constructively self-criticize your big-picture behavior constantly.\n"
                "3. Reflect on past decisions and strategies to refine your approach.\n"
                "4. Every command has a cost, so be smart and efficient. Aim to complete tasks in the least number of steps."
            )

            # user_prompt = (
            #     "Carefully consider your next command.\n"
            #     f"{commands_str}\n\n"
            #     "Constraints:\n"
            #     '1. Send a separate "done" command *after* the todo was achieved.\n'
            #     "2. Reflect on past decisions and strategies to refine your approach.\n"
            #     "3. Make sure the command WILL NOT run into useless loop!\n\n"
            #     'Exclusively use the commands listed in double quotes e.g. "command name"\n'
            #     "You should only respond in JSON format as described below:\n"
            #     f"{command_format}\n"
            #     "Ensure the response and can be parsed by Python json.loads and NOTHING ELSE:"
            # )

            MAX_TOKENS = 4000
            OUTPUT_TOKENS = 500

            prompt_tokens = 3500
            context_index = 0

            context = ""
            messages = [
                {"role": "system", "content": role_prompt},
                {"role": "system", "content": system_prompt},
                {
                    "role": "user",
                    "content": f"This reminds you of these events from your past:\n{context}",
                },
                # {"role": "user", "content": constraint_prompt},
                {"role": "user", "content": f"INSTRUCTIONS:\n{INSTRUCTIONS}"},
            ]

            while context_index < len(short_term):
                split_context = short_term[context_index:]
                context = "\n\n".join(
                    (
                        f"Reason: {command['reason']}\n"
                        f"Command: {command['name']}, args: {command['args']}\n"
                        f"Result: \n{result}"
                    )
                    for command, result in split_context
                )
                messages = [
                    {"role": "system", "content": role_prompt},
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"This reminds you of these events from your past:\n{context}",
                    },
                    # {"role": "user", "content": constraint_prompt},
                    {"role": "user", "content": f"INSTRUCTIONS:\n{INSTRUCTIONS}"},
                ]
                prompt_tokens = count_message_tokens(messages)
                if prompt_tokens > MAX_TOKENS - OUTPUT_TOKENS:
                    context_index += 1
                else:
                    break

            logger.debug("---------- PROMPT BEGIN ----------")
            for message in messages:
                logger.debug(message["role"] + ": " + message["content"])
            logger.debug("---------- PROMPT END ----------")

            try:
                with Spinner():
                    response = llm_chat(
                        messages=messages,
                        temperature=0.2,
                        max_tokens=MAX_TOKENS - prompt_tokens,
                    )

                command = parse_response(response)

                logger.info(f"KR: {kr['kr']}")
                logger.info(f"Todo: {todo}")
                logger.info(f"Reason: {command['reason']}")
                logger.info(f"Command: {command['name']}, args: {command['args']}")

                cmd_name = command["name"]
                cmd_args = command["args"]

                if cmd_name == "done":
                    logger.info("TODO DONE!!!")
                    break
                if cmd_name == "web_search":
                    ddg_results = ddg(cmd_args, max_results=2)
                    ddg_results = "\n".join(
                        f"{e['title']}   {e['href']}" for e in ddg_results
                    )
                    short_term.append((command, ddg_results))
                elif cmd_name == "web_summary":
                    try:
                        with urlopen(cmd_args) as response:
                            html = response.read()

                        response_text = memory.summarize_memory_if_large(
                            BeautifulSoup(html, features="lxml").get_text(),
                            2000,
                        )
                    except Exception as e:
                        logger.error(e)
                        response_text = str(e)

                    short_term.append((command, response_text))
                else:
                    short_term.append((command, "ok"))

            except json.JSONDecodeError:
                logger.error(f"Invalid JSON response: {response}")
            except Exception as e:
                logger.error(e)

            logger.info("=" * 30)
            step_count += 1


def parse_response(response: str) -> dict:
    """
    <reason>[YOUR_REASONING]</reason>
    <command>[COMMAND]</command>
    <argument>[ARGUMENT]</argument>
    """

    PATTERN = r"<(\w+)>(.*?)</\w+>"
    matches = re.findall(PATTERN, response)

    reason = matches[0][1]
    command = matches[1][1]
    argument = matches[2][1]

    return {
        "reason": reason,
        "name": command,
        "args": argument,
    }
