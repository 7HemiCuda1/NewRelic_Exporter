import os

class Common:

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
            appRoot = Common.get_parent(appRoot)

        return appRoot

    def get_events_from_json(data):
        """
        Takes the data from the json files and extracts the events.
        :param data: data that may contain events from new relic
        :return events: parsed json events
        """
        events = {}
        if len(data) > 3:
            print("Need to look at the data returning from New Relic. there are more than 3 nested dict lists")
            print("Data = \n" + str(events))
        elif len(data) > 2:
            events = data["results"][0]["events"]
            if len(events) < 1:
                print("There are no events, Here is the Data " + str(data))
        elif len(data) > 1:
            print("- INFO - Need to look at the data returning from New Relic. there are more than 3 nested dict lists")
            print("Data = \n" + str(events))
        elif len(data) > 0:
            events = data[0]["results"][0]["events"]
            if len(events) < 1:
                print("- INFO - There are no events, Here is the Data " + str(data))
        return events


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
