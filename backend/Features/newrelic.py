import datetime
import pytz  # pip install pytz
import os
import config
import json
from backend.Features import elastic
from backend.Classes import Query, NewRelicResults
from backend.HelperFunctions import Common

timezone = pytz.timezone('US/Mountain')
logger = Common.Common.setup_custom_logger('myapp')

async def newRelicRequest(url, querystring, headers, client):
    # TODO: Add try for errors.
    #
    # print("- Request - " + str(query.url) + " *** \n" + str(query.querystring) + " ****  \n" + str(query.headers))
    async with client.get(url, params=querystring, headers=headers) as response:
        assert response.status == 200
        return await response.text()


def getNumOfEventsFromData(data):
    events = Common.Common.get_events_from_json(data)
    # cnt = 0
    num_of_events = len(events)
    # TODO: Is this depricated?
    # for event in events:
    #     body = {}
    #     # get all entries and add to a string
    #     eventItems = event.keys()
    #     # print("event keys ")
    #     listOfKeys = []
    #     for key in eventItems:
    #         listOfKeys.append(key)
    #     for key in eventItems:
    #         cnt = cnt + 1
    return num_of_events


async def get_number_rows_from_new_relic(nrqlQuery, query, client, thread_id):
    querystring = {
        "nrql": nrqlQuery}
    return_value = 0
    query.setQueryString(querystring)
    temp_results = json.loads(await newRelicRequest(query.url,querystring, query.headers, client))
    try:
        return_value = temp_results["results"][0]["count"]
        logger.debug("{} - INFO - # of rows from new relic is {} ".format(thread_id, str(return_value)))
    except Exception as e:
        logger.error("{} - ERROR - Exception caught when trying to ge the number of "
              "rows returned from New Relic\n{}".format(thread_id, str(e)))

    return return_value


async def get_number_members_from_new_relic(nrqlQuery, query, client, thread_id):
    querystring = {
        "nrql": nrqlQuery}
    return_value = 0
    query.setQueryString(querystring)
    temp_results = json.loads(await newRelicRequest(query.url,querystring, query.headers, client))
    try:
        return_value = temp_results["results"][0]["count"]
        # TODO: breakpoint added to ensure we are capturing the members correctly
        logger.debug("{} - INFO - # of members is {} ".format(thread_id, str(return_value)))
    except Exception as e:
        logger.error("{} Exception caught when trying to ge the number of rows returned from New Relic " .format(thread_id, str(e)))

    return return_value


async def collectTransactionsForApps(startdate, enddate, client, log, thread_id):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    logger.info("{} starting transaction".format(thread_id))
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(startdate, enddate, appname, client, "transactions", log, thread_id)
        # TODO: Add logging method
        #print("- END - (" + appname + " Transactions DONE!!!)" + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-transactions", thread_id)


async def collectTransactionErrorsForApps(startdate, enddate, client, log, thread_id):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    logger.info("{} starting transaction errors".format(thread_id))
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(startdate, enddate, appname, client, "transaction-error", log, thread_id)
        # TODO: Add logging method
        #print("- END - (" + appname + " Transactions DONE!!!) " + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-transactions-errors",thread_id)


async def collectProcessInfoForApps(startdate, enddate, client, log, thread_id):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    logger.info("{} starting Processes for apps".format(thread_id))
    for appname in config.BaseConfig.SystemSampleApps["apps"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(startdate, enddate, appname, client, "host", log, thread_id)
        # TODO: Add logging method
        #print("- END - (" + appname + " App process Errors DONE!!!) added - " + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-processinfo-errors-microservices", thread_id)


async def collectProcessInfoForMicroservices(startdate, enddate, client, log, thread_id):
    query = Query.Query()
    query.setStartDate(startdate)
    query.setEndDate(enddate)
    logger.info("{} starting Processes for microservices".format(thread_id))
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        #print("- START -  processing " + str(appname))
        data = await getAppTransactions(startdate, enddate, appname, client, "process", log, thread_id)
        # TODO: Add logging method
        #print("- END - (" + appname + " Microservice process Errors DONE!!!)" + str(log.get_newrelic_requestCount()))
        writeJSONFile(data, appname + "-processinfo-microservices", thread_id)
    # end for



def writeJSONFile(data, appname, thread_id):
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
                logger.info("{} Saving File here: {}".format(thread_id, fullpath))
            # end with
        except FileNotFoundError as e:
            logger.error("{} - ERROR - File Not Found Error, Please check that"
                  " folder is accessible. {} ".format(thread_id, str(e)))
        # end Try
    # end if


def areEventsEq(ev1, ev2, thread_id):
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
        logger.error("{} - ERROR- Key Error when trying to compare {} event = {}".format(thread_id, str(e), str(ev1)))

    return False


def get_members_from_newrelic_data(data_for_memberids, thread_id):

    try:
        returnVal = data_for_memberids["results"][0]["members"]
        logger.debug("{} Number of members actually retirived = {}".format(thread_id, len(returnVal)))
    except Exception as e:
        logger.error("{} Exception caught when trying to ge the members returned from New Relic {} ".format(thread_id, str(e)))
    return returnVal


async def no_member_transaction_processing(loop_start_date,
                                           index,
                                           type,
                                           loop_end_date,
                                           json_results,
                                           s,
                                           appname,
                                           my_query,
                                           client,
                                           log,
                                           thread_id):

    # Build the Query and request.
    f = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryFrom"]
    w = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryWhere"]
    pw = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryPostWhere"]
    # Get number of results for no Member
    nrqlNoMemberQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                        " until '{endDate}' where {where} " \
                        "LIKE '%{appname}%' {postwhere}".format(select="count(*)",
                                                                f=f,
                                                                startDate=loop_start_date,
                                                                endDate=loop_end_date,
                                                                appname=appname,
                                                                where=w,
                                                                postwhere=pw + "and MemberId IS NULL"
                                                                )
    querystring = {"nrql": nrqlNoMemberQuery}
    my_query.setQueryString(querystring)
    # Get the number of events that come back for events that have no Member ID.
    data_for_no_member = json.loads(await newRelicRequest(my_query.url, querystring, my_query.headers, client))
    num_of_no_member_events = data_for_no_member["results"][0]["count"]
    logger.debug("{} Number of events for no Member Ids. {}".format(thread_id, str(num_of_no_member_events)))

    if num_of_no_member_events > 100:
        logger.warn("{} - Warning - To Prevent missing requests here, filtering No MemberID by host"
              "* Request : {} ".format(thread_id, str(nrqlNoMemberQuery)))

        # Gets a list of hosts to use later to narrow query
        nrqlNoMemberHostQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                                " until '{endDate}' where {where} " \
                                "LIKE '%{appname}%' {postwhere}".format(select="uniques(host)",
                                                                        f=f,
                                                                        startDate=loop_start_date,
                                                                        endDate=loop_end_date,
                                                                        appname=appname,
                                                                        where=w,
                                                                        postwhere=pw + "and MemberId IS NULL"
                                                                        )
        querystring = {"nrql": nrqlNoMemberHostQuery}
        my_query.setQueryString(querystring)
        data_for_no_member_hosts = json.loads(
            await newRelicRequest(my_query.url, querystring, my_query.headers, client))
        hosts = data_for_no_member_hosts["results"][0]["members"]
        logger.debug("{} - INFO - There are {} different hosts to pull data for.".format(thread_id, len(hosts)))

        for (i, host) in enumerate(hosts):
            # Gets the data for each host to import into Elastic Search
            pw = "and error IS NULL and MemberId IS NULL and host = '{}'".format(host)
            nrqlNoMemberIndividualHostQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                                              " until '{endDate}' where {where} " \
                                              "LIKE '%{appname}%' {postwhere}".format(select="*",
                                                                                      f=f,
                                                                                      startDate=loop_start_date,
                                                                                      endDate=loop_end_date,
                                                                                      appname=appname,
                                                                                      where=w,
                                                                                      postwhere=pw
                                                                                      )
            querystring = {"nrql": nrqlNoMemberIndividualHostQuery}
            my_query.setQueryString(querystring)
            data_on_hosts = json.loads(await newRelicRequest(my_query.url, querystring, my_query.headers, client))
            host_events = Common.Common.get_events_from_json(data_on_hosts)
            # print("{} got {} host events for host {}".format(thread_id, str(len(host_events)), host))

            if len(host_events) > 0:
                elastic.process_transactions(host_events, index + config.BaseConfig.indexDate, type, log,
                                             thread_id)
            else:
                logger.debug("{} - INFO - No Events added to ElasticSearch for "
                      "this host! {}".format(thread_id, host))

    elif num_of_no_member_events > 0:
        nrqlQueryNoMember = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                            "until '{endDate}' where {where} LIKE '%{appname}%' " \
                            "{postwhere}".format(select="*",
                                                 f=f,
                                                 startDate=loop_start_date,
                                                 endDate=loop_end_date,
                                                 appname=appname,
                                                 where=w,
                                                 postwhere=pw + "and MemberId IS NULL")
        querystring = {"nrql": nrqlQueryNoMember}
        my_query.setQueryString(querystring)
        try:
            no_member_results = json.loads(await newRelicRequest(my_query.url, querystring, my_query.headers, client))
            json_results[s] = no_member_results
            no_member_events = Common.Common.get_events_from_json(no_member_results)
            # print("{} got {} events for hosts!".format(thread_id, str(len(no_member_events))))

            # TODO: Need to check to see if there is too many requests.
            if len(no_member_events) > 100:
                logger.error("*" * 50)
                logger.error("{} - CRITICAL - There are missing requests here, filtering No MemberID host, Need further filtering"
                      "* Request : {} ".format(thread_id, str(nrqlNoMemberQuery)))

            elif len(no_member_events) > 0:
                elastic.process_transactions(no_member_events, index + config.BaseConfig.indexDate, type, log,
                                             thread_id)
            else:
                logger.debug("{} - INFO - No Events added to ElasticSearch for "
                      "this member! {}".format(thread_id, str(no_member_events)))

        except Exception as ex:
            logger.error("*" * 50)
            logger.error("{} Exception Getting number of no Member requests. {}".format(thread_id, str(ex)))
    # End elif
    return json_results

async def getAppTransactions(start_date, end_date, appname, client, type, log, thread_id):
    my_query = Query.Query()
    json_results = {}
    index = config.BaseConfig.elasticSearchIndex[type]["index-name"]
    # results = NewRelicResults.Results()

    # Get data loop (change the start date and end date by 1 min. then check that the data is different.)
    loop_start_date = start_date + datetime.timedelta(seconds=-1)
    loop_end_date = start_date
    previousEvents = {} # TODO: Do i need this
    # create timer
    total = 0
    s = 0
    while loop_start_date <= end_date:
        # create a test stopwatch
        start_stopwatch = datetime.datetime.now()

        # shift both start date and end date by 1 min.
        loop_start_date = loop_end_date
        loop_end_date = loop_start_date + datetime.timedelta(seconds=1)
        logger.info("-"*60)
        logger.info("- INFO - Starting interval {} to {}".format(loop_start_date, loop_end_date))
        # Build the Query and request.
        select = config.BaseConfig.elasticSearchIndex[type]["select"]
        memberselect = config.BaseConfig.elasticSearchIndex[type]["memberIdCheck"]
        f = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryFrom"]
        w = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryWhere"]
        pw = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryPostWhere"]
        pwm = config.BaseConfig.elasticSearchIndex[type]["memberIdWhere"]

        # TODO: Get a count of the requests and if it is grater than 100 then we need to find a way to make it smaller.
        # get the number of rows for the next period.
        nrqlQueryRows = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                        "until '{endDate}' where {where} LIKE " \
                        "'%{appname}%' {postwhere}".format(select="count(*)",
                                                           f=f,
                                                           startDate=loop_start_date,
                                                           endDate=loop_end_date,
                                                           appname=appname,
                                                           where=w,
                                                           postwhere=pw
                                                           )
        querystring = {"nrql": nrqlQueryRows}
        my_query.setQueryString(querystring)
        #TODO: Removed Try, may need to handle possible error.
        num_of_rows = (await get_number_rows_from_new_relic(nrqlQueryRows, my_query, client, thread_id))
        logger.debug("{} Number of rows = {}".format(thread_id, str(num_of_rows)))
        # Check to see if there are too many rows. else that there are rows vs no rows.
        if num_of_rows > 99:
            logger.debug("*"*50)
            logger.debug("{} - Warning - To Prevent missing requests here, filtering on MemberID "
                  "* Request : {} ".format(thread_id, str(nrqlQueryRows)))
            # if there are more than 100 then we need to request less. so lets get each memberId's requests.
            try:
                nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                                    "until '{endDate}' where {where} " \
                                    "LIKE '%{appname}%' {postwhere}".format(select=memberselect,
                                                                            f=f,
                                                                            startDate=loop_start_date,
                                                                            endDate=loop_end_date,
                                                                            appname=appname,
                                                                            where=w,
                                                                            postwhere=pw
                                                                            )
                querystring = {"nrql": nrqlMemberIDQuery}
                my_query.setQueryString(querystring)

                # Get a list of members to cycle through to limit the amount of rows that comes back from New Relic.
                data_for_memberids = json.loads(await newRelicRequest(my_query.url,querystring, my_query.headers, client))
                number_of_memberids = len(data_for_memberids["results"][0]["members"])
                logger.debug("{} Number of members = {}".format(thread_id, str(number_of_memberids)))
                members = data_for_memberids["results"][0]["members"]

            except Exception as e:
                logger.error("*" * 50)
                logger.error("{} - CRITICAL ERROR - There was an Exception getting the number of "
                      "members or just no members this is an async process. ".format(thread_id, str(e)))
                return {}

            if number_of_memberids > 1000:
                logger.warn("*" * 50)
                logger.warn("{} - Error - Number of members is too high need to figure out a new "
                      "way to reduce the number of results from New Relic".format(thread_id))

            else:
                for memb in members:
                    # TODO: May need to check the amount of returned results to make sure we dont miss anything.
                    # get the data for each member and add to Elastic Search.
                    nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                                        "until '{endDate}' where {where} LIKE '%{appname}%' " \
                                        "{postwhere}".format(select=select,
                                                             f=f,
                                                             startDate=loop_start_date,
                                                             endDate=loop_end_date,
                                                             appname=appname,
                                                             where=w,
                                                             postwhere=pw + pwm + memb + "'"
                                                             )
                    querystring = {"nrql": nrqlMemberIDQuery}
                    my_query.setQueryString(querystring)
                    try:
                        member_results = json.loads(await newRelicRequest(my_query.url,querystring, my_query.headers, client))
                        json_results[s] = member_results
                        events_for_member = Common.Common.get_events_from_json(member_results)
                        # print("{} Got {} Events! ".format(thread_id, str(len(events_for_member))))

                        if len(events_for_member) > 0:
                            elastic.process_transactions(events_for_member,
                                                         index + config.BaseConfig.indexDate,
                                                         type,
                                                         log,
                                                         thread_id
                                                         )
                        else:
                            logger.info("*" * 50)
                            logger.info("{} - INFO - No Events added to ElasticSearch "
                                  "for this member! {}".format(thread_id, memb))
                    except Exception as e:
                        logger.error("*" * 50)
                        logger.error("{} Exception - {}".format(thread_id, e))
                # End For
            # End else

            # Process No Member results.
            json_results = (await no_member_transaction_processing(loop_start_date, index, type, loop_end_date, json_results, s, appname, my_query, client, log, thread_id))

            logger.debug("{} Processed NoMember Transactions. ".format(thread_id))

        elif num_of_rows > 0:
            nrqlQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} " \
                        "LIKE '%{appname}%' {postwhere}".format(select=select,
                                                                f=f,
                                                                startDate=loop_start_date,
                                                                endDate=loop_end_date,
                                                                appname=appname,
                                                                where=w,
                                                                postwhere=pw
                                                                )
            #TODO: temp message
            logger.debug("{} - Debug - NRQL Query = {}".format(thread_id, nrqlQuery))
            querystring = {"nrql": nrqlQuery}
            my_query.setQueryString(querystring)

            try:
                temp_results = json.loads(await newRelicRequest(my_query.url,querystring, my_query.headers, client))
                json_results[s] = temp_results
            except Exception as e:
                logger.error("{} There was an Exception getting the number of rows this is an "
                      "async process. {}" .format(thread_id, str(e)))

            # TODO: Set the event to the results object.
            # gets the events from the json results.
            events = Common.Common.get_events_from_json(json_results[s])
            # add the events to the elastic search cluster.
            if len(events) > 0:
                elastic.process_transactions(events, index + config.BaseConfig.indexDate, type, log, thread_id)
            else:
                logger.debug("{} -* INFO - No Events added to ElasticSearch for this period!".format(thread_id))
        else:
            logger.debug("{} - INFO - No data in this query {}".format(thread_id, nrqlQueryRows))
        s = s + 1  # increment for the jsonResults
        stop_stopwatch = datetime.datetime.now()
        time = stop_stopwatch - start_stopwatch
        logger.info("This second started at {} and ended at {}".format(start_stopwatch, stop_stopwatch))
        total = total + time.total_seconds()
    # End While loop
    # timer
    logger.info("This applcation took {} seconds to run. ".format(total))
    return json_results