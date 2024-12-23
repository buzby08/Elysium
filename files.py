from datetime import datetime
from functools import cache
import os
from pprint import pprint
from typing import Any, Union
import psutil

import settings

if settings.platform() == "windows":
    import win32security
else:
    import pwd


def get_drives() -> list[str]:
    """Returns the path of all drives mounted on the current system."""
    print("got drives")
    return [x.mountpoint for x in psutil.disk_partitions(all=True)]


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
    """
    Gets all the files and folders in a given directory.

    Args:
        file_path (str): The directory to check.

    Returns:
        tuple[list[str], list[str]]: A tuple containing two lists, one
            containing all folders, and one containing all files. This
            is in the format (FILES, FOLDERS).
    """
    items: list[str] = get_drives() if file_path == '' else os.listdir(file_path)
    
    pprint(items)

    files: list[str] = []
    folders: list[str] = []

    for item in items:
        full_path: str = os.path.join(file_path, item)
        if os.path.isfile(full_path):
            files.append(item)
            continue
            
        folders.append(item)

    return (sorted(files, key=str.casefold), sorted(folders, key=str.casefold))


def get_file_metadata(file_path: str) -> dict[str, Union[str, datetime, None]]:
    """
    Retrieve metadata for a single file or folder.

    Args:
        file_path (str): Path to the file or folder.

    Returns:
        dict: Metadata dictionary containing owner, last modified time, and file size.
    """
    try:
        file_stats: os.stat_result = os.stat(file_path)
        owner: str = (
            _get_windows_owner(file_path) 
            if settings.platform() == "windows" 
            else _get_unix_owner(file_stats)
        )

        

        metadata: dict[str, Union[str, datetime, None]] = {
            "Path": file_path,
            "Owner": owner,
            "Last Modified": datetime.fromtimestamp(file_stats.st_mtime),
            "File Size": (
                format_size(file_stats.st_size) 
                if not os.path.isdir(file_path) 
                else None
            ),
            "Item": get_file_type(file_path),
        }

        return metadata
    
    except FileNotFoundError:
        return {"Error": f"File not found: {file_path}"}
    
    except Exception as e:
        return {"Error": str(e)}
    

def format_size(size: int | float) -> str:
    """
    Convert a file size from bytes to a human-readable format.

    Args:
        size (int): The file size in bytes.

    Returns:
        str: The file size as a formatted string.
    """
    units: list[str] = ["B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB"]
    for unit in units:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} {units[-1]}"


def _get_windows_owner(file_path: str) -> str:
        """Get the owner of a file or folder on Windows."""
        try:
            owner_sid: Any
            owner: str
            _: Any
            
            security_descriptor: Any = (
                win32security.GetFileSecurity( #type: ignore
                    file_path,
                    win32security.OWNER_SECURITY_INFORMATION #type: ignore
                )
            )
            owner_sid = security_descriptor.GetSecurityDescriptorOwner()

            owner, _,  _ =   win32security.LookupAccountSid( #type: ignore
                None, #type: ignore
                owner_sid
            )  
            return owner
        except Exception as e:
            print(e)
            return "Unknown Owner"
        

def _get_unix_owner(file_stats: os.stat_result) -> str:
        """Get the owner of a file or folder on Unix-like systems."""
        try:
            return pwd.getpwuid(file_stats.st_uid).pw_name #type: ignore
        except KeyError:
            return "Unknown Owner"


@cache
def get_file_type(file_path: str) -> str:
    extension: str
    _, extension = os.path.splitext(file_path)
    if os.path.isdir(file_path): extension = "Folder"

    return extension



if __name__ == "__main__":
    get_file_metadata(r"E:\file explorer\gui.py")