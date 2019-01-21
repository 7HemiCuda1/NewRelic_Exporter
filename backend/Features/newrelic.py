import datetime
import pytz  # pip install pytz
import os
import config
import json
from backend.Features import elastic
from backend.Classes import Query, NewRelicResults
from backend.HelperFunctions import Common

timezone = pytz.timezone('US/Mountain')


async def newRelicRequest(query, client):
    # TODO: Add try for errors.
    # print("- Request - " + str(query.url) + " *** \n" + str(query.querystring) + " ****  \n" + str(query.headers))
    async with client.get(query.url, params=query.querystring, headers=query.headers) as response:
        assert response.status != 500
        return await response.text()


def getNumOfEventsFromData(data):
    events = Common.Common.get_events_from_json(data)
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


async def get_number_rows_from_new_relic(nrqlQuery, query, client):
    querystring = {
        "nrql": nrqlQuery}
    returnVal = 0
    query.setQueryString(querystring)
    temp_results = json.loads(await newRelicRequest(query, client))
    try:
        returnVal = temp_results["results"][0]["count"]
    except Exception as e:
        print("Exception caught when trying to ge the number of rows returned from New Relic\n" + str(e))

    return returnVal


async def get_number_members_from_new_relic(nrqlQuery, query, client):
    querystring = {
        "nrql": nrqlQuery}
    returnVal = 0
    query.setQueryString(querystring)
    temp_results = json.loads(await newRelicRequest(query, client))
    try:
        returnVal = temp_results["results"][0]["count"]
        print("- INFO - # of members is " + str(returnVal))
    except Exception as e:
        print("Exception caught when trying to ge the number of rows returned from New Relic " + str(e))

    return returnVal


async def collectTransactionsForApps(startdate, enddate, client, log):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    print("starting transaction")
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(query, appname, client, "transactions", log)
        # TODO: Add logging method
        #print("- END - (" + appname + " Transactions DONE!!!)" + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-transactions")


async def collectTransactionErrorsForApps(startdate, enddate, client, log):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    print("starting transaction errors")
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(query, appname, client, "transactions", log)
        # TODO: Add logging method
        #print("- END - (" + appname + " Transactions DONE!!!) " + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-transactions-errors")


async def collectProcessInfoForApps(startdate, enddate, client, log):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    print("starting Processes for apps")
    for appname in config.BaseConfig.SystemSampleApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(query, appname, client, "host", log)
        # TODO: Add logging method
        #print("- END - (" + appname + " App process Errors DONE!!!) added - " + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-processinfo-errors-microservices")


async def collectProcessInfoForMicroservices(startdate, enddate, client, log):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    print("starting Processes for microservices")
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(query, appname, client, "process", log)
        # TODO: Add logging method
        #print("- END - (" + appname + " Microservice process Errors DONE!!!)" + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-processinfo-microservices")
    # end for



def writeJSONFile(data, appname):
    """
    Write the data to the file.
    :param data:
    :param appname:
    :return:
    """
    # Change to output Directory
    if config.BaseConfig.LogBackup:
        appRoot = (os.sep).join([config.BaseConfig.appRoot, "Data"])
        filename = "results-{}-{}.json".format(appname, datetime.datetime.now(timezone).isoformat(' '))
        filename = filename.replace(":", "-")
        fullpath = os.sep.join([appRoot, filename])
        try:
            with open(fullpath, "w") as fout:
                json.dump(data, fout)
                # json.dump(data, fout, indent=4, sort_keys=True)
                # TODO: Need logging here
                print("Saving File here: {}".format(fullpath))
            # end with
        except FileNotFoundError as e:
            print("- ERROR - File Not Found Error, Please check that folder is accessible. " + str(e))
        # end Try
    # end if


def areEventsEq(ev1, ev2):
    pairs = zip(ev1, ev2)
    try:
        difference = [[(k, x[k], y[k]) for k in x if x[k] != y[k]] for x, y in pairs if x != y]
        # first check to see if they match.
        if len(difference) > 0:
            # any(x != y for x,y in pairs):
            # since something does not match i need to find out what.
            # print("this is whats different " + str(difference))
            return False
        else:
            # print("They Match")
            return True

    except KeyError as e:
        print("- ERROR- Key Error when trying to compare " + str(e) + " event = " + str(ev1))

    return False


async def getAppTransactions(query, appname, client, type, log):
    json_results = {}
    index = config.BaseConfig.elasticSearchIndex[type]["index-name"]
    results = NewRelicResults.Results()
    delta = (query.endDate - query.startDate).total_seconds() / 60
    print("- INFO - Delta = " + str(delta))
    if delta > 604800:  # same as 1 week
        print("- WARNING - The Number of Seconds is too high. check your date range! "
              "System can only handle 1 week of seconds(604800), You provided {d}".format(d=delta))
        return {}
    # Get data loop (change the start date and end date by 1 min. then check that the data is different.)
    loop_start_date = query.startDate + datetime.timedelta(seconds=-1)
    loop_end_date = query.startDate
    previousEvents = {}
    s = 0
    while loop_start_date <= query.endDate:
        # shift both start date and end date by 1 min.
        loop_start_date = loop_end_date
        loop_end_date = loop_start_date + datetime.timedelta(seconds=1)

        # Build the Query and request.
        select = config.BaseConfig.elasticSearchIndex[type]["select"]
        memberselect = config.BaseConfig.elasticSearchIndex[type]["memberIdCheck"]
        f = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryFrom"]
        w = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryWhere"]
        pw = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryPostWhere"]
        pwm = config.BaseConfig.elasticSearchIndex[type]["memberIdWhere"]


        # TODO : Get a count of the requests and if it is grater than 1000 then we need to find a way to make it smaller.
        # get the number of rows.
        nrqlQueryRows = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
            select="count(*)", f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname, where=w,
            postwhere=pw)
        querystring = {"nrql": nrqlQueryRows}
        query.setQueryString(querystring)
        try:
            numOfRows = await get_number_rows_from_new_relic(nrqlQueryRows, query, client)
            print("Number of rows = " + str(numOfRows))
        except Exception as e:
            print("There was an Exception getting the number of rows (count) this is an async process. " + str(e))

        if numOfRows > 99:
            print("- Warning - There may be missing requests here. * Request : " + str(nrqlQueryRows))
            # if there are more than 100 then we need to request less. so lets get each memberId's requests.
            try:
                nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
                    select=memberselect, f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname,
                    where=w,
                    postwhere=pw)
                querystring = {"nrql": nrqlMemberIDQuery}
                query.setQueryString(querystring)

                # Get a list of members to cycle through to limit the amout of rows that comes back from New Relic.
                data_for_memberids = (await newRelicRequest(query, client))
                number_of_memberids = getNumOfEventsFromData(data_for_memberids)
                events_for_members = Common.Common.get_events_from_json(data_for_memberids)
                print("Number of members = " + str(number_of_memberids))

                nrqlNoMemberQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
                    select="count(*)", f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname, where=w,
                    postwhere=pw + "and MemberId IS NULL")
                querystring = {"nrql": nrqlNoMemberQuery}
                query.setQueryString(querystring)
                # Get the number of events that come back for events that have no Member ID.
                data_for_no_member = (await newRelicRequest(query, client))
                number_of_no_member_events = getNumOfEventsFromData(data_for_no_member)
                print("Number of events for no Member Ids. " + str(number_of_no_member_events))
                events_for_no_members = Common.Common.get_events_from_json(data_for_no_member)

            except Exception as e:
                print("There was an Exception getting the number of members this is an async process. " + str(e))
            if number_of_memberids > 1000:
                print("Number of members is too high need to figure out a new way to reduce the number of results from New Relic")
            else:
                for memb in events_for_members:
                    try:
                        # get the data for each member.
                        nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
                            select=select, f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname,
                            where=w,
                            postwhere=pw + pwm + memb + "'")
                        querystring = {"nrql": nrqlMemberIDQuery}
                        query.setQueryString(querystring)
                        member_results = json.loads(await newRelicRequest(query, client))
                        num_of_events_for_member = Common.Common.get_events_from_json(member_results)
                        print(" Got Events " + str(number_of_no_member_events))
                        events = Common.Common.get_events_from_json(member_results)

                        if len(num_of_events_for_member) > 0:
                            elastic.process_transactions(events, index + config.BaseConfig.indexDate, type, log)
                        else:
                            print("- INFO - No Events added to ElasticSearch for this member! " + memb)

                    except Exception as e:
                        print(" Exception - " + e)
#TODO: Get Events Ended here. Please resume.
                for ev in events_for_no_members:
                    nrqlQueryNoMember = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
                        select=select, f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname,
                        where=w,
                        postwhere=pw + "and MemberId IS NULL")
        elif numOfRows > 0:
            nrqlQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} LIKE '%{appname}%' {postwhere}".format(
                select=select, f=f, startDate=loop_start_date, endDate=loop_end_date, appname=appname, where=w, postwhere=pw)
            #TODO: temp message
            print("- Debug - NRQL Query = {}".format(nrqlQuery))
            querystring = {"nrql": nrqlQuery}
            query.setQueryString(querystring)

            try:
                temp_results = json.loads(await newRelicRequest(query, client))
                json_results[s] = temp_results
            except Exception as e:
                print("There was an Exception getting the number of rows this is an async process. " + str(e))

            # TODO: Set the event to the results object.
            # gets the events from the json results.
            events = Common.Common.get_events_from_json(json_results[s])
            # add the events to the elastic search cluster.
            if len(events) > 0:
                elastic.process_transactions(events, index + config.BaseConfig.indexDate, type, log)
            else:
                print("-* INFO - No Events added to ElasticSearch for this period!")
        else:
            print("- INFO - No data in this query " + nrqlQueryRows)
    # End While loop
    return json_results