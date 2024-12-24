from __future__ import annotations
import os
import tkinter as tk
from typing import Any, Callable
from PIL import Image

from PIL.ImageFile import ImageFile
import customtkinter as ctk #type: ignore

import files



class Frame(ctk.CTkFrame):
    def __init__(
        self, 
        widget_name: str, 
        master: ctk.CTk | ctk.CTkToplevel,
        **kwargs: Any
        ) -> None:
        kwargs["master"] = master
        self._widgets: list[ctk.CTkBaseClass] = []
        self.__name__: str = widget_name
        super().__init__(**kwargs) #type: ignore

    def add_frame(
        self,
        frame: 'Frame'
    ) -> None:
        self.__setattr__(frame.__name__, frame)

    def add_widget(
        self, 
        name: str, 
        widget_object: type[ctk.CTkBaseClass],
        **kwargs: Any
    ) -> None:
        """
        Adds a widget to the application.

        Args:
            name (str): The name of the widget. Can then be accessed
                by `app.{name}`
            widget_object (type[ctk.CTkBaseClass]): The widget object, 
                e.g. ctk.CTkLabel. This is the uninitialised class.
            **kwargs (Any): The arguments you pass when initialising
                the widget outside of the app.
        """
        kwargs["master"] = self
        widget: ctk.CTkBaseClass = widget_object(**kwargs)
        self._widgets.append(widget)
        setattr(self, name, widget)

    def add_button(
        self,
        button: Button
    ) -> None:
        self._widgets.append(button)
        setattr(self, button.widget_name, button)

    def block_deletion(self, widget: ctk.CTkBaseClass) -> None:
        widget.__dict__["protected"] = True

    def remove_widget(self, widget: ctk.CTkBaseClass) -> None:
        if widget.__dict__.get("protected", False):
            print(f"Cannot delete {widget}")
            return
        
        self._widgets.remove(widget)
        widget.destroy()

    @property
    def widgets(self) -> list[ctk.CTkBaseClass]:
        return self._widgets
    


class ScrollableFrame(ctk.CTkScrollableFrame):
    def __init__(
        self, 
        widget_name: str, 
        master: ctk.CTk | ctk.CTkToplevel,
        **kwargs: Any
        ) -> None:
        kwargs["master"] = master
        self._widgets: list[ctk.CTkBaseClass] = []

        self.__name__: str = widget_name
        super().__init__(**kwargs) #type: ignore

    def add_frame(
        self,
        frame: 'Frame'
    ) -> None:
        self.__setattr__(frame.__name__, frame)

    def add_widget(
        self, 
        name: str, 
        widget_object: type[ctk.CTkBaseClass],
        **kwargs: Any
    ) -> None:
        """
        Adds a widget to the application.

        Args:
            name (str): The name of the widget. Can then be accessed
                by `app.{name}`
            widget_object (type[ctk.CTkBaseClass]): The widget object, 
                e.g. ctk.CTkLabel. This is the uninitialised class.
            **kwargs (Any): The arguments you pass when initialising
                the widget outside of the app.
        """
        kwargs["master"] = self
        widget: ctk.CTkBaseClass = widget_object(**kwargs)
        self._widgets.append(widget)
        setattr(self, name, widget)
    
    def add_button(
        self,
        button: Button
    ) -> None:
        self._widgets.append(button)
        setattr(self, button.widget_name, button)

    def block_deletion(self, widget: ctk.CTkBaseClass) -> None:
        widget.__dict__["protected"] = True

    def remove_widget(self, widget: ctk.CTkBaseClass) -> None:
        if widget.__dict__.get("protected", False):
            print(f"Cannot delete {widget}")
            return
        
        self._widgets.remove(widget)
        widget.destroy()
    
    def scroll_to_top(self) -> None:
        """
        Scrolls the frame to the top of the content.
        """
        self._parent_canvas.yview_moveto(0)

    @property
    def widgets(self) -> list[ctk.CTkBaseClass]:
        return self._widgets
    


class Button(ctk.CTkButton):
    def __init__(
        self,
        widget_name: str,
        master: ctk.CTk | ctk.CTkToplevel,
        single_click: Callable[[Button, tk.Event[Any]], None],
        double_click: Callable[[Button, tk.Event[Any]], None] | None = None,
        color: str | None = None,
        **kwargs: Any
    ) -> None:
        kwargs["master"] = master
        kwargs["fg_color"] = color
        super().__init__(**kwargs) #type: ignore


        self.widget_name: str = widget_name
        self._single_click_timer: str | None = None
        self._single_click_callback: Callable[[Button, tk.Event[Any]], None] = (
            single_click
        )
        self._double_click_callback: Callable[[Button, tk.Event[Any]], None] | None = (
            double_click
        )

        self.bind("<Button-1>", self._single_click) #type: ignore
        self.bind("<Double-1>", self._double_click) #type: ignore
    

    def _single_click(self, event: tk.Event[Any]) -> None:
        if self._single_click_timer is None:
            self._single_click_timer = self.after(250, self._activate_single_click, event)

    def _activate_single_click(self, event: tk.Event[Any]) -> None:
        self._single_click_callback(self, event)
        self._single_click_timer = None

    def _double_click(self, event: tk.Event[Any]) -> None:
        if not self._double_click_callback:
            self._activate_single_click(event)
            return
        
        if self._single_click_timer is not None:
            self.after_cancel(self._single_click_timer)
            self._single_click_timer = None
        
        self._double_click_callback(self, event)



class App:
    def __init__(
        self,
        app_name: str = "My App"
    ) -> None:
        """Initialises the application with the given app_name."""
        self.root: ctk.CTk = ctk.CTk()

        if not app_name.strip():
            raise ValueError("'app_name' cannot be empty.")
        
        self.root.title(app_name)

        self._app_name: str = app_name
        self._width: int = 800
        self._height: int = 600
        self._x_coord: int = 150
        self._y_coord: int = 100
        self._fullscreen: bool = False
        self._file_path: str = ""
        self._widgets: list[
            ctk.CTkBaseClass 
            | ctk.CTkFrame 
            | ctk.CTkScrollableFrame
        ] = []
        self._display_fp_widget: ctk.CTkLabel | None = None
        self._root_dir: str = ""
        self._images: dict[str, ctk.CTkImage] = {}

        self.extra_details: dict[str, Any] = {}

        self.root.geometry(
            f"{self._width}x{self._height}+{self._x_coord}+{self._y_coord}"
        )

        self.root.bind("<F11>", lambda x: self.toggle_fullscreen())
        self.root.bind("<Escape>", lambda x: self._exit_fullscreen())

    def run(self) -> None:
        """Runs the app mainloop."""
        self.root.mainloop() #type: ignore

    def add_frame(
        self,
        frame: Frame | ScrollableFrame
    ) -> None:
        self._widgets.append(frame)
        self.__setattr__(frame.__name__, frame)

    def add_widget(
        self, 
        name: str, 
        widget_object: type[ctk.CTkBaseClass],
        **kwargs: Any
    ) -> None:
        """
        Adds a widget to the application.

        Args:
            name (str): The name of the widget. Can then be accessed
                by `app.{name}`
            widget_object (type[ctk.CTkBaseClass]): The widget object, 
                e.g. ctk.CTkLabel. This is the uninitialised class.
            **kwargs (Any): The arguments you pass when initialising
                the widget outside of the app.
        """
        kwargs["master"] = self.root
        widget: ctk.CTkBaseClass = widget_object(**kwargs)
        self._widgets.append(widget)
        setattr(self, name, widget)

    def add_button(
        self,
        button: Button
    ) -> None:
        self._widgets.append(button)
        setattr(self, button.widget_name, button)

    def toggle_fullscreen(self) -> None:
        """Toggles fullscreen on or off, based on the current app state."""
        self.fullscreen = not self.fullscreen

    def toggle_light_mode(self) -> None:
        color_mode: str = "light" if ctk.get_appearance_mode().lower() == "dark" else "dark"
        ctk.set_appearance_mode(color_mode)

    def block_deletion(self, widget: ctk.CTkBaseClass) -> None:
        widget.__dict__["protected"] = True

    def remove_widget(self, widget: ctk.CTkBaseClass) -> None:
        if widget.__dict__.get("protected", False):
            print(f"Cannot delete {widget}")
            return
        
        self._widgets.remove(widget)
        widget.destroy()

    def add_image(
        self,
        name: str,
        light_image_file_path: str | None = None,
        dark_image_file_path: str | None = None,
        size: tuple[int, int] = (20, 20)
    ) -> None:
        light_image: ImageFile | None = None
        dark_image: ImageFile | None = None

        if light_image_file_path:
            light_image = Image.open(light_image_file_path)

        if dark_image_file_path:
            dark_image = Image.open(dark_image_file_path)

        self._images[name] = ctk.CTkImage(light_image, dark_image, size) #type: ignore

    def _exit_fullscreen(self) -> None:
        """Immediately exits fullscreen of the application."""
        self.fullscreen = False

    @property
    def fullscreen(self) -> bool:
        """The fullscreen property of the app."""
        return self._fullscreen

    @fullscreen.setter
    def fullscreen(self, state: bool) -> None:
        state_name: str = "zoomed" if state else "normal"

        geom: tuple[int, int, int, int] = self.geometry

        self.root.attributes('-fullscreen', state) #type: ignore
        self.root.state(state_name)

        self.geometry = {
            "width": geom[0],
            "height": geom[1],
            "x": geom[2],
            "y": geom[3]
        }
        self._fullscreen = state

    @property
    def file_path(self) -> str:
        return self._file_path
    
    @file_path.setter
    def file_path(self, value: str | list[str]) -> None:
        if isinstance(value, list):
            value = os.path.join(*value)

        if not files.valid_dir(value):
            raise NotADirectoryError(f"file_path expects a directory! {value} does not match!")

        self._file_path = files.fix_path(value)
            
        if self._display_fp_widget is not None:
            self._display_fp_widget.configure(text=value) #type: ignore


    @property
    def geometry(self) -> tuple[int, int, int, int]:
        """The geometry of the app. (width, height, x_coord, y_coord)"""
        return (self._width, self._height, self._x_coord, self._y_coord)

    @geometry.setter
    def geometry(
        self,
        kwargs: dict[str, int]
    ) -> None:
        self._width = kwargs.get("width", self._width)
        self._height = kwargs.get("height", self._height)
        self._x_coord = kwargs.get("x", self._y_coord)
        self._y_coord = kwargs.get("y", self._y_coord)

        self.root.geometry(
            f"{self._width}x{self._height}+{self._x_coord}+{self._y_coord}"
        )

    @property
    def app_name(self) -> str:
        """The name of the app. Cannot have any whitespace."""
        return self._app_name
    
    @app_name.setter
    def app_name(self, value: str) -> None:
        if not value.strip():
            raise ValueError("The app name cannot be blank.")
        
        self.root.title(value.strip())
        self._app_name = value.strip()

    @property
    def coords(self) -> tuple[int, int]:
        """The coordinates of the app currently."""
        return (self._x_coord, self._y_coord)
    
    @property
    def widgets(self) -> list[
        ctk.CTkBaseClass
        | ctk.CTkFrame
        | ctk.CTkScrollableFrame
    ]:
        return self._widgets
    
    @property
    def display_fp_widget(self) -> ctk.CTkLabel | None:
        return self._display_fp_widget

    @display_fp_widget.setter
    def display_fp_widget(self, value: ctk.CTkLabel) -> None:
        self._display_fp_widget = value

    @property
    def root_dir(self) -> str:
        return self._root_dir
    
    @root_dir.setter
    def root_dir(self, value: str | list[str]) -> None:
        if isinstance(value, list):
            value = os.path.join(*value)

        if not files.valid_dir(value):
            raise NotADirectoryError(f"root_dir expects a directory! {value} does not match!")

        self._root_dir = files.fix_path(value)

    @property
    def images(self) -> dict[str, ctk.CTkImage]:
        return self._images

    def __getattr__(self, name: str) -> Any:
        raise AttributeError

    def __delattr__(self, name: str) -> None:
        if name in [
            "parser",
            "app_name",
            "width",
            "height",
            "coords",
            "x_coord",
            "y_coord"
        ]:
            raise AttributeError(f"'{name}' cannot be deleted.")
        
        super().__delattr__(name)



def widget_exists(widget: ctk.CTkBaseClass | None) -> bool:
    try:
        return widget.winfo_exists() if widget else False
    except Exception:
        return False