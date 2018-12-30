import os


def get_parent(path):
    """(str) -> str)
    Returns the parent folder of path path.

    :param path: the path we want to find the parent of

    :return: the parent folder of path
    """
    return os.path.dirname(path)


def getRoot(appRoot):
    """
    gets the root based on the number of directories to move up.
    :param appRoot:
    :return: appRoot:
    """
    for i in range(3):
        appRoot = get_parent(appRoot)

    return appRoot


class Metrics:

    def __init__(self):
        self._newrelic_requestCount = 0
        self._es_Entries = 0

    def increment_newrelic_requestCount(self, count):
        self._newrelic_requestCount = self._newrelic_requestCount + count

    def get_newrelic_requestCount(self):
        return self._newrelic_requestCount

    def increment_es_Entries(self, count):
        self._es_Entries = self._es_Entries + count

    def get_es_Entries(self):
        return self._es_Entries
