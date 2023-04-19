import os
import json
import openai
from dotenv import load_dotenv
from hybrid.logger import logger

load_dotenv(verbose=True)


openai.api_base = os.getenv("OPENAI_API_BASE")
openai.api_key = os.getenv("OPENAI_API_KEY")

if __name__ == "__main__":
    task_format = {
        "description": "task description",
        "output": "task output",
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
        "Ensure the response in Chinese and can be parsed by Python json.loads:"
    )

    messages = [{"role": "system", "content": task_prompt}]

    logger.debug(task_prompt)

    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0.5,
    )['choices'][0]['message']['content']

    logger.debug(response)

    try:
        tasks = json.loads(response)
        for i, task in enumerate(tasks):
            print(str(i + 1) + ". D: " + task['description'])
            print("   O: " + task['output'])
    except Exception as e:
        logger.error(e)
