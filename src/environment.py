# This is a class that is used to manage environment variables in the repl and webapp
# It allows you to set and get environment variables from a dictionary


class Environment:
    def __init__(self):
        self.env = {}

    def set(self, key, value):
        self.env[key] = value

    def get(self, key):
        return self.env.get(key)

    def clear(self):
        self.env.clear()

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
