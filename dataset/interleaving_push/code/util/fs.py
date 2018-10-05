import os

def ensure_dir_exists(pathspec):
    try:
        os.makedirs(pathspec)
    except Exception as e:
        pass
