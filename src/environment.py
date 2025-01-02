# This is a class that is used to manage environment variables in the repl and webapp
# It allows you to set and get environment variables from a dictionary
import os
from src.constants import *


class Environment:
    def __init__(self):
        self.env = DEFAULT_ENVIRONMENT
        # Load all the environment variables that start with PROMPTER_ into the environment
        for key, value in os.environ.items():
            if key.startswith("PROMPTER_"):
                # Remove the PROMPTER_ prefix
                key = key[9:].upper()
                self.env[key] = value

    def set(self, key, value):
        self.env[key.upper()] = value

    def get(self, key):
        return self.env.get(key.upper())

    def clear(self):
        self.env.clear()

    def unset(self, key):
        # Remove the key from the environment if it exists
        if key.upper() in self.env:
            del self.env[key.upper()]

    def __getitem__(self, key):
        return self.get(key)

    def __setitem__(self, key, value):
        self.set(key, value)

    def __contains__(self, key):
        return key in self.env

    def get_all(self):
        return self.env
        return repr(self.env)

    def __str__(self):
        return str(self.env)
