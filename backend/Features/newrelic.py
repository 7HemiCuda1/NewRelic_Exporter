import requests
import datetime
import pytz  # pip install pytz
import re, os
import json
from backend.Classes import Query
import config

timezone = pytz.timezone('US/Mountain')
from backend.Features import elastic
from backend.HelperFunctions import Common


def newRelicRequest(query):
    payload = ""
    # TODO: Add try for errors.
    response = requests.request("GET", query.url, headers=query.headers, params=query.querystring)

    if response.status_code != 200:
        # This means something went wrong so try again.
        response = requests.request("GET", query.url, headers=query.headers, params=query.querystring)
        if response.status_code != 200:
            raise Exception(
                'GET /tasks/ {code} - message= {text}'.format(code=response.status_code, text=response.text))

    # print(response.text)
    return response.text


def getNumOfEventsFromData(data):
    events = elastic.get_events_from_json(data)
    cnt = 0
    numOfEvents = len(events)
    for event in events:
        body = {}
        # get all entries and add to a string
        eventItems = event.keys()
        # print("event keys ")
        listOfKeys = []
        for key in eventItems:
            listOfKeys.append(key)
        for key in eventItems:
            cnt = cnt + 1
    return numOfEvents


def collectDataforTest(query, appRoot):
    """

    :param query:
    :return:
    """

    # Transactions (including Errors)
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = getAppTransactions(query, appname, appRoot)
        # print("The number of events added to ES = " + str(getNumOfEventsFromData(data)))
        # TODO: Add logging method
        print(appname + " Transactions DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transactions")

        # print("Processed : " + len(data) )
    # TODO: Need to add host stats
    # Host Stats.
    # for appname in config.BaseConfig.NewRelicMicroservices['services']:
    # data = {"defalt": "Data"}
    # print(appname + " Host Stats DONE!!!")
    # writeJSONFile(data, appRoot, appname)

    # Transaction Errors.
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = getAppTransactionErrors(query, appname, appRoot)
        print(appname + " Transaction Errors DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transaction-errors")


def getAppTransactions(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds()

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop.
    loopstartdate = query.startDate + datetime.timedelta(0, -1)
    loopenddate = query.startDate
    for s in range(int(delta)):
        # need to write every minute to a file to keep the file size smaller.
        if loopstartdate.second == 0:
            # write to json file for backup.
            writeJSONFile(jsonResults, appRoot, appname)

            jsonResults = {}

        # shift both start date and end date by 1 millisecond.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(0, 1)
        # print("Startdate is {} - end date is {} ".format(loopstartdate, loopenddate))

        # Build the Query and request.  with TIMEZONE 'America/Denver'
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName = '{appname}'".format(
                startDate=query.startDate,
                endDate=query.endDate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])
            # add the events to the elastic search cluster.
            elastic.process_transactions(events, "jd-transactions")
            print("Added {} transaction events to Elastic Search! ".format(str(len(events))))

    return jsonResults


def getAppTransactionErrors(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds()

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop.
    loopstartdate = query.startDate + datetime.timedelta(0, -1)
    loopenddate = query.startDate
    for s in range(int(delta)):
        # need to write every minute to a file to keep the file size smaller.
        if loopstartdate.second == 0:
            # write to json file for backup.
            writeJSONFile(jsonResults, appRoot, appname)

            jsonResults = {}

        # shift both start date and end date by 1 millisecond.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(0, 1)
        # print("Startdate is {} - end date is {} ".format(loopstartdate, loopenddate))

        # Build the Query and request.  with TIMEZONE 'America/Denver'
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName = '{appname}' " \
                        "and errorMessage IS NOT NULL".format(
                startDate=query.startDate,
                endDate=query.endDate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])
            # add the events to the elastic search cluster.
            elastic.process_transactions(events, "jd-transaction-errors")
            print("Added {} transaction error events to Elastic Search! ".format(str(len(events))))

    return jsonResults


def writeJSONFile(data, appRoot, appname):
    """
    Write the data to the file.
    :param data:
    :return:
    """
    # Change to output Directory
    appRoot = (os.sep).join([appRoot, "Data"])
    filename = "results-{}-{}.json".format(appname, datetime.datetime.now(timezone).isoformat(' '))
    filename = filename.replace(":", "-")
    fullpath = os.sep.join([appRoot, filename])
    with open(fullpath, "w") as fout:
        json.dump(data, fout)
        # json.dump(data, fout, indent=4, sort_keys=True)
        # TODO: Need logging here
        print("Saving File here: {}".format(fullpath))
