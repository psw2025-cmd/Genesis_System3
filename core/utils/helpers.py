import os
from datetime import datetime


def timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def ensure_folder(path):
    os.makedirs(path, exist_ok=True)
    return path
