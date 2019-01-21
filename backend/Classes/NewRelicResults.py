import config

class Results:

    def __init__(self):
        self._json = {}
        self._events = {}

    def get_events(self):
        return self._events

    def set_events(self, events):
        self._events = events

    def set_json(self, json):
        self._json = json

    def get_json(self):
        return self._json

    def update_json(self, json):
        self._json.update(json)

