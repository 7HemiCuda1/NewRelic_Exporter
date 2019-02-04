import datetime
import pytz  # pip install pytz
import os
import config
import json
from backend.Features import elastic
from backend.HelperFunctions import Common

timezone = pytz.timezone('US/Mountain')
logger = Common.Common.setup_custom_logger('newrelic')

async def newRelicRequest(querystring, threadId,  client):
    rlog = Common.Common.setup_custom_logger("resuests")
    # Get url and header info.
    header = config.BaseConfig.headers
    url = config.BaseConfig.url
    async with client.get(url, params=querystring, headers=header) as response:
        rlog.debug(threadId + " query string = " + str(querystring) + "\nResponse = " + str(response.status)
                   + " And Reason = " + str(response.reason))
        res = await response.text()
        if response.status != 200:
            rlog.error(threadId + " " + res + " Query = " + str(querystring) + " result " + str(response.status))
        else:
            rlog.debug(threadId + " " + res + " Query = " + str(querystring)+ " result " + str(response.status))
    return res


async def get_number_rows_from_new_relic(nrqlQuery, thread_id, client):
    querystring = {"nrql": nrqlQuery}
    return_value = 0

    temp_results = json.loads(await newRelicRequest(querystring,thread_id, client))
    try:
        return_value = temp_results["results"][0]["count"]
        logger.debug("{} - debug - # of rows from new relic is {} ".format(thread_id, str(return_value)))
    except Exception as e:
        logger.error("{} - ERROR - Exception caught when trying to ge the number of "
          "rows returned from New Relic\n{}".format(thread_id, str(e)))

    return return_value


async def collectTransactionsForApps(startdate, enddate, log, thread_id, client):
    logger.info("*" * 80)
    logger.info("{} starting transactions for apps".format(thread_id))
    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = await getAppTransactions(startdate, enddate, appname, "transactions", log, thread_id, client)
        writeJSONFile(data, appname + "-transactions", thread_id)


async def collectTransactionErrorsForApps(startdate, enddate, log, thread_id, client):
    logger.info("*" * 80)
    logger.info("{} starting transaction errors for apps".format(thread_id))

    for appname in config.BaseConfig.NewRelicApps["apps"]:
        data = await getAppTransactions(startdate, enddate, appname, "transaction-error", log, thread_id, client)
        writeJSONFile(data, appname + "-transactions-errors",thread_id)


async def collectHostInfoForApps(startdate, enddate, log, thread_id, client):
    logger.info("*" * 80)
    logger.info("{} starting host for apps".format(thread_id))
    for appname in config.BaseConfig.SystemSampleApps["apps"]:
        data = await getAppTransactions(startdate, enddate, appname, "host", log, thread_id, client)
        writeJSONFile(data, appname + "-processinfo-errors-microservices", thread_id)


async def collectProcessInfoForMicroservices(startdate, enddate, log, thread_id, client):
    logger.info("*" * 80)
    logger.info("{} starting Processes for microservices".format(thread_id))
    for appname in config.BaseConfig.NewRelicMicroservices["services"]:
        data = await getAppTransactions(startdate, enddate, appname, "process-micro", log, thread_id, client)
        writeJSONFile(data, appname + "-processinfo-microservices", thread_id)
    # end for


async def collectProcessInfoForApps(startdate, enddate, log, thread_id, client):
    logger.info("*" * 80)
    logger.info("{} starting Processes for Apps".format(thread_id))
    for appname in config.BaseConfig.ProcessSampleApp["apps"]:
        data = await getAppTransactions(startdate, enddate, appname, "process-app", log, thread_id, client)
        writeJSONFile(data, appname + "-processinfo-apps", thread_id)
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
                logger.info("{} Saving File here: {}".format(thread_id, fullpath))
            # end with
        except FileNotFoundError as e:
            logger.error("{} - ERROR - File Not Found Error, Please check that"
                  " folder is accessible. {} ".format(thread_id, str(e)))
        # end Try
    # end if


async def no_member_transaction_processing(loop_start_date,
                                           index,
                                           type,
                                           loop_end_date,
                                           json_results,
                                           s,
                                           event_history,
                                           appname,
                                           log,
                                           thread_id,
                                           client):
    # Build the Query and request.
    f = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryFrom"]
    w = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryWhere"]
    pw = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryPostWhere"]
    # Get number of results for no Member
    nrqlNoMemberQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                        " until '{endDate}' where {where} " \
                        "= '{appname}' {postwhere}".format(select="count(*)",
                                                                f=f,
                                                                startDate=loop_start_date,
                                                                endDate=loop_end_date,
                                                                appname=appname,
                                                                where=w,
                                                                postwhere=pw + " and MemberId IS NULL"
                                                                )
    querystring = {"nrql": nrqlNoMemberQuery}
    # Get the number of events that come back for events that have no Member ID.
    data_for_no_member = json.loads(await newRelicRequest(querystring, thread_id, client))
    num_of_no_member_events = data_for_no_member["results"][0]["count"]
    logger.debug("{} Number of events for no Member Ids. {}".format(thread_id, str(num_of_no_member_events)))

    if num_of_no_member_events > 100:
        logger.warn("{} - Warning - To Prevent missing requests here, filtering No MemberID by host"
              "* Request : {} ".format(thread_id, str(nrqlNoMemberQuery)))

        # Gets a list of hosts to use later to narrow query
        nrqlNoMemberHostQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                                " until '{endDate}' where {where} " \
                                "= '{appname}' {postwhere}".format(select="uniques(host)",
                                                                        f=f,
                                                                        startDate=loop_start_date,
                                                                        endDate=loop_end_date,
                                                                        appname=appname,
                                                                        where=w,
                                                                        postwhere=pw + " and MemberId IS NULL"
                                                                        )
        querystring = {"nrql": nrqlNoMemberHostQuery}
        data_for_no_member_hosts = json.loads(
            await newRelicRequest(querystring, thread_id, client))
        hosts = data_for_no_member_hosts["results"][0]["members"]
        logger.debug("{} - DEBUG - There are {} different hosts to pull data for.".format(thread_id, len(hosts)))

        for (i, host) in enumerate(hosts):
            # Gets the data for each host to import into Elastic Search
            pw = "and error IS NULL and MemberId IS NULL and host = '{}'".format(host)
            nrqlNoMemberIndividualHostQuery = "SELECT {select} FROM {f} SINCE '{startDate}'" \
                                              " until '{endDate}' where {where} " \
                                              "= '{appname}' {postwhere}".format(select="*",
                                                                                      f=f,
                                                                                      startDate=loop_start_date,
                                                                                      endDate=loop_end_date,
                                                                                      appname=appname,
                                                                                      where=w,
                                                                                      postwhere=pw
                                                                                      )
            querystring = {"nrql": nrqlNoMemberIndividualHostQuery}
            data_on_hosts = json.loads(await newRelicRequest(querystring, thread_id, client))
            host_events = Common.Common.get_events_from_json(data_on_hosts)
            # print("{} got {} host events for host {}".format(thread_id, str(len(host_events)), host))

            if len(host_events) > 0:
                elastic.process_transactions(host_events, index + config.BaseConfig.indexDate, type, log,
                                             thread_id)
                logger.info("{} - Adding {} no member Host transactions to "
                      "Elastic Search".format(thread_id, str(len(host_events))))
                event_history.increment_es__entries(len(host_events))
            else:
                logger.debug("{} - DEBUG - No Events added to ElasticSearch for "
                      "this host! {}".format(thread_id, host))

    elif num_of_no_member_events > 0:
        nrqlQueryNoMember = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                            "until '{endDate}' where {where} = '{appname}' " \
                            "{postwhere}".format(select="*",
                                                 f=f,
                                                 startDate=loop_start_date,
                                                 endDate=loop_end_date,
                                                 appname=appname,
                                                 where=w,
                                                 postwhere=pw + " and MemberId IS NULL")
        querystring = {"nrql": nrqlQueryNoMember}
        try:
            no_member_results = json.loads(await newRelicRequest(querystring, thread_id, client))
            json_results[s] = no_member_results
            no_member_events = Common.Common.get_events_from_json(no_member_results)

            if len(no_member_events) > 100:
                logger.error("*" * 50)
                logger.error("{} - CRITICAL - There are missing requests here, filtering No MemberID host, "
                             "Need further filtering * Request : {} ".format(thread_id, str(nrqlNoMemberQuery)))

            elif len(no_member_events) > 0:
                elastic.process_transactions(no_member_events, index + config.BaseConfig.indexDate, type, log,
                                             thread_id)
                logger.info("{} - Adding {} no member transactions to "
                            "Elastic Search".format(thread_id, str(len(no_member_events))))
                event_history.increment_es__entries(len(no_member_events))
            else:
                logger.debug("{} - DEBUG - No Events added to ElasticSearch for "
                             "this member! {}".format(thread_id, str(no_member_events)))

        except Exception as ex:
            logger.error("*" * 50)
            logger.error("{} Exception Getting number of no Member requests. {}".format(thread_id, str(ex)))
    # End elif
    return json_results


async def getAppTransactions(start_date, end_date, appname, type, log, thread_id, client):
    json_results = {}
    index = config.BaseConfig.elasticSearchIndex[type]["index-name"]

    # Testing a better loop
    delta = abs(end_date - start_date).seconds

    # Get data loop (change the start date and end date by 1 min. then check that the data is different.)
    loop_start_date = start_date + datetime.timedelta(seconds=-1)
    loop_end_date = start_date
    # Count number of events added.
    # event_history = Common.Metrics()
    s = 0
    for s in range(delta):

        print("{} Status - >>>>>>Loop # {} of {} for app {}".format(thread_id, s, delta, appname))

        if loop_start_date >= end_date:
            print("*"*10 + "Oh no. Loop broken " + "*"*10)
            logger.error("*"*10 + "Oh no. Loop broken " + "*"*10)

        # shift both start date and end date by 1 min.
        loop_start_date = loop_end_date
        loop_end_date = loop_start_date + datetime.timedelta(seconds=1)
        #event_history.get_newrelic_request_count()

        # TODO: Need to rethink the metrics process.
        event_history = Common.Metrics()
        # logger.info("-"*60)
        # logger.info("{} - INFO - Starting {} for {}"
        #             " interval {} to {}".format(thread_id, type, appname, loop_start_date, loop_end_date))
        # Build the Query and request.
        select = config.BaseConfig.elasticSearchIndex[type]["select"]
        memberselect = config.BaseConfig.elasticSearchIndex[type]["memberIdCheck"]
        f = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryFrom"]
        w = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryWhere"]
        pw = config.BaseConfig.elasticSearchIndex[type]["nrqlQueryPostWhere"]
        pwm = config.BaseConfig.elasticSearchIndex[type]["memberIdWhere"]

        if type != "process-micro":
            nrqlQueryRows = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                            "until '{endDate}' where {where} = " \
                            "'{appname}' {postwhere}".format(select="count(*)",
                                                             f=f,
                                                             startDate=loop_start_date,
                                                             endDate=loop_end_date,
                                                             appname=appname,
                                                             where=w,
                                                             postwhere=pw
                                                             )
        else:
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
        num_of_rows = (await get_number_rows_from_new_relic(nrqlQueryRows, thread_id, client))
        logger.info("{} **** Found {} **** entries for app {} on {} in interval {} to {}".format(thread_id,
                                                                                                 str(num_of_rows),
                                                                                                 type, appname,
                                                                                                 loop_start_date,
                                                                                                 loop_end_date
                                                                                                 ))
        # Check to see if there are too many rows. else that there are rows vs no rows.
        if num_of_rows > 99:
            logger.debug("*"*50)
            logger.debug("{} - DEBUG - To Prevent missing requests here, filtering on MemberID "
                         "* Request : {} ".format(thread_id, str(nrqlQueryRows)))
            # if there are more than 100 then we need to request less. so lets get each memberId's requests.
            try:
                if type != "process-micro":
                    nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                                        "until '{endDate}' where {where} " \
                                        "= '{appname}'".format(select=memberselect,
                                                                                f=f,
                                                                                startDate=loop_start_date,
                                                                                endDate=loop_end_date,
                                                                                appname=appname,
                                                                                where=w
                                                                                )
                else:
                    nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                                        "until '{endDate}' where {where} " \
                                        "LIKE '%{appname}%'".format(select=memberselect,
                                                                                f=f,
                                                                                startDate=loop_start_date,
                                                                                endDate=loop_end_date,
                                                                                appname=appname,
                                                                                where=w
                                                                                )
                querystring = {"nrql": nrqlMemberIDQuery}

                # Get a list of members to cycle through to limit the amount of rows that comes back from New Relic.
                data_for_memberids = json.loads(await newRelicRequest(querystring, thread_id, client))
                number_of_memberids = len(data_for_memberids["results"][0]["members"])
                logger.debug("{} Number of members = {}".format(thread_id, str(number_of_memberids)))
                members = data_for_memberids["results"][0]["members"]

            except Exception as e:
                logger.error("*" * 50)
                logger.error("{} - CRITICAL ERROR - There was an Exception getting the number of "
                             "members or just no members. Here is the Query Used {} \n"
                             "and here is the exception {}".format(thread_id, querystring, str(e)))
                return {}

            if number_of_memberids > 1000:
                logger.warn("*" * 50)
                logger.warn("{} - Error - Number of members is too high need to figure out a new "
                      "way to reduce the number of results from New Relic".format(thread_id))

            else:
                for memb in members:
                    # get the data for each member and add to Elastic Search.
                    nrqlMemberIDQuery = "SELECT {select} FROM {f} SINCE '{startDate}' " \
                                        "until '{endDate}' where {where} = '{appname}' " \
                                        "{postwhere}".format(select=select,
                                                             f=f,
                                                             startDate=loop_start_date,
                                                             endDate=loop_end_date,
                                                             appname=appname,
                                                             where=w,
                                                             postwhere=pw + " " + pwm + memb + "'"
                                                             )
                    querystring = {"nrql": nrqlMemberIDQuery}
                    try:
                        member_results = json.loads(await newRelicRequest(querystring, thread_id, client))
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
                            logger.info("{} - Adding {} member transactions to "
                                  "Elastic Search".format(thread_id, str(len(events_for_member))))
                            event_history.increment_es__entries(len(events_for_member))
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
            json_results = (
                await no_member_transaction_processing(loop_start_date, index, type, loop_end_date, json_results, s,
                                                       event_history, appname, log, thread_id, client))


            logger.debug("{} Processed NoMember Transactions. ".format(thread_id))

        elif num_of_rows > 0:
            nrqlQuery = "SELECT {select} FROM {f} SINCE '{startDate}' until '{endDate}' where {where} " \
                        "= '{appname}' {postwhere}".format(select=select,
                                                                f=f,
                                                                startDate=loop_start_date,
                                                                endDate=loop_end_date,
                                                                appname=appname,
                                                                where=w,
                                                                postwhere=pw
                                                                )
            querystring = {"nrql": nrqlQuery}
            try:
                temp_results = json.loads(await newRelicRequest(querystring, thread_id, client))
                json_results[s] = temp_results
            except Exception as e:
                logger.error("{} There was an Exception getting the number of rows this is an "
                      "async process. {}" .format(thread_id, str(e)))
            # gets the events from the json results.
            events = Common.Common.get_events_from_json(json_results[s])
            # add the events to the elastic search cluster.
            if len(events) > 0:
                elastic.process_transactions(events, index + config.BaseConfig.indexDate, type, log, thread_id)
                logger.info("{} - Adding {} transactions to "
                      "Elastic Search".format(thread_id, str(len(events))))
                event_history.increment_es__entries(len(events))
            else:
                logger.debug("{} -* DEBUG - No Events added to ElasticSearch "
                             "for this period! {} to {}".format(thread_id, loop_start_date, loop_end_date))
        else:
            logger.debug("{} - INFO - No data in this query {}".format(thread_id, nrqlQueryRows))
    # End While loop
    return json_results