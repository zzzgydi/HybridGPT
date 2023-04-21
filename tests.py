import re


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


if __name__ == "__main__":
    test = """<reason>[YOUR_REASONING]</reason>
        <command>[COMMAND]</command>
        <argument>[ARGUMENT]</argument>
    """

    print(parse_response(test))
