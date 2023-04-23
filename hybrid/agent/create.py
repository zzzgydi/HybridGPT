import json
from hybrid.llm import llm_chat
from hybrid.logger import logger


def agent_create(objective: str) -> list[dict]:
    task_format = {
        "kr": "key result",
        "thought": "show the your thought about to achieve this key result step by step",
        "todo": ["a list of todo to achieve this key result"],
    }
    formatted_response = json.dumps(task_format, indent=2)

    system_prompt = (
        f"You are an autonomous OKR creation AI. You have the following objective `{objective}`.\n"
        "Create a list of key results according to the objective. Each key result should be completed by the AI system WITHOUT user assistance and is more closely reached or completely reached.\n"
        "The AI system has and ONLY has the following abilities:\n"
        "1. Internet access for searches and information gathering.\n"
        "2. Long Term memory management.\n"
        "3. Text Summarization.\n"
        "4. File System access for storing and retrieving data.\n\n"
        "Return the response as a list[dict] in JSON format as described below:\n"
        f"[{formatted_response}]\n"
        "Ensure the response and can be parsed by Python json.loads:"
    )
    logger.debug(system_prompt)

    messages = [{"role": "system", "content": system_prompt}]

    try:
        response = llm_chat(messages=messages, temperature=0.5)
        tasks = json.loads(response)
        # TODO: validate tasks
        return tasks
    except Exception as e:
        logger.error(e)
        return []
