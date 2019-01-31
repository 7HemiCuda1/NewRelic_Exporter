import os
import sys
import logging
import datetime


class Common:

    def get_parent(path):
        """(str) -> str)
        Returns the parent folder of path path.

        :param path: the path we want to find the parent of

        :return: the parent folder of path
        """
        return os.path.dirname(path)

    def getRoot(file):
        """
        gets the root based on the number of directories to move up.
        :param file:
        :return: file:
        """
        for i in range(3):
            file = Common.get_parent(file)

        return file

    def get_events_from_json(data):
        """
        Takes the data from the json files and extracts the events.
        :param data: data that may contain events from new relic
        :return events: list of parsed json events
        """
        logger = Common.setup_custom_logger("common")
        # try:
        #     events = data["requests"][0]["events"]
        # except Exception as e:
        #     print("This is not a New Relic Result" + e)
        events = {}
        if len(data) > 3:
            logger.debug(
                "Common - get_events_from_data - Data > 3: Need to look at the data returning from New Relic. "
                "there are more than 3 nested dict lists")
            logger.debug("Data = \n" + str(events))
        elif len(data) > 2:
            try:
                events = data["results"][0]["events"]
            except KeyError as k:
                logger.error("Key Error with this data. {} ".format(data.__str__()))
                return events
            if len(events) < 1:
                logger.debug(
                    "Common - get_events_from_data - events > 2: There are no events, Here is the Data " + str(data))
        elif len(data) > 1:
            logger.debug(
                "- INFO - Need to look at the data returning from New Relic. there are more than 3 nested dict lists")
            logger.debug("Data = \n" + str(events))
        elif len(data) > 0:
            events = data[0]["results"][0]["events"]
            if len(events) < 1:
                logger.debug("- INFO - There are no events, Here is the Data " + str(data))
        return events

    def setup_custom_logger(name):
        formatter = logging.Formatter(fmt='%(asctime)s : %(levelname)-8s : %(name)s : %(funcName)s %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')
        stamp = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H")

        try:
            file_name = "log-"+ name + stamp + ".log"
            handler = logging.FileHandler(file_name, mode='w')
            handler.setFormatter(formatter)
        except OSError as ose:
            print("OS Error Logging is broken. " + str(ose))
        screen_handler = logging.StreamHandler(stream=sys.stdout)
        screen_handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.setLevel(logging.ERROR)
        logger.addHandler(handler)
        logger.addHandler(screen_handler)

        return logger


class Metrics:

    def __init__(self):
        self._newrelic_request_count = 0
        self._es__entries = 0

    def increment_newrelic_request_count(self, count):
        self._newrelic_request_count = self._newrelic_request_count + count

    def get_newrelic_request_count(self):
        return self._newrelic_request_count

    def increment_es__entries(self, count):
        self._es__entries = self._es__entries + count

    def get_es__entries(self):
        return self._es__entries
