from hybrid.agent import agent_create, agent_exec
from hybrid.logger import logger
from hybrid.spinner import Spinner


if __name__ == "__main__":
    objective = "write a blog post about the GPT-3"

    with Spinner():
        krs = agent_create(objective=objective)

    logger.info(krs)

    for kr in krs:
        command = agent_exec(objective=objective, kr=kr)
        logger.info(command)
