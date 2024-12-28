from functools import cache
import platform as pform

@cache
def platform() -> str:
    """Returns the lowercase platform name for the system"""
    return pform.system().lower()