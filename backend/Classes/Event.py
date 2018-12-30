class Event:

    def __init__(self):
        """
        Initializes a new Event instance. All variables are initially set to
        None/ the empty list.
        """
        self._response.status = ""
        self._totalTime = None
        self._timestamp = None
        self._appId = None
        self._Language = ""
        self._queueDuration = None
        self._Username = ""
        self._appName = ""
        self._name = ""
        self._transactionType = ""
        self._URI = ""
        self._duration = None
        self._databaseCallCount = None
        self._UserId = ""
        self._transactionSubType = ""
        self._MemberId = ""
        self._Country = ""
        self._host = ""
        self._host.displayName = ""
        self._webDuration = None
        self._databaseDuration = None
        self._request.uri = ""
        self._tripId = ""
        self._realAgentId = None

    def __eq__(self, other):
        """(Event, Event) -> boolean

        Returns whether or not this Event is equal to Event other. Two
        Events are considered equal if all of their attributes are the same.

        :param other: the Event we are comparing this Event against
        :return: whether or not this Event is equal to Event other
        """
        return self._response.status == other._response.status and \
               self._totalTime == other._totalTime and \
               self._timestamp == other._timestamp and \
               self._appId == other._appId and \
               self._Language == other._Language and \
               self._queueDuration == other.queueDuration and \
               self._Username == other._Username and \
               self._appName == other._appName and \
               self._name == other._name and \
               self._transactionType == other._transactionType and \
               self._URI == other._URI and \
               self._duration == other._duration and \
               self._databaseCallCount == other._databaseCallCount and \
               self._UserId == other._UserId and \
               self._transactionSubType == other._transactionSubType and \
               self._MemberId == other._MemberId and \
               self._Country == other._Country and \
               self._host == other._host and \
               self._host.displayName == other._host.displayName and \
               self._webDuration == other._webDuration and \
               self._databaseDuration == other._databaseDuration and \
               self._request.uri == other._request.uri and \
               self._tripId == other._tripId and \
               self._realAgentId == other._realAgentId

    def __ne__(self, other):
        """(Event, Event) -> boolean

        Returns whether or not this Event is not equal to Event other.
        Two Events are considered not equal if some of their attributes are
        different.

        :param other: the Event we are comparing this Event against
        :return: whether or not this Event is not equal to Event other
        """
        return not self == other

    def set_timestamp(self, v):
        self._timestamp = v

    def get_timestamp(self):
        return self._timestamp

    def set_realAgentId(self, v):
        self._realAgentId = v

    def get_realAgentId(self):
        return self._realAgentId
