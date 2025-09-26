import os
import getpass
import socket
from pathlib import Path

from shell.commands import handle_command
from shell.parser import expand_env_and_split


def prompt() -> str:        # формирование пути и имени пользователя
    user = getpass.getuser()
    host = socket.gethostname()
    cwd = Path.cwd()
    home = Path.home()

    if cwd.is_relative_to(home):
        rel = cwd.relative_to(home)
        if rel == Path("."):
            shown = "~"
        else:
            shown = f"~{os.sep}{rel}"
    else:
        shown = str(cwd)

    shown = shown.replace("\\", "/")
    return f"{user}@{host}:{shown}$ "


def run_repl() -> None:        # Обработка и выполнение команд, прерывание работы, вывод ошибок
    while True:
        try:
            line = input(prompt())
        except (EOFError, KeyboardInterrupt):       # Прерывание по Ctrl+D или Ctrl+C
            print()
            break

        if not line.strip():
            continue

        try:
            argv = expand_env_and_split(line)
        except ValueError as e:
            print(f"parse error: {e}")
            continue

        cmd, *args = argv
        try:
            should_exit = handle_command(cmd, args)
            if should_exit:
                break
        except Exception as e:
            print(f"error: {e}")
