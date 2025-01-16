from copy import deepcopy
from datetime import datetime
import sys
import customtkinter as ctk
from CTkMessagebox import CTkMessagebox


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


def warn(
    root: ctk.CTk | None,
    title: str = "",
    message: str = ""
) -> None:
    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message: str = f"{current_date} WARN {title} - {message}"


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
        master=root,
        title=f"Warning - {title}",
        message=message,
        icon="warning",
        option_1="Continue",
        option_2="Cancel"
    )

    if msg.get() == "Cancel":
        sys.exit(1)




def error(
    root: ctk.CTk | None,
    title: str = "",
    message: str = ""
) -> None:
    current_date: str = datetime.now().strftime("%d-%m-%Y %H:%M:%S.%f")
    title = title.replace('\n', ' ')
    message = message.replace('\n', ' ')

    log_message: str = f"{current_date} ERROR {title} - {message}"

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
            master=root,
            title=f"Error: {title}",
            message=message,
            icon="cancel",
            option_1="OK"
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
