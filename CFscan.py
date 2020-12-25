import os
import sys
from lib.output.helptxt import ArgumentParser
from lib.core.controller import Controller


class CFscan():
    def __init__(self):
        self.script_path = (os.path.dirname(os.path.realpath(__file__)))
        self.arguments = ArgumentParser(self.script_path)
        self.controller = Controller(self.script_path, self.arguments)

if __name__ == "__main__":
    main = CFscan()
    print(main.script_path)
