import json
from pprint import pprint

x = {
    "background": {
        "primary": [
            ["CTk", "fg_color"],
            ["CTkToplevel", "fg_color"],
            ["CTkFrame", "fg_color"]
        ],
        "secondary": [
            ["CTkFrame", "top_fg_color"],
            ["CTkFrame", "border_color"],
            ["CTkScrollableFrame", "label_fg_color"]
        ],
        "tertiary": [
            ["CTkLabel", "fg_color"],
            ["CTkEntry", "fg_color"]
        ]
    },
    "foreground": {
        "primary": [
            ["CTkButton", "fg_color"],
            ["CTkOptionMenu", "fg_color"],
            ["CTkSwitch", "progress_color"]
        ],
        "secondary": [
            ["CTkButton", "hover_color"],
            ["CTkSlider", "progress_color"],
            ["CTkComboBox", "border_color"]
        ],
        "accent": [
            ["CTkCheckBox", "fg_color"],
            ["CTkRadioButton", "fg_color"],
            ["CTkProgressBar", "progress_color"]
        ]
    },
    "text": {
        "primary": [
            ["CTkButton", "text_color"],
            ["CTkLabel", "text_color"],
            ["CTkTextbox", "text_color"]
        ],
        "secondary": [
            ["CTkEntry", "text_color"],
            ["CTkSlider", "button_color"],
            ["CTkProgressBar", "fg_color"]
        ],
        "hint": [
            ["CTkEntry", "placeholder_text_color"],
            ["CTkCheckBox", "text_color_disabled"],
            ["CTkOptionMenu", "text_color_disabled"]
        ],
        "inverse": [
            ["CTkButton", "text_color"],
            ["CTkLabel", "text_color"],
            ["CTkSlider", "button_hover_color"]
        ]
    },
    "interactive": {
        "hover": [
            ["CTkButton", "hover_color"],
            ["CTkCheckBox", "hover_color"],
            ["CTkScrollbar", "button_hover_color"]
        ],
        "selected": [
            ["CTkSegmentedButton", "selected_color"],
            ["CTkRadioButton", "border_color"],
            ["CTkOptionMenu", "fg_color"]
        ],
        "active": [
            ["CTkSwitch", "progress_color"],
            ["CTkSlider", "progress_color"],
            ["CTkTextbox", "scrollbar_button_hover_color"]
        ]
    },
    "utility": {
        "success": [
            ["CTkSwitch", "progress_color"],
            ["CTkSlider", "progress_color"],
            ["CTkRadioButton", "hover_color"]
        ],
        "warning": [
            ["CTkCheckBox", "hover_color"],
            ["CTkButton", "hover_color"],
            ["CTkSlider", "button_hover_color"]
        ],
        "error": [
            ["CTkFrame", "border_color"],
            ["CTkScrollbar", "button_hover_color"],
            ["CTkSegmentedButton", "unselected_hover_color"]
        ],
        "info": [
            ["CTkProgressBar", "progress_color"],
            ["CTkSlider", "fg_color"],
            ["CTkTextbox", "scrollbar_button_color"]
        ]
    }
}


with open("theme.json", "r") as f:
    theme = json.load(f)


with open("light.json", "r") as f:
    light = json.load(f)

with open("dark.json", "r") as f:
    dark = json.load(f)


for main_key in x:
    for secondary_key in x[main_key]:
        light_color = light[main_key][secondary_key]
        dark_colour = dark[main_key][secondary_key]

        for prim in theme:
            for sec in theme[prim]:
                if [prim, sec] in x[main_key][secondary_key]:
                    theme[prim][sec] = [light_color, dark_colour]


pprint(theme)

with open("theme.json", "w") as f:
    json.dump(theme, f)