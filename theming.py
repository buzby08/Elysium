import json



def update_widget_theme(
    UI_theme: dict[str, dict[str, dict[str, str]]],
    file_path: str,
    root_dir: str = ""
) -> None:
    """
    Updates the widget theme file based on the given `UI_theme`.

    Args:
        UI_theme (dict[str, dict[str, dict[str, str]]]): This is a 
        dictionary of both light and dark themes, showing colors for 
        each element, such as `interactive.foreground`.
        file_path (str): The file path to save the widget theme to.
    """
    with open(f"{root_dir}\\Themes\\widgetTheme.json", "r") as widgetTheme_file, \
        open(f"{root_dir}\\Themes\\UIToWidget.json", 'r') as UIToWidget_file:
        widget_theme = json.load(widgetTheme_file)
        UIToWidget_theme = json.load(UIToWidget_file)

    for main_key in UIToWidget_theme:
        for secondary_key in UIToWidget_theme[main_key]:
            light_color = UI_theme["light"][main_key][secondary_key]
            dark_colour = UI_theme["dark"][main_key][secondary_key]

            for prim in widget_theme:
                for sec in widget_theme[prim]:
                    if [prim, sec] in UIToWidget_theme[main_key][secondary_key]:
                        widget_theme[prim][sec] = [light_color, dark_colour]

    with open(file_path, "w") as f:
        json.dump(widget_theme, f)


def save_color_scheme(
    scheme: dict[str, dict[str, dict[str, str]]],
    file_path: str,
    root_dir: str = ""
) -> None:
    """
    Saves a UI color scheme, and saves it to the widgets theme file.

    Args:
        scheme (dict[str, dict[str, dict[str, str]]]): The UI colour 
        scheme as a dictionary. View the `UI_theme` argument in the 
        `update_widget_theme` function for more information.
        file_path (str): The file path to save the updated widget theme.
    """
    update_widget_theme(scheme, file_path)

    with open(f"{root_dir}\\Themes\\UITheme.json", "w") as f:
        json.dump(scheme, f)


def main() -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()