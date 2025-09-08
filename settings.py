import json
import os
from typing import Any, cast

import errors
from files import fix_path, Path



class File_Association:
    def __init__(self) -> None:
        self.__name__: str = "File_Association"
        return None
    
    def parse_dict(self, obj: dict[str, str]) -> None:
        for key, value in obj.items():
            self.__setattr__(key, value)
    
    def __getattr__(self, name: str) -> Any:
        return "Attr does not exist"

    def __str__(self) -> str:
        result: str = ""
        for key, value in self.__dict__.items():
            if key == "__name__": continue

            result += f"@{self.__name__} - {key}: {value}\n"

        return result
    

class File_Extensions:
    def __init__(self) -> None:
        self.__name__: str = "File_Extensions"
        return None
    
    def parse_dict(self, obj: dict[str, str|list[str]]) -> None:
        for key, value in obj.items():
            string_value: str | list[str] = value

            if isinstance(value, list):
                string_value = os.path.join(*value)

            self.__setattr__(key, string_value)

    def __str__(self) -> str:
        result: str = ""
        for key, value in self.__dict__.items():
            if key == "__name__": continue
            
            result += f"@{self.__name__} - {key}: {value}\n"

        return result


class AI_Rules:
    def __init__(self) -> None:
        self.__name__: str = "AI_Rules"

        self.file_extensions: File_Extensions = File_Extensions()
        self._global_folders: list[str] = []
        self.sort_on_close: bool = False

    @property
    def global_folders(self) -> list[str]:
        return self._global_folders
    
    @global_folders.setter
    def global_folders(self, value: list[list[str]]) -> None:
        self._global_folders = []
        error: bool = False

        for item in value:
            path: str = os.path.join(*item)
            if not os.path.isdir(path):
                error = True
                continue

            self._global_folders.append(path)
        
        if error:
            errors.warn(
                None,
                "Invalid item",
                "One or more values given were not found, "
                + "or were not directories."
            )
        
    @global_folders.deleter
    def global_folders(self) -> None:
        del self._global_folders

    def __str__(self) -> str:
        result: str = ""
        for key, value in self.__dict__.items():
            if key == "__name__": continue
            
            result += f"@{self.__name__} - {key}: {value}\n"

        return result
            


class Settings:
    def __init__(self) -> None:
        self.__name__: str = "Settings"

        self._color_mode: str = "dark"
        self._color_theme: Path = Path("Themes") + Path("widgetTheme.json")
        self._start_directory: Path = Path()
        self._recent_files: list[Path] = []
        self.file_association: File_Association = File_Association()
        self.global_ai_rules: AI_Rules = AI_Rules()
        self.local_ai_rules: AI_Rules = AI_Rules()

        del self.local_ai_rules.global_folders
        del self.local_ai_rules.sort_on_close

    def parse_settings(self, obj: dict[str, Any]) -> None:
        self.color_mode = obj.get("colorMode", self.color_mode)
        self.color_theme = obj.get("colorTheme", self.color_theme)
        self.start_directory = obj.get("startDirectory", self.start_directory)
        self.recent_files = obj.get("recentFiles", self.recent_files)
        self.file_association.parse_dict(obj.get("fileAssociation", {}))
        
        global_ai_rules = obj.get("globalAIRules", {})
        global_file_extensions = global_ai_rules.get("fileExtensions", {})
        global_folders = global_ai_rules.get("globalFolders", [])
        global_sort_on_close = global_ai_rules.get("sortOnClose", False)

        local_file_rules = obj.get("localAIRules", {}).get("fileExtensions", []) or global_file_extensions

        self.global_ai_rules.global_folders = global_folders
        self.global_ai_rules.sort_on_close = global_sort_on_close
        self.global_ai_rules.file_extensions.parse_dict(global_file_extensions)

        self.local_ai_rules.file_extensions.parse_dict(local_file_rules)

        errors.info(None, "", "Parsed successfully")

    def save_settings(self, file_path: str | Path) -> None:
        with open(file_path, "r") as f:
            old_settings: dict[str, Any] = json.load(f)

        old_settings["colorMode"] = self.color_mode
        old_settings["colorTheme"] = self.color_theme.path
        old_settings["startDirectory"] = self.start_directory.path
        old_settings["recentFiles"] = [x.path for x in self.recent_files]

        with open(file_path, 'w') as f:
            json.dump(old_settings, f)

    @property
    def color_mode(self) -> str:
        return self._color_mode
    
    @color_mode.setter
    def color_mode(self, value: str) -> None:
        if not value.strip().lower() in ("light", "dark", "system"):
            errors.warn(
                None,
                "Value Error",
                "Color mode must be either 'light', 'dark', or 'system'."
            )
            self._color_mode = "system"
            return

        self._color_mode = value.strip().lower()
    
    @property
    def color_theme(self) -> Path:
        return self._color_theme
    
    @color_theme.setter
    def color_theme(self, value: Path | str | list[str]) -> None:
        if isinstance(value, str) or isinstance(value, list):
            value = Path(value)
            
        if not value.valid_file() and not value.startswith("_internal"):
            self.color_theme = Path("_internal") + value
        
        elif not value.valid_file():
            errors.warn(
                None,
                "File Not Found",
                f"{repr(value)} does not1 exist, and could not be found"
            )
            return

        self._color_theme = value

    @property
    def start_directory(self) -> Path:
        return self._start_directory
    
    @start_directory.setter
    def start_directory(self, value: Path | str | list[str]) -> None:
        if isinstance(value, str) or isinstance(value, list):
            value = Path(value)

        if not value.valid_dir():
            errors.warn(
                None,
                "Not A Directory error",
                "start_directory expects a directory! "
                + f"{repr(value)} does not match!"
            )
            return

        self._start_directory = fix_path(value)

    @property
    def recent_files(self) -> list[Path]:
        return self._recent_files
    
    @recent_files.setter
    def recent_files(self, value: list[Path | str | list[str]]) -> None:
        for i, item in enumerate(value):
            if isinstance(item, str) or isinstance(item, list):
                value[i] = Path(item)

        error: bool = False

        for item in value:
            if not cast(Path, item).valid_file():
                error = True
        
        if error:
            errors.warn(
                None,
                "File not found",
                "One or more values given were not found, "
                + "or were not files."
            )
        self._recent_files = [Path(x) for x in value if isinstance(x, str)]

    def __str__(self) -> str:
        result: str = ""
        for key, value in self.__dict__.items():
            if key == "__name__": continue
            
            result += f"@{self.__name__} - {key}: {value}\n"

        return result