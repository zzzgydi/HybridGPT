def generate_command_string(command: tuple) -> str:
    args_string = ", ".join(f'"{key}": "{value}"' for key, value in command[2].items())
    return f'{command[0]}: "{command[1]}", args: {args_string}'


def generate_number_list(array: list[str]) -> str:
    return "\n".join(str(i + 1) + ". " + s for i, s in enumerate(array))
