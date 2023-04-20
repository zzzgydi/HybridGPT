
from hybrid.agent import agent_create, agent_exec
from hybrid.logger import logger


if __name__ == "__main__":
    objective = "write a blog post about the GPT-3"
    krs = agent_create(objective=objective)

    logger.info(krs)

    for kr in krs:
        command = agent_exec(objective=objective, kr=kr)
        logger.info(command)
