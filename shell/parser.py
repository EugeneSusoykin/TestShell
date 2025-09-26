import os
import platform
import shlex


def expand_env_and_split(line: str) -> list[str]:
    expanded = os.path.expandvars(line)
    is_windows = platform.system().lower().startswith("win")
    return shlex.split(expanded, posix=not is_windows)

