import os.path
from pathlib import Path
from stat import filemode
import time


_OLDPWD = Path.cwd()


def _change(path: str) -> Path:    # Замена "~", "$HOME", "${USER}" на реальный путь
    s = os.path.expandvars(path)
    if ("$HOME" in path or "${HOME}" in path) and "HOME" not in os.environ:
        home = str(Path.home())
        s = s.replace("$HOME", home).replace("${HOME}", home)

    s = os.path.expanduser(s)
    return Path(s).resolve()

    # os.path.expanduser - заменяет ~ на домашнюю директорию пользователя
    # os.path.expanduser("~/projects") -> "/home/user/projects"
    #
    # os.path.expandvars - заменяет переменные окружения из ОС
    # os.environ["MYDIR"] = "/tmp"
    # os.path.expandvars("$MYDIR/logs") -> "/tmp/logs"
    #
    # .resolve() - оптимизирует путь, убирает лишнее


def _cmd_cd(args: list[str]) -> None:    # Команда cd
    # "cd" - домашняя директория
    # "cd -" - предыдущая директория
    # "cd <path>" - указанная директория

    global _OLDPWD

    if not args:
        target = Path.home()
    elif args[0] == '-':
        target = _OLDPWD
    else:
        target = _change(args[0])

    if not target.exists():
        print(f"cd: no such file or directory: {target}")
        return
    if not target.is_dir():
        print(f"cd: not a directory: {target}")
        return

    _OLDPWD = Path.cwd()
    os.chdir(target)


def _cmd_ls(args: list[str]) -> None:    # Команда ls
    # "-a" - все файлы, включая скрытые
    # "-l" - подробный список (владелец, группа, дата создания, размер и др.)

    show_all = False
    long_format = False
    paths: list[Path] = []

    for a in args:
        if a.startswith("-"):
            show_all |= "a" in a
            long_format |= "l" in a
        else:
            paths.append(_change(a))

    if not paths:
        paths = [Path.cwd()]


    def prnt_entry(path: Path) -> None:
        if not long_format:
            print(path.name)
            return

        try:
            st = path.lstat()
            mode = filemode(st.st_mode)
            size = st.st_size
            mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(st.st_mtime))
            print(f"{mode} {size:>10} {mtime} {path.name}")
        except OSError as e:
            print(f"ls: error reading '{path}': {e}")


    def list_dir(dir: Path) -> None:
        if not dir.exists():
            print(f"ls: cannot access '{dir}': No such file or directory")
            return
        if dir.is_file():
            prnt_entry(dir)
            return

        try:
            items = sorted(dir.iterdir(), key=lambda x: x.name.lower())
        except PermissionError:
            print(f"ls: cannot open directory '{dir}': Permission denied")
            return

        for it in items:
            if not show_all and it.name.startswith("."):
                continue
            prnt_entry(it)


    for i, p in enumerate(paths):
        if len(paths) > 1:
            print(f"{p}:")
        list_dir(p)
        if i < len(paths) - 1:
            print()


def handle_command(cmd: str, args: list[str]) -> bool:
    if cmd == "exit":
        return True
    if cmd == "cd":
        _cmd_cd(args)
        return False
    if cmd == "ls":
        _cmd_ls(args)
        return False

    print(f"cmd: command not found: {cmd}")
    return False
