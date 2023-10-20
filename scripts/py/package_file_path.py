import os

from argparse import ArgumentParser
from typing import Callable

ROOT_DIR = os.path.abspath("./src/package/")

ORIGINAL = "..dgisim"
REPLACEMENT = "._core"

def do_text_work(f: Callable[[str], str]) -> None:
    for subdir, dirs, files in os.walk(ROOT_DIR):
        for file in files:
            file_path = os.path.join(subdir, file)
            if not file_path.endswith(".py"):
                continue
            with open(file_path, "rt") as fin:
                file_content = fin.read()
            file_content = f(file_content)
            with open(file_path, "wt") as fout:
                fout.write(file_content)

if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-r", "--replace", action="store_true")
    parser.add_argument("-b", "--back", action="store_true")
    args = parser.parse_args()

    def f(s: str):
        if args.replace:
            return s.replace(ORIGINAL, REPLACEMENT)
        elif args.back:
            return s.replace(REPLACEMENT, ORIGINAL)
        else:
            return s

    do_text_work(f)