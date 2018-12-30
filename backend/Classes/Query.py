import config


class Query:

    def __init__(self):
        """
        Creates a new Query object with num num, name name and section
		section.
		"""
        self.url = "https://insights-api.newrelic.com/v1/accounts/1139936/query"
        self.headers = {
            'X-Query-Key': config.BaseConfig.NR_APIKEY,
            'Accept': "application/json",
            'cache-control': "no-cache"
        }
        self.payload = ""
        self.querystring = None
        self.startDate = None
        self.endDate = None

    def __eq__(self, other):
        """
        Checks to see if this Query is equal to other. Query are
		equal when all of their attributes are equal.


        :param other:
        :return:
        """
        return self.url == other.url and \
               self.headers == other.headers and \
               self.payload == other.payload and \
               self.querystring == other.querystring

    def __ne__(self, other):
        """
        Checks to see if this Query is not equal to other. Query are
		equal when some of their attributes are not equal.


        :param other:
        :return:
        """
        return not self == other

    def __str__(self):
        """
        Returns a human readable string representation of this Query
		object

        :return:
        """

        return "{url} - {headers} - {payload} -  ({querystring})".format(url=self.url,
                                                                         headers=self.headers,
                                                                         payload=self.payload,
                                                                         querystring=self.querystring)

    def __hash__(self):
        """
        Generates a unique hashcode for this Query object. The hash-code of
		a Query object is determined by using the built-in hash function on
		a tuple containing all of its attributes.

		:return: A hash code for this Query object.
		"""
        return hash((self.url, self.headers, self.payload, self.querystring))

    def setURL(self, url):
        """
        sets the URL
        :param url:
        :return:
        """
        self.url = url

    def getURL(self):
        """
        returns the URL form the Query object
        :return:
        """
        return self.url

    def setQueryString(self, querystring):
        """
        sets the querystring
        :param querystring:
        :return:
        """
        self.querystring = querystring

    def getQueryString(self):
        """
        returns the querystring form the Query object
        :return:
        """
        return self.querystring

    def setHeaders(self, headers):
        """
        sets the headers
        :param headers :
        :return:
        """
        self.headers = headers

    def getHeaders(self):
        """
        returns the headers  form the Query object
        :return:
        """
        return self.headers

    def setPayload(self, payload):
        """
        sets the payload
        :param payload :
        :return:
        """
        self.payload = payload

    def getPayload(self):
        """
        returns the payload  form the Query object
        :return:
        """
        return self.payload

    def setStartDate(self, startDate):
        """
        sets the startDate
        :param startDate :
        :return:
        """
        self.startDate = startDate

    def getStartDate(self):
        """
        returns the startDate  form the Query object
        :return:
        """
        return self.startDate

    def setEndDate(self, endDate):
        """
        sets the endDate
        :param endDate :
        :return:
        """
        self.endDate = endDate

    def getEndDate(self):
        """
        returns the endDate  form the Query object
        :return:
        """
        return self.endDate
