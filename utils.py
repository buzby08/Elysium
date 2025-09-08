from functools import cache
import platform as pform
import shutil
import subprocess
import screeninfo

import errors

@cache
def platform() -> str:
    """Returns the lowercase platform name for the system"""
    return pform.system().lower()

def get_primary_monitor() -> screeninfo.Monitor:
    monitors: list[screeninfo.Monitor] = screeninfo.get_monitors()
    for m in monitors:
        if getattr(m, "is_primary", False):
            return m
        
    for m in monitors:
        monitor_is_at_center: bool = m.x == 0 and m.y == 0

        if monitor_is_at_center: return m

    fallback: screeninfo.Monitor = monitors[0]
    return fallback


@cache
def is_windows() -> bool:
    return platform() == "windows"


@cache
def is_darwin() -> bool:
    return platform() == "darwin"


@cache
def is_linux() -> bool:
    return not (is_windows() or is_darwin())


def open_terminal_mac(directory: str) -> None:
    subprocess.Popen([
        "oascript", "-e",
        f'''tell application "Terminal"
            activate
            do script "cd '{directory}'"
        end tell'''
    ])


def open_terminal_win(directory: str) -> None:
    subprocess.Popen([
        "powershell.exe", "-NoExit", "-Command",
        f"Set-Location -Path '{directory}'"
    ])


def open_terminal_linux(directory: str) -> None:
    terminals: list[list[str]] = [
        ["x-terminal-emulator", "--working-directory", directory],
        ["gnome-terminal", "--working-directory", directory],
        ["kgx", "--working-directory", directory],
        ["konsole", "--workdir", directory],
        ["xfce4-terminal", "--working-directory", directory],
        ["xterm", "-e", f"cd {directory}; bash"]
    ]

    for terminal in terminals:
        try:
            errors.info(
                root=None,
                title="Terminal open attempt",
                message=f"Attempting to open terminal using command {terminal}"
            )
            subprocess.Popen(terminal)
            errors.info(None, title="Terminal open attempt", message="Success")
            break
        except FileNotFoundError:
            continue


def open_terminal(directory: str) -> None:
    if is_windows(): 
        open_terminal_win(directory)
        return

    if is_darwin(): 
        open_terminal_mac(directory)
        return
    
    if is_linux():
        open_terminal_linux(directory)
        return
    
    raise OSError("Could not find a suitable operating system")