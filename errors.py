from copy import deepcopy
from datetime import datetime
import sys
from typing import NoReturn
import customtkinter as ctk #type: ignore
from CTkMessagebox import CTkMessagebox #type: ignore
import gui #type: ignore


class Colors:
    def __init__(
        self,
        info: str,
        warn: str,
        error: str,
        critical: str,
        emergency: str
    ) -> None:
        self.info: str = info
        self.warn: str = warn
        self.error: str = error
        self.critical: str = critical
        self.emergency: str = emergency

def rgb(
    red: int,
    green: int,
    blue: int,
    background: bool = False
) -> str:
    for value in (red, green, blue):
        if not (0 <= value <= 255):
            error(
                root=None,
                title="Invalid RGB color",
                message=(
                    "All RGB colors must have an integer value between "
                    + f"0 and 255, not '{value}"
                )
            )

    color_style: int = 38 if not background else 48

    color: str = "\033[{style};2;{r};{g};{b}m"
    
    return color.format(style=color_style, r=red, g=green, b=blue)


def confirm(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    options: tuple[str, str] = ("yes", "no")
) -> bool:
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')


    if not root:
        print(f"CONFIRM: {title} - {message}")
        print(f"{options[0].title()} | {options[1].title()}")
        while (item := input('>> ').lower()) not in options:
            print("That is not a valid option!")
            print(f"CONFIRM: {title} - {message}")
            print(f"{options[0].title()} | {options[1].title()}")
        
        return item == options[0].lower()
    

    msg = CTkMessagebox(
        master=root.root,
        title=f"CONFIRM - {title}",
        message=message,
        icon="question",
        option_1=options[0],
        option_2=options[1]
    )

    return msg.get() == options[0] #type: ignore


def warn(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    log_message: str = ""
) -> None | NoReturn:
    if "warn" not in log_values:
        return

    
    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    
    log_message = f"{current_date} WARN {title} - {log_message or message}"


    try:
        with open(log_file, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_colors.warn
            + log_message
            + __reset_color__
        )
    except NameError:
        with open(__log_file__, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_message
            + __reset_color__
        )

    if not root:
        return
    

    msg = CTkMessagebox(
        master=root.root,
        title=f"Warning - {title}",
        message=message,
        icon="warning",
        option_1="Continue",
        option_2="Quit App"
    )

    if msg.get() == "Quit App":
        sys.exit(1)




def error(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    log_message: str = ""
) -> NoReturn:
    if "error" not in log_values:
        sys.exit()


    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message = f"{current_date} ERROR {title} - {log_message or message}"

    try:
        with open(log_file, 'a') as f:
            print(log_message, file=f)
        print(
            log_colors.error
            + log_message
            + __reset_color__
        )
    except NameError:
        with open(__log_file__, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_message
            + __reset_color__
        )

    if root:
        CTkMessagebox(
            master=root.root,
            title=f"ERROR: {title}",
            message=message,
            icon="cancel",
            option_1="OK"
        )
    
    sys.exit(1)


def info(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    log_message: str = ""
) -> None:
    if "info" not in log_values:
        return


    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message = f"{current_date} INFO {title} - {log_message or message}"

    try:
        with open(log_file, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_colors.error
            + log_message
            + __reset_color__
        )
    except NameError:
        with open(__log_file__, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_message
            + __reset_color__
        )

    if root:
        CTkMessagebox(
            master=root.root,
            title=f"INFO: {title}",
            message=message,
            icon="info",
            option_1="OK"
        )
    


def critical(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    log_message: str = ""
) -> NoReturn:
    if "critical" not in log_values:
        sys.exit()


    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message = f"{current_date} CRITICAL {title} - {log_message or message}"

    try:
        with open(log_file, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_colors.error
            + log_message
            + __reset_color__
        )
    except NameError:
        with open(__log_file__, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_message
            + __reset_color__
        )

    if root:
        CTkMessagebox(
            master=root.root,
            title=f"CRITICAL: {title}",
            message=message,
            icon="cancel",
            option_1="Quit App"
        )
    
    sys.exit(1)


def emergency(
    root: gui.App | None,
    title: str = "",
    message: str = "",
    log_message: str = ""
) -> NoReturn:
    if "emergency" not in log_values:
        sys.exit()
    
    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message = f"{current_date} EMERGENCY {title} - {log_message or message}"

    try:
        with open(log_file, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_colors.error
            + log_message
            + __reset_color__
        )
    except NameError:
        with open(__log_file__, 'a') as f:
            print(log_message, file=f)
        
        print(
            log_message
            + __reset_color__
        )

    if root:
        CTkMessagebox(
            master=root.root,
            title=f"EMERGENCY: {title}",
            message=message,
            icon="cancel",
            option_1="Quit APP"
        )
    
    sys.exit(1)



__reset_color__: str = "\u001b[0m"
__log_file__: str = "elysium.LOG"
__log_colors__: Colors = Colors(
    info=rgb(173, 216, 230, background=True)+rgb(0, 51, 102),
    warn=rgb(255, 223, 186, background=True)+rgb(102, 51, 0),
    error=rgb(255, 200, 180, background=True)+rgb(102, 0, 0),
    critical=rgb(255, 102, 102, background=True)+rgb(51, 0, 0),
    emergency=rgb(255, 0, 0, background=True)+rgb(255, 255, 255)
)

log_colors: Colors = deepcopy(__log_colors__)
log_file: str = __log_file__
log_values: tuple[str, ...] = ("emergency", "critical", "error", "info", "warn")
