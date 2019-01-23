# from application.FrontEndMain import app

# app = app
from backend.Features import newrelic
from backend.HelperFunctions.Common import Metrics, Common
import datetime
import asyncio
import aiohttp
import random


async def main(log, client):
    tasks = []
    #enddate = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
    #startdate = enddate - datetime.timedelta(seconds=60)
    # To Add the start time and end time Manually you must enter it in MST,
    startdate = datetime.datetime(2019, 1, 23, 15, 00, 00) + datetime.timedelta(seconds=25200)
    enddate = datetime.datetime(2019, 1, 23, 15, 00, 2) + datetime.timedelta(seconds=25200)

    logger.info("Starting process with this date range, Start: {} EndTime: {}".format(str(startdate), str(enddate)))
    one_rand_int = random.randint(1, 2000) * 5
    one_thread_id = "t"+ str(one_rand_int)
    # Add references to methods here
    # tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForApps(startdate, enddate, client, log, one_thread_id)))
    two_rand_int = random.randint(1, 2000) * 5
    two_thread_id = "t" + str(two_rand_int)
    tasks.append(asyncio.ensure_future(newrelic.collectTransactionsForApps(startdate, enddate, client, log, two_thread_id)))
    three_rand_int = random.randint(1, 2000) * 5
    three_thread_id = "t" + str(three_rand_int)
    # tasks.append(asyncio.ensure_future(newrelic.collectTransactionErrorsForApps(startdate, enddate, client, log, three_thread_id)))
    four_rand_int = random.randint(1, 2000) * 5
    four_thread_id = "t" + str(four_rand_int)
    # tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForMicroservices(startdate, enddate, client, log, four_thread_id)))

# TODO: Need to create a ID to add to the logs so i knwo what async thread i am looking at.
    #print(datetime.datetime.now().strftime('%H:%M.%S') + " Sleeping 60 sec")
    #time.sleep(60)
    #print(datetime.datetime.now().strftime('%H:%M.%S') + " Waking up")

    await asyncio.gather(*tasks)

logger = Common.setup_custom_logger('myapp')
logger.info(datetime.datetime.now().strftime('%H:%M.%S') + " Starting")
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)
log = Metrics()
logger.info('This is a message!')

loop.run_until_complete(main(log, client))

client.close()
loop.close()
# print("Total = " +log.get_newrelic_requestCount())
logger.info(datetime.datetime.now().strftime('%H:%M.%S') + " stopping")
