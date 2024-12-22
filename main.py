from __future__ import annotations
import argparse
import ctypes
import json
import os
import subprocess
import threading
from typing import Any, Callable
import sys

import customtkinter as ctk #type: ignore

import files
import gui
import settings



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
        default=1000
    )
    parser.add_argument(
        "-t", 
        "--height", 
        help="Sets the height of the window",
        default=500
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

    app.geometry = {
        "width": parser.width,
        "height": parser.height,
        "x": parser.xCoord,
        "y": parser.yCoord
    }

    return app


def get_settings(file_path: str) -> settings.Settings:
    sett: settings.Settings = settings.Settings()
    
    with open(file_path, "r") as f:
        sett.parse_settings(json.load(f))
    
    return sett


def fetch_metadata(
    app: gui.App,
    file_path: str,
    callback: Callable[[gui.App, dict[str, str | files.datetime | None]], Any]
) -> None:
    def worker():
        metadata_dict: dict[str, str | files.datetime | None] = (
            files.get_file_metadata(file_path)
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
    file_path: str = str(button.cget("text")) #type: ignore
    full_file_path: str = os.path.join(app.file_path, file_path)

    app.file_path = full_file_path
    populate_files(app)


def open_file(button: gui.Button, app: gui.App) -> None:
    windows: bool = settings.platform() == "windows"
    macos: bool = settings.platform() == "darwin"

    button_file: str = str(button.cget("text")) #type: ignore
    file_path: str = os.path.join(app.file_path, button_file)

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
            None, "runas", sys.executable, " ".join(sys.argv+[app.file_path]), None, 1
        )

    else:
        app.main_section.add_widget(
            "warning_lbl",
            ctk.CTkLabel,
            text="This directory requires elevated permissions."
        )
        app.main_section.warning_lbl.pack(fill=ctk.X, side=ctk.TOP)


def populate_files(app: gui.App, refresh: bool = False) -> None:   
    app.main_section.scroll_to_top()
    file_path: str = app.file_path

    for widget in app.main_section.widgets[:]:
        app.main_section.remove_widget(widget)
    
    for widget in app.details_bar.widgets[:]:
        app.details_bar.remove_widget(widget)

    files_list: list[str]
    folders: list[str]

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


def back_directory(app: gui.App) -> None:
    red = "\u001b[31m"
    norm = "\u001b[0m"
    file_path: list[str] = app.file_path.split('\\')
    print(f"{red}current_file_path: {repr(str(file_path))}{norm}")
    while '' in file_path:
        file_path.remove('')

    if len(file_path) != 1:
        new_fp: str = '\\'.join(file_path[:-1])
    else:
        new_fp: str = ""
    app.file_path = new_fp
    print(f"{red}new_file_path: {repr(str(new_fp))}{norm}")
    print(f"{red}app file path: {repr(app.file_path)}{norm}")
    if "selected" in app.extra_details:
        del app.extra_details["selected"]
    populate_files(app)


def display_settings(event: gui.tk.Event[Any]) -> None:
    raise NotImplementedError


def new_file(event: gui.tk.Event[Any]) -> None:
    raise NotImplementedError


def open_share_menu(file_path: str) -> None:
    # Use the Windows explorer.exe shell to show the sharing UI
    subprocess.run(["explorer", "/select,", file_path], shell=True)


def _update_details_bar(
    app: gui.App,
    metadata_dict: dict[str, str | files.datetime | None]
) -> None:
    owner: str | files.datetime | None = metadata_dict.get("Owner")
    item_type: str | files.datetime | None = metadata_dict.get("Item")
    modified_date: str | files.datetime | None = metadata_dict.get("Last Modified")
    size: str | files.datetime | None = metadata_dict.get("File Size")

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


def main() -> None:
    parser: argparse.Namespace = setup_parser(sys.argv[1:], "Elysium 1.1.2")

    app: gui.App = setup_app(parser)
    app.app_name = "Elysium"
    app.root_dir = "_internal"

    user_settings: settings.Settings = get_settings(os.path.join(app.root_dir, "Settings", "userSettings.json"))

    app.file_path = user_settings.start_directory

    ctk.set_default_color_theme(user_settings.color_theme)
    ctk.set_appearance_mode(user_settings.color_mode)


    app.root.iconbitmap(f"{app.root_dir}\\Images\\ElysiumLogo.ico") # type: ignore

    if parser.directory is not None and os.path.isdir(parser.directory):
        app.file_path = parser.directory

    app.add_image(
        "logo",
        f"{app.root_dir}\\Images\\ElysiumLogo.png",
        size=(45, 45)
    )
    app.add_image(
        "new_file",
        f"{app.root_dir}\\Images\\light\\new_file.png",
        f"{app.root_dir}\\Images\\dark\\new_file.png",
        size=(25, 25)
    )
    app.add_image(
        "settings",
        f"{app.root_dir}\\Images\\light\\settings.png",
        f"{app.root_dir}\\Images\\dark\\settings.png",
        size=(25, 25)
    )
    app.add_image(
        "file",
        f"{app.root_dir}\\Images\\light\\file.png",
        f"{app.root_dir}\\Images\\dark\\file.png"
    )
    app.add_image(
        "folder",
        f"{app.root_dir}\\Images\\light\\folder.png",
        f"{app.root_dir}\\Images\\dark\\folder.png"
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
        single_click=lambda button, event: display_settings(event),
        color="transparent",
        image=app.images["settings"],
        text="",
        width=20,
    ))
    app.title_bar.settings_btn.pack(side=ctk.RIGHT, padx=5)

    app.title_bar.add_button(gui.Button(
        "new_file_btn",
        app.title_bar,
        single_click=lambda button, event: new_file(event),
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
    
    populate_files(app)

    app.run()

    return None


if __name__ == "__main__":
    main()