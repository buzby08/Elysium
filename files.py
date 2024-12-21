from genericpath import isfile
import os
import platform
import subprocess
import psutil
import windows_metadata




def get_drives() -> list[str]:
    """Returns the path of all drives mounted on the current system."""
    return [x.mountpoint for x in psutil.disk_partitions(all=True)]


def get_platform() -> str:
    """Returns the current os name: windows, darwin, other (for linux)"""
    return platform.system().lower()


def get_folders(cwd: str) -> list[str]:
    """
    Returns all the folders in the given file path.

    Args:
        cwd (str): The file path to find folders from

    Raises:
        FileNotFoundError: When `cwd` is not a valid directory

    Returns:
        list[str]: A list of the directories (their full paths)
    """
    if cwd == '':
        return get_drives()
    
    if not os.path.isdir(cwd):
        raise FileNotFoundError(
            f"'{cwd}' is not a valid directory.")
    
    folders: list[str] = []
    for item in os.listdir(cwd):
        split_item = item.split('.')
        if len(split_item) <= 1 or item.startswith('.'):
            folders.append(os.path.join(cwd, item))
    
    return folders


def get_files_folders(file_path: str) -> tuple[list[str], list[str]]:
    items: list[str] = os.listdir(file_path)

    files: list[str] = []
    folders: list[str] = []

    for item in items:
        full_path: str = os.path.join(file_path, item)
        if os.path.isfile(full_path):
            files.append(item)
            continue
            
        folders.append(item)

    return (sorted(files, key=str.casefold), sorted(folders, key=str.casefold))
