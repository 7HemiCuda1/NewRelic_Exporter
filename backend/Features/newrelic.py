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

    # Transactions for apps (excluding Errors)
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = getAppTransactions(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " Transactions DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transactions")
    # Transaction Errors for apps
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = getAppTransactionErrors(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " Transactions DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transactions-errors")

    # Transactions for Microservices
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        data = getMicroserviceTransactions(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " Microservice Transactions DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transactions-microservices")

    # Transaction Errors for Microservices
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        data = getMicroserviceTransactionsErrors(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " Microservice Transaction Errors DONE!!!")
        writeJSONFile(data, appRoot, appname + "-transactions-errors-microservices")

    # Process Info for Microservices
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        data = getHostStatisticForMicroservices(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " Microservice process Errors DONE!!!")
        writeJSONFile(data, appRoot, appname + "-processinfo-microservices")

    # Process Info for apps
    for appname in config.BaseConfig.SystemSample["apps"]:
        data = getHostStatisticForApps(query, appname, appRoot)
        # TODO: Add logging method
        print(appname + " App process Errors DONE!!!")
        writeJSONFile(data, appRoot, appname + "-processinfo-errors-microservices")




def getAppTransactions(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 min.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)
        if loopstartdate <= query.endDate:
            # Build the Query and request.
            if loopstartdate <= query.endDate:
                nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName = '{appname}' and error IS NULL ".format(
                    startDate=loopstartdate,
                    endDate=loopenddate,
                    appname=appname)
                querystring = {
                    "nrql": nrqlQuery}
                query.setQueryString(querystring)

                # do the request and set the returned data to a Dict.
                tempResults = json.loads(newRelicRequest(query))
                jsonResults[s] = tempResults

                # gets the events from the json results.
                events = elastic.get_events_from_json(jsonResults[s])
                # do comparison
                if previousEvents != {}:
                    if areEventsEq(events, previousEvents) == False:
                        # add the events to the elastic search cluster.
                        elastic.process_transactions(events, "jd-transaction-" + config.BaseConfig.indexDate)
                        print("Added {} transaction events to Elastic Search! ".format(str(len(events))))
                else:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-transaction-" + config.BaseConfig.indexDate)
                    print("Added {} transaction events to Elastic Search! ".format(str(len(events))))
                previousEvents = events


    return jsonResults


def getAppTransactionErrors(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop. (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 minute.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)

        # Build the Query and request.
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName = '{appname}' " \
                        "and errorMessage IS NOT NULL ".format(
                startDate=loopstartdate,
                endDate=loopenddate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])

            # do comparison
            if previousEvents != {}:
                if areEventsEq(events, previousEvents) == False:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-transaction-errors-"  + config.BaseConfig.indexDate)
                    print("Added {} transaction events to Elastic Search! ".format(str(len(events))))
            else:
                # add the events to the elastic search cluster.
                elastic.process_transactions(events, "jd-transaction-errors-"  + config.BaseConfig.indexDate)
                print("Added {} transaction error events to Elastic Search! ".format(str(len(events))))
            previousEvents = events

    return jsonResults


def getMicroserviceTransactions(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop. (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 minute.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)

        # Build the Query and request.
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName LIKE '%{appname}%' " \
                        "and errorMessage IS NULL ".format(
                startDate=loopstartdate,
                endDate=loopenddate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])

            # do comparison
            if previousEvents != {}:
                if areEventsEq(events, previousEvents) == False:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-transaction-microservice-"  + config.BaseConfig.indexDate)
                    print("Added {} transaction microservice to Elastic Search! ".format(str(len(events))))
            else:
                # add the events to the elastic search cluster.
                elastic.process_transactions(events, "jd-transaction-microservice-"  + config.BaseConfig.indexDate)
                print("Added {} transaction microservice events to Elastic Search! ".format(str(len(events))))
            previousEvents = events

    return jsonResults


def getMicroserviceTransactionsErrors(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop. (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 minute.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)

        # Build the Query and request.
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' where appName LIKE '%{appname}%' " \
                        "and errorMessage IS NOT NULL ".format(
                startDate=loopstartdate,
                endDate=loopenddate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])

            # do comparison
            if previousEvents != {}:
                if areEventsEq(events, previousEvents) == False:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-transaction-microservice-"  + config.BaseConfig.indexDate)
                    print("Added {} transaction microservice errors to Elastic Search! ".format(str(len(events))))
            else:
                # add the events to the elastic search cluster.
                elastic.process_transactions(events, "jd-transaction-microservice-"  + config.BaseConfig.indexDate)
                print("Added {} transaction microservice errors events to Elastic Search! ".format(str(len(events))))
            previousEvents = events

    return jsonResults


def getHostStatisticForMicroservices(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop. (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 minute.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)

        # Build the Query and request.
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM ProcessSample SINCE '{startDate}' until '{endDate}' WHERE `containerLabel_com.docker.swarm.service.name` LIKE '%{appname}%' " \
                        "and errorMessage IS NULL ".format(
                startDate=loopstartdate,
                endDate=loopenddate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])

            # do comparison
            if previousEvents != {}:
                if areEventsEq(events, previousEvents) == False:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-processstat-microservice-"  + config.BaseConfig.indexDate)
                    print("Added {} transaction microservice errors to Elastic Search! ".format(str(len(events))))
            else:
                # add the events to the elastic search cluster.
                elastic.process_transactions(events, "jd-processstat-microservice-"  + config.BaseConfig.indexDate)
                print("Added {} transaction microservice errors events to Elastic Search! ".format(str(len(events))))
            previousEvents = events

    return jsonResults


def getHostStatisticForApps(query, appname, appRoot):
    jsonResults = {}
    delta = (query.endDate - query.startDate).total_seconds() / 60

    # TODO: This needs to be refactored and handled higher.
    # need to check to see if the delta seconds is too high to query. This is a performance and time issue. I cant Async this.
    if delta > 604800:  # same as 1 week
        print("The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))

    # Get data loop. (change the start date and end date by 1 min. then check that the data is different.)
    loopstartdate = query.startDate + datetime.timedelta(minutes=-1)
    loopenddate = query.startDate
    previousEvents = {}
    for s in range(int(delta)):
        # shift both start date and end date by 1 minute.
        loopstartdate = loopenddate
        loopenddate = loopstartdate + datetime.timedelta(minutes=1)

        # Build the Query and request.
        if loopstartdate <= query.endDate:
            nrqlQuery = "SELECT * FROM SystemSample SINCE '{startDate}' until '{endDate}' WHERE application = '{appname}' " \
                        "and errorMessage IS NULL ".format(
                startDate=loopstartdate,
                endDate=loopenddate,
                appname=appname)
            querystring = {
                "nrql": nrqlQuery}
            query.setQueryString(querystring)

            # do the request and set the returned data to a Dict.
            tempResults = json.loads(newRelicRequest(query))
            jsonResults[s] = tempResults
            # gets the events from the json results.
            events = elastic.get_events_from_json(jsonResults[s])

            # do comparison
            if previousEvents != {}:
                if areEventsEq(events, previousEvents) == False:
                    # add the events to the elastic search cluster.
                    elastic.process_transactions(events, "jd-hoststat-" + config.BaseConfig.indexDate)
                    print("Added {} transaction microservice errors to Elastic Search! ".format(str(len(events))))
            else:
                # add the events to the elastic search cluster.
                elastic.process_transactions(events, "jd-hoststat-" + config.BaseConfig.indexDate)
                print("Added {} transaction microservice errors events to Elastic Search! ".format(str(len(events))))
            previousEvents = events

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
    try:
        with open(fullpath, "w") as fout:
            json.dump(data, fout)
            # json.dump(data, fout, indent=4, sort_keys=True)
            # TODO: Need logging here
            print("Saving File here: {}".format(fullpath))
    except FileNotFoundError as e:
        print("File Not Found Error, Please check that folder is accessible. " + str(e))

def areEventsEq(ev1, ev2):

    pairs = zip(ev1, ev2)
    try:
        difference = [[(k, x[k], y[k]) for k in x if x[k] != y[k]] for x, y in pairs if x != y]
        #first check to see if they match.
        if len(difference) > 0:
            #any(x != y for x,y in pairs):
            # since something does not match i need to find out what.
            #print("this is whats different " + str(difference))
            return False
        else:
            #print("They Match")
            return True

    except KeyError as e:
        print("Key Error when trying to compare " + str(e))

    return False