import os
from datetime import datetime

def current_time_text() -> str:
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

def print_to_file(*args, filepath:str, datetime:bool=False) -> None:
    with open(filepath, mode='a') as f:
        for arg in args: print(arg, file=f)
        if datetime: print('@' + current_time_text(), file=f)


def print_to_stdout(*args, datetime:bool = False) -> None:
    for arg in args: print(arg)
    if datetime: print('@' + current_time_text())


def prepare_directory(path:str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)

