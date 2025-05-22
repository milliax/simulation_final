
# TODO: Add a docstring to describe the purpose of this module

class Dispatcher:
    def __init__(self):
        self.routes = {}

    def register_route(self, path, handler):
        self.routes[path] = handler

    def dispatch(self, path):
        if path in self.routes:
            return self.routes[path]()
        else:
            return "404 Not Found"