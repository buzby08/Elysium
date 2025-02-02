from __future__ import annotations
import argparse
import asyncio
import ctypes
import json
import os
import shutil
from PIL import Image, ImageTk #type: ignore - This is needed on Linux, but not Win32
import subprocess
import threading
from typing import Any, Callable
import sys

import customtkinter as ctk #type: ignore
import pyperclip #type: ignore

import errors
import files
from files import Path
import gui
import settings
import utils



def setup_parser(arguments: list[str], version: str) -> argparse.Namespace:
    """
    Creates a terminal argument parser based on the given CLI arguments.

    Args:
        arguments (list[str]): The CLI arguments to parse.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser_help: str = """
Elysium is a revolutionary organisational tool designed to streamline 
workflows and redefine productivity. By blending modern aesthetics with 
powerful functionality, Elysium offers an innovative approach to file 
and project management, perfect for users seeking structure and 
efficiency without compromising flexibility.
"""
    parser = argparse.ArgumentParser(description=parser_help)
    parser.add_argument(
        "-d",
        "--directory",
        help="The directory to start the app in.",
        default=None
    )
    parser.add_argument(
        "-p",
        "--project",
        help="The project start the app in. This is the projectID",
        default=0
    )
    parser.add_argument(
        "-w", 
        "--width", 
        help="Sets the width of the window",
        default=None
    )
    parser.add_argument(
        "-t", 
        "--height", 
        help="Sets the height of the window",
        default=None
    )
    parser.add_argument(
        "-x", 
        "--xCoord", 
        help="Sets the x coordinate of the window",
        default=200
    )
    parser.add_argument(
        "-y", 
        "--yCoord", 
        help="Sets the y coordinate of the window",
        default=100
    )
    parser.add_argument(
        "-v",
        "--version",
        help="Displays the current version of the app",
        action="version",
        version=version
    )
    args: argparse.Namespace = parser.parse_args(arguments)
    return args


def setup_app(parser: argparse.Namespace) -> gui.App:
    """Initialised the application"""
    app: gui.App = gui.App()
    screen_width: int = app.root.winfo_screenwidth()
    screen_height: int = app.root.winfo_screenheight()

    width: int = parser.width or int(screen_width * 0.8)
    height: int = parser.height or int(screen_height * 0.8)


    app.geometry = {
        "width": width,
        "height": height,
        "x": parser.xCoord,
        "y": parser.yCoord
    }

    return app


def get_settings(file_path: Path) -> settings.Settings:
    sett: settings.Settings = settings.Settings()

    
    with open(file_path, "r") as f:
        sett.parse_settings(json.load(f))
    
    return sett


def fetch_metadata(
    app: gui.App,
    file_path: str,
    callback: Callable[[gui.App, dict[str, str | Path | files.datetime | None]], Any]
) -> None:
    def worker():
        metadata_dict: dict[str, str | Path| files.datetime | None] = (
            files.get_file_metadata(Path(file_path))
        )
        callback(app, metadata_dict)

    thread = threading.Thread(target=worker)
    thread.start()


def display_details(button: gui.Button, app: gui.App) -> None:
    file_path: str = str(button.cget("text")) #type: ignore

    previously_selected: gui.Button | None = app.extra_details.get("selected")
    item_exists: bool = gui.widget_exists(previously_selected)
    if previously_selected and item_exists:
        previously_selected.configure(border_color="gray") #type: ignore
    
    if previously_selected is not button:
        hover_color = button.cget("hover_color") #type: ignore
        button.configure(border_color=hover_color) #type: ignore

        app.extra_details["selected"] = button

    for widget in app.details_bar.widgets[:]:
        app.details_bar.remove_widget(widget)
    
    file_path = os.path.join(app.file_path, file_path)
    fetch_metadata(app, file_path, _update_details_bar)


def open_folder(button: gui.Button, app: gui.App) -> None:
    file_path: Path = Path(button.cget("text")) #type: ignore
    full_file_path: Path = app.file_path + file_path
    

    app.file_path = full_file_path
    populate_files(app)


def open_file(button: gui.Button, app: gui.App) -> None:
    windows: bool = utils.platform() == "windows"
    macos: bool = utils.platform() == "darwin"

    button_file: Path = Path(button.cget("text")) #type: ignore
    file_path: Path = app.file_path + button_file

    if windows:
        os.startfile(file_path)
        return

    if macos:
        subprocess.call(("open", file_path))
        return

    subprocess.call(("xdg-open", file_path))


def get_files_elevated_permissions(app: gui.App) -> None:
    if sys.platform == "win32":
        # Relaunch on Windows
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv+[str(app.file_path)]), None, 1
        )

    else:
        app.main_section.add_widget(
            "warning_lbl",
            ctk.CTkLabel,
            text="This directory requires elevated permissions."
        )
        app.main_section.warning_lbl.pack(fill=ctk.X, side=ctk.TOP)

        errors.warn(
            app.root,
            "Permission Error",
            "This directory requires elevated permissions."
        )


def populate_files(app: gui.App, refresh: bool = False) -> None:   
    app.main_section.scroll_to_top()

    file_path: Path = app.file_path

    for widget in app.main_section.widgets[:]:
        app.main_section.remove_widget(widget)
    
    for widget in app.details_bar.widgets[:]:
        app.details_bar.remove_widget(widget)

    files_list: list[Path]
    folders: list[Path]

    if file_path in app.extra_details["directories"] and not refresh:
        files_list = app.extra_details["directories"][file_path]["files"]
        folders = (
            app.extra_details["directories"][file_path]["folders"]
        )
    
    else:
        files_list, folders = files.get_files_folders(file_path)
        app.extra_details["directories"][file_path] = {}
        app.extra_details["directories"][file_path]["folders"] = folders
        app.extra_details["directories"][file_path]["files"] = files_list


    for _, folder in enumerate(folders):
        app.main_section.add_button(gui.Button(
            "folder",
            app.main_section,
            single_click=lambda button, x, folder=folder: display_details(button, app),
            double_click=lambda button, x, folder=folder: open_folder(button, app),
            text=folder,
            border_width=1,
            border_color="gray",
            image=app.images["folder"],
            compound=ctk.LEFT,
            anchor="w"
        ))
        app.main_section.folder.pack(fill=ctk.X, padx=5)


    for _, file in enumerate(files_list):
        app.main_section.add_button(gui.Button(
            "file",
            app.main_section,
            single_click=lambda button, x, file=file: display_details(button, app),
            double_click=lambda button, x, file=file: open_file(button, app),
            text=file,
            border_width=1,
            border_color="gray",
            image=app.images["file"],
            compound=ctk.LEFT,
            anchor="w"
        ))
        app.main_section.file.pack(fill=ctk.X, padx=5)


def delete_item(app: gui.App, item: Path | None = None, no_confirm: bool = False) -> None:
    path: Path

    if not item:
        selected: Any | None = app.extra_details.get("selected")

        if not selected:
            return
        
        path = Path(selected.cget("text"))
        
        app.main_section.remove_widget(selected)

    path = item or path

    delete: bool = True

    if not no_confirm:
        delete = errors.confirm(app, "Delete", f"Do you want to delete {repr(path)}?")

    if not delete:
        populate_files(app)
        return
    
    if path.valid_dir() or files.get_file_type(path) == "Folder":
        errors.info(
            None,
            "Execution",
            "In 'folder' if statement"
        )
        try:
            shutil.rmtree((item or (app.file_path + path)).path)
            
            for item in app.details_bar.widgets:
                app.details_bar.remove_widget(item)
        except PermissionError:
            errors.warn(
                app,
                "Permission Error",
                f"{repr(path)} could not be deleted."
            )
            return
        
        try:
            app.extra_details["directories"][app.file_path]["folders"].remove(path)
        except: pass
        
        return

    try:
        os.remove(item or ((app.file_path + path).path))
    except PermissionError:
        errors.warn(
            app,
            "Permission Error",
            f"{repr(path)} could not be deleted."
        )
    try:
        app.extra_details["directories"][app.file_path]["files"].remove(path)
    except:
        pass
    for item in app.details_bar.widgets:
        app.details_bar.remove_widget(item)


def rename_item(app: gui.App) -> None:
    def execute_rename() -> None:
        new_path: Path = Path(app.main_section.renamed_file.get())
        new_full_path: Path = app.file_path + new_path

        overwrite: bool = False

        if os.path.exists(new_full_path):
            overwrite = errors.confirm(
                app.root,
                "Rename?",
                f"{repr(new_path)} already exists. Do you want to overwrite it?"
            )

        if os.path.exists(new_full_path) and overwrite:
            delete_item(app, new_full_path)

        try:
            os.rename(full_path, new_full_path)
        except OSError:
            populate_files(app)

        populate_files(app, refresh=True)


    app_path: Path = app.file_path
    selected_widget: Any | None = app.extra_details.get("selected")
    if not selected_widget:
        return
    
    selected_position = selected_widget.pack_info()
    
    item_path: Path = Path(selected_widget.cget("text"))
    full_path: Path = app_path + item_path



    app.main_section.remove_widget(selected_widget)
    app.main_section.add_widget("renamed_file", ctk.CTkEntry)
    app.main_section.renamed_file.pack(**selected_position)
    app.main_section.renamed_file.focus_set()
    app.main_section.renamed_file.bind("<FocusOut>", lambda x: execute_rename())
    app.main_section.renamed_file.bind("<Return>", lambda x: execute_rename())
    

def back_directory(app: gui.App) -> None:
    file_path: list[str] = app.file_path.as_list()

    new_fp: Path

    if len(file_path) != 1:
        new_fp = Path(file_path[:-1])
    elif (
        (file_path == ['/'] and utils.platform() != "windows")
        or utils.platform() == "windows"
    ):
        new_fp = Path()
    else:
        new_fp = Path('/')

    app.file_path = new_fp
    if "selected" in app.extra_details:
        del app.extra_details["selected"]
    populate_files(app)


def display_settings(app: gui.App, event: gui.tk.Event[Any]) -> None:
    def save_settings() -> None:
        color_mode: str = color_mode_toggle.get().lower()
        start_directory: str = str(start_directory_input.get())
        start_directory_path: Path = Path(start_directory)

        if (
            start_directory
            and start_directory_path.valid_dir()
        ):
            app.extra_details["settings"].start_directory = start_directory_path

        if color_mode != app.extra_details["settings"].color_mode:
            app.extra_details["settings"].color_mode = color_mode
            ctk.set_appearance_mode(color_mode)

        app.extra_details["settings"].save_settings(
            app.root_dir
            + Path("Settings")
            + Path("userSettings.json")
        )

        settings_window.destroy()


    settings_window: ctk.CTkToplevel = ctk.CTkToplevel(
        master=app.root,
        takefocus=True
    )

    settings_label: ctk.CTkLabel = ctk.CTkLabel(
        master=settings_window,
        text="Edit Settings Configuration"
    )

    save_button: ctk.CTkButton = ctk.CTkButton(
        master=settings_window,
        text="Save",
        command=save_settings
    )

    empty_item: ctk.CTkLabel = ctk.CTkLabel(master=settings_label, text="")

    color_mode_label: ctk.CTkLabel = ctk.CTkLabel(
        master=settings_window, 
        text="Color Mode"
    )

    color_mode_toggle: ctk.CTkComboBox = ctk.CTkComboBox(
        master=settings_window,
        values=["Light", "Dark", "System"]
    )
    color_mode_toggle.set(app.extra_details["settings"].color_mode.title())

    start_directory_label: ctk.CTkLabel = ctk.CTkLabel(
        master=settings_window,
        text="Start Directory"
    )
    start_directory_input: ctk.CTkEntry = ctk.CTkEntry(
        master=settings_window,
        placeholder_text=app.extra_details["settings"].start_directory
    )


    settings_label.grid(row=0, column=0, columnspan=4)
    save_button.grid(row=0, column=5)
    empty_item.grid(row=1, column=0, rowspan=2)
    color_mode_label.grid(row=3, column=0)
    color_mode_toggle.grid(row=3, column=1)
    start_directory_label.grid(row=4, column=0)
    start_directory_input.grid(row=4, column=1)


def new_file(app: gui.App, event: gui.tk.Event[Any]) -> None:
    def generate_new_file(event: gui.tk.Event[Any]) -> None:
        file_name: str = app.main_section.new_file.get()
        file_path: Path = Path(file_name)

        if files.get_file_type(file_path) == "Folder":
            os.mkdir(app.file_path + file_path)

        else:
            with open(app.file_path + file_path, "x") as f: f.close()

        app.main_section.remove_widget(app.main_section.new_file)
        app.root.bind("<BackSpace>", lambda x: back_directory(app))
        populate_files(app, refresh=True)

    app.main_section.scroll_to_top()


    app.main_section.add_widget("new_file", ctk.CTkEntry, placeholder_text="Input file name...")
    top_item = app.main_section.widgets[2]
    try:
        app.main_section.new_file.pack(side="top", before=top_item, fill="x")
    except:
        app.main_section.new_file.pack(side="top", fill="x")

    app.main_section.new_file.focus_set()

    app.main_section.new_file.bind("<FocusOut>", generate_new_file)
    app.main_section.new_file.bind("<Return>", generate_new_file)
    app.root.unbind("<BackSpace>")


def copy(app: gui.App, cut: bool = False) -> None:
    errors.info(
        None,
        "Execution",
        "copy() started"
    )
    app_path: Path = app.file_path

    selected: Any | None = app.extra_details.get("selected")
    if not selected:
        return
    
    selected_path: Path = Path(selected.cget("text"))
    full_path: Path = app_path + selected_path

    pyperclip.copy(str(full_path))

    app.extra_details["cut"] = cut


def paste(app: gui.App) -> None:
    errors.info(
        None,
        "Execution",
        "paste() started"
    )
    app_path: Path = app.file_path

    recent_copy: Path = Path(pyperclip.paste())
    cut: bool = app.extra_details.get("cut", False)

    if not (recent_copy.valid_dir() or recent_copy.valid_file()):
        return
    
    directory: Path
    file_ending: Path

    path_as_list: list[str] = recent_copy.as_list()
    directory = Path(path_as_list[:-1])
    file_ending = Path(path_as_list[-1])

    if recent_copy.valid_file():
        shutil.copy(recent_copy, app_path+file_ending)
    else:
        shutil.copytree(recent_copy, app_path+file_ending)

    populate_files(app, refresh=True)

    if cut:
        delete_item(app, recent_copy, no_confirm=True)
    
    if cut and recent_copy.valid_file():
        app.extra_details["directories"][str(directory)]["files"].remove(str(file_ending))
        return

    if cut and recent_copy.valid_dir():
        app.extra_details["directories"][str(directory)]["folders"].remove(str(file_ending))
        return


def _update_details_bar(
    app: gui.App,
    metadata_dict: dict[str, str | Path | files.datetime | None]
) -> None:
    owner: str | Path | files.datetime | None = metadata_dict.get("Owner")
    item_type: str | Path | files.datetime | None = metadata_dict.get("Item")
    modified_date: str | Path | files.datetime | None = metadata_dict.get("Last Modified")
    size: str | Path | files.datetime | None = metadata_dict.get("File Size")

    if isinstance(modified_date, files.datetime):
        modified_date = modified_date.strftime("%d-%m-%Y %H:%M:%S")
    for attr_name, attr_val in (
        ("Owner", owner),
        ("Item", item_type),
        ("Last modified", modified_date),
        ("File size", size)
    ):
        if not attr_val:
            continue
        app.details_bar.add_widget(
            "detail_name",
            ctk.CTkLabel,
            text=attr_name,
            fg_color="gray"
        )
        app.details_bar.add_widget(
            "detail_val",
            ctk.CTkLabel,
            text=f"  {attr_val}"
        )
        app.details_bar.detail_name.pack(side=ctk.TOP, fill=ctk.BOTH)
        app.details_bar.detail_val.pack(side=ctk.TOP, fill=ctk.BOTH)


async def main() -> None:
    """The main method for Elysium."""
    parser: argparse.Namespace = setup_parser(sys.argv[1:], "Elysium 1.2.2")

    app: gui.App = setup_app(parser)
    app.app_name = "Elysium"
    app.root_dir = Path()

    user_settings: settings.Settings = get_settings(
        app.root_dir
        + Path("Settings")
        + Path("userSettings.json")
    )

    app.file_path = user_settings.start_directory

    ctk.set_default_color_theme(str(user_settings.color_theme))
    ctk.set_appearance_mode(user_settings.color_mode)

    app.extra_details["settings"] = user_settings


    if utils.platform() != "windows":
        app.root.iconphoto(True, gui.tk.PhotoImage(str(Path(
            [str(app.root_dir), "Images", "ElysiumLogo.png"]
        ))))
    else:
        app.root.iconbitmap(
            Path([str(app.root_dir), "Images", "ElysiumLogo.ico"]).path
        )

    if parser.directory is not None and os.path.isdir(parser.directory):
        app.file_path = parser.directory

    app.add_image(
        "logo",
        Path([str(app.root_dir), "Images", "ElysiumLogo.png"]),
        size=(45, 45)
    )
    app.add_image(
        "new_file",
        Path([str(app.root_dir), "Images", "light", "new_file.png"]),
        Path([str(app.root_dir), "Images", "dark", "new_file.png"]),
        size=(25, 25)
    )
    app.add_image(
        "settings",
        Path([str(app.root_dir), "Images", "light", "settings.png"]),
        Path([str(app.root_dir), "Images", "dark", "settings.png"]),
        size=(25, 25)
    )
    app.add_image(
        "file",
        Path([str(app.root_dir), "Images", "light", "file.png"]),
        Path([str(app.root_dir), "Images", "dark", "file.png"])
    )
    app.add_image(
        "folder",
        Path([str(app.root_dir), "Images", "light", "folder.png"]),
        Path([str(app.root_dir), "Images", "dark", "folder.png"])
    )

    app.extra_details["directories"] = {
        "": {
            "files": [],
            "folders": files.get_drives()
        }
    }

    app.add_frame(gui.Frame(
        "title_bar",
        app.root,
        height=50,
        border_color="gray",
        border_width=1
    ))
    app.title_bar.pack_propagate(False)
    app.add_frame(gui.ScrollableFrame(
        "projects_bar",
        app.root,
        width=130,
        border_color="gray",
        border_width=1
    ))
    app.add_frame(gui.ScrollableFrame(
        "main_section",
        app.root,
        border_color="gray",
        border_width=1
    ))
    app.add_frame(gui.ScrollableFrame(
        "details_bar",
        app.root,
        width=130,
        border_color="gray",
        border_width=1
    ))

    
    app.title_bar.add_widget(
        "logo_lbl", 
        ctk.CTkLabel, 
        image=app.images["logo"], 
        text=""
    )
    app.title_bar.logo_lbl.pack(side=ctk.LEFT, padx=5)

    app.title_bar.add_widget(
        "app_name", 
        ctk.CTkLabel, 
        text="Elysium", 
        font=("Arial", 20)
    )
    app.title_bar.app_name.pack(side=ctk.LEFT, padx=10)

    app.title_bar.add_widget("search", ctk.CTkLabel, text=app.file_path)
    app.title_bar.search.pack(side=ctk.LEFT, padx=10, fill=ctk.X)
    app.display_fp_widget = app.title_bar.search

    app.title_bar.add_button(gui.Button(
        "settings_btn",
        app.title_bar,
        single_click=lambda button, event: display_settings(app, event),
        color="transparent",
        image=app.images["settings"],
        text="",
        width=20,
    ))
    app.title_bar.settings_btn.pack(side=ctk.RIGHT, padx=5)

    app.title_bar.add_button(gui.Button(
        "new_file_btn",
        app.title_bar,
        single_click=lambda button, event: new_file(app, event),
        color="transparent",
        image=app.images["new_file"],
        text="",
        width=20,
    ))
    app.title_bar.new_file_btn.pack(side=ctk.RIGHT, padx=5)

    app.projects_bar.add_widget("title", ctk.CTkLabel, text="PROJECTS")
    app.projects_bar.title.pack(side=ctk.TOP)

    app.projects_bar.add_widget("separator", ctk.CTkFrame, height=2, fg_color="gray")
    app.projects_bar.separator.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)
    
    app.projects_bar.add_button(gui.Button(
        "color_mode_btn",
        app.projects_bar,
        single_click=lambda button, event: app.toggle_light_mode(),
        text="Switch"
    ))
    app.projects_bar.color_mode_btn.pack(side=ctk.LEFT)

    app.main_section.add_widget("title", ctk.CTkLabel, text="FILES")
    app.main_section.block_deletion(app.main_section.title)
    app.main_section.title.pack(side=ctk.TOP)

    app.main_section.add_widget("separator", ctk.CTkFrame, height=2, fg_color="gray")
    app.main_section.block_deletion(app.main_section.separator)
    app.main_section.separator.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)

    app.details_bar.add_widget("title", ctk.CTkLabel, text="DETAILS")
    app.details_bar.title.pack(side=ctk.TOP)
    app.details_bar.block_deletion(app.details_bar.title)

    app.details_bar.add_widget("separator", ctk.CTkFrame, height=2, fg_color="gray")
    app.details_bar.separator.pack(side=ctk.TOP, fill=ctk.X, padx=10, pady=10)
    app.details_bar.block_deletion(app.details_bar.separator)


    app.title_bar.pack(side=ctk.TOP, fill=ctk.X)
    app.main_section.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
    app.details_bar.pack(side=ctk.LEFT, fill=ctk.Y)


    app.root.bind("<BackSpace>", lambda x: back_directory(app))
    app.root.bind("<Control-r>", lambda x: populate_files(app, refresh=True))
    app.root.bind("<F5>", lambda x: populate_files(app, refresh=True))
    app.root.bind("<Delete>", lambda event: delete_item(app))
    app.root.bind("<F2>", lambda event: rename_item(app))
    app.root.bind("<Control-c>", lambda event: copy(app))
    app.root.bind("<Control-x>", lambda event: copy(app, cut=True))
    app.root.bind("<Control-v>", lambda event: paste(app))

    populate_files(app)

    app.run()

    return None


if __name__ == "__main__":
    asyncio.run(main())