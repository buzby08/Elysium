from __future__ import annotations
import os


import errors
from files import Path


class ProjectPath(Path):
    def __init__(
        self,
        path: str | list[str] | None = None
    ) -> None:
        path = path or ""

        self._separator: str = '/'

        if isinstance(path, list):
            while '' in path:
                path.remove('')
            path = self._separator.join(path)

        self._path: str = "src" + self._separator + path

        del self.list_items

    def split(self, sep: str | None = None) -> tuple[ProjectPath, ...]:
        sep = sep or self._separator

        items: list[str] = self.path.split(sep)

        return tuple(ProjectPath(item) for item in items)
    
    def valid_file(self) -> bool:
        extension: str
        _, extension = os.path.splitext(self.path)

        return bool(extension)
    
    def valid_dir(self) -> bool:
        return not self.valid_file()



class Details:
    def __init__(self) -> None:
        self._name: str = "Undefined"
        self._description: str | None = None
        self._version: str = "Undefined"
        self._created: str = "Undefined"
        self._modified: str = "Undefined"
        self._owner: str = "Undefined"

    def parse(self, section: list[str]) -> None:
        for line in section:
            keyword: str = line.split(':')[0].strip()
            value: str = line.removeprefix(keyword + ':')

            match keyword:
                c

                case _:
                    errors.warn(
                        None,
                        "Invalid Keyword",
                        (
                            f"{repr(keyword)} is not a valid keyword for "
                            + "the Details section of a project file."
                        )
                    )

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the name parameter.")

        self._name = value

    @property
    def description(self) -> str | None:
        return self._description

    @description.setter
    def description(self, value: str | None) -> None:
        if value is None:
            self._description = None
            return

        self._description = _apply_format(value) or None

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the version parameter.")

        self._version = value

    @property
    def created(self) -> str:
        return self._created

    @created.setter
    def created(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the created parameter.")

        self._created = value

    @property
    def modified(self) -> str:
        return self._name

    @modified.setter
    def modified(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the modified parameter.")

        self.modified = value

    @property
    def owner(self) -> str:
        return self._owner

    @owner.setter
    def owner(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the owner parameter.")

        self._owner = value



class Assets:
    def __init__(self) -> None:
        self._files: dict[ProjectPath, Path] = {}

        self._items: dict[str, ProjectPath] = {}
        self._sorted: list[ProjectPath] = []

    def add_file(self, file_path: Path, local_path: ProjectPath) -> None:
        if not file_path.valid_file():
            raise FileNotFoundError("'file_path' must be a file!")

        if not local_path.valid_file():
            raise FileNotFoundError("'local_path' must be a file!")

        self._files[local_path] = file_path
        self._items[local_path.path] = local_path
        self._sorted = sorted(self._items.values(), key=lambda x: x.path)

    def delete_file(self, path: ProjectPath) -> None:
        if path in self._files:
            del self._files[path]

        if path.path in self._items:
            del self._items[path.path]

        if path in self._sorted:
            self._sorted.remove(path)

    def add_folder(self, file_path: Path) -> None:
        if not file_path.valid_dir():
            raise FileNotFoundError("'file_path' must be a directory!")

        items: tuple[Path, ...] = file_path.list_items()

        for item in items:
            project_item_path: str = item.path.removeprefix(file_path.path)
            local_path: ProjectPath = ProjectPath(
                project_item_path.split(file_path.separator)
            )

            self._files[local_path] = file_path
            self._items[local_path.path] = local_path
        

        self._sorted = sorted(self._items.values(), key=lambda x: x.path)

    def delete_folder(self, file_path: Path) -> None:
        if not file_path.valid_dir():
            raise FileNotFoundError("'file_path' must be a directory!")
        
        items: tuple[Path, ...] = file_path.list_items()

        for item in items:
            project_item_path: str = item.path.removeprefix(file_path.path)
            local_path: ProjectPath = ProjectPath(
                project_item_path.split(file_path.separator)
            )
            
            self.delete_file(local_path)

    @property
    def files(self) -> dict[ProjectPath, Path]:
        return self._files



class Settings:
    def __init__(self) -> None:
        self._save_path: str = ""
        self._pre_run_script: tuple[str, str] = ('', '')
        self._post_run_script: tuple[str, str] = ('', '')

    def parse(self, section: list[str]) -> None:
        for line in section:
            keyword: str = line.split(':')[0].strip()
            value: str = line.removeprefix(keyword + ':')

            match keyword:
                case "SavePath":
                    self.save_path = value

                case "PreRunScript":
                    value1: str
                    value2: str
                    value1, value2 = value.split(':')
                    
                    value1 += ':'

                    self.pre_run_script = (value1, value2)

                case "PostRunScript":
                    value1: str
                    value2: str
                    value1, value2 = value.split(':')
                    
                    value1 += ':'

                    self.post_run_script = (value1, value2)
                
                case _:
                    ...

    @property
    def save_path(self) -> str:
        return self._save_path
    
    @save_path.setter
    def save_path(self, value: str) -> None:
        value = _apply_format(value)
        if value == "" or value == "Undefined":
            raise ValueError("You must provide a value for the save_path parameter.")
        
        self._save_path = value

    @property
    def pre_run_script(self) -> str:
        return ' '.join(self._pre_run_script)
    
    @pre_run_script.setter
    def pre_run_script(self, value: tuple[str, str]) -> None:
        self._pre_run_script = value

    @property
    def post_run_script(self) -> str:
        return ' '.join(self._post_run_script)
    
    @post_run_script.setter
    def post_run_script(self, value: tuple[str, str]) -> None:
        self._post_run_script = value



class Dependencies:
    def __init__(self) -> None:
        self.all: list[str] = []

    def parse(self, section: list[str]) -> list[Exception]:
        errors: list[Exception] = []

        for item in section:
            try:
                dependency: str = _apply_format(item)
            except Exception as e:
                errors.append(e)
                continue
            
            self.all.append(dependency)

        return errors


class Languages:
    def __init__(self) -> None:
        self._main: tuple[str, str] = ('', '')
        self._others: list[tuple[str, str]] = []

    def add_language(
        self,
        name: str,
        version: str,
        main: bool = False
    ) -> None:
        if not main:
            self._others.append((name, version))
            return
        
        self._others.append(self._main)
        self._main = (name, version)

    def remove_language(self, name: str) -> None:
        if self._main[0] == name:
            raise ValueError(
                "Cannot delete main language. Please override it using "
                "add_language instead."
            )
        
        for item in self._others:
            if item[0] == name:
                self._others.remove(item)
                return
            
        raise ModuleNotFoundError(f"The language {repr(name)} was not found.")
    
    def parse(self, section: list[str]) -> list[Exception]:
        errors: list[Exception] = []


        main: bool = False
        for item in section:
            if " :" not in item and ';' not in item:
                errors.append(ValueError(
                    f"Language {repr(item)} is missing the key "
                    "separators: ' :' and ';'."
                ))

            split_item: list[str] = item.split(" :")
            
            language_name: str = _apply_format(split_item[0]+" :")
            language_version: str = _apply_format(split_item[1])

            if language_name.startswith("(Main)"):
                main = True
                language_name = language_name.removeprefix("(Main)").lstrip()

            self.add_language(language_name, language_version, main)

        return errors


    @property
    def main(self) -> tuple[str, str]:
        return self._main
    
    @property
    def others(self) -> list[tuple[str, str]]:
        return self._others



class Project:
    def __init__(
        self,
        file_path: str,
        details: Details | None = None,
        assets: Assets | None = None,
        settings: Settings | None = None,
        dependencies: Dependencies | None = None,
        languages: Languages | None = None
    ) -> None:
        self._file_path: str = file_path
        self.details: Details = details or Details()
        self.assets: Assets = assets or Assets()
        self.settings: Settings = settings or Settings()
        self.dependencies: Dependencies = dependencies or Dependencies()
        self.languages: Languages = languages or Languages()

    @property
    def file_path(self) -> str:
        return self._file_path



def _apply_format(item: str) -> str:
    """
    Applies the default format for all values in the project.
    This removes any whitespace, and the trailing colon or semi-colon.

    Args:
        item (str): The item to format.

    Returns:
        str: The formatted item.

    Raises:
        TypeError: The item is not a string.
    """
    if not isinstance(item, str): #type: ignore
        raise TypeError(
            f"_apply_format expects a string, not {type(item)}."
        )
    item = item.rstrip()

    if not (item.endswith(';') or item.endswith(" :")):
        errors.error(
            root=None,
            title="Value Error",
            message=(
                "The value does not match the default format.\n"
                "The item must end with ' :' or ';' - "
                f"{repr(item)} does not match this format."
            )
        )
        return item.strip()
    

    if item.endswith(" :"):
        item = item.replace(" :", '')
    if item.endswith(';'):
        item = item.replace(';', '')

    return item.strip()