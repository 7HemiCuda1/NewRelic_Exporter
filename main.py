# from application.FrontEndMain import app

# app = app
from backend.Features import newrelic
from backend.HelperFunctions.Common import Metrics
import datetime
import asyncio
import aiohttp


async def main(log, client):
    tasks = []
    #enddate = datetime.datetime.utcnow() - datetime.timedelta(seconds=300)
    #startdate = enddate - datetime.timedelta(seconds=60)
    # To Add the start time and end time Manually you must enter it in MST,
    startdate = datetime.datetime(2019, 1, 21, 8, 36, 00) + datetime.timedelta(seconds=25200)
    enddate = datetime.datetime(2019, 1, 21, 8, 37, 00) + datetime.timedelta(seconds=25200)

    print("Starting process with this date range, Start: {} EndTime: {}".format(str(startdate), str(enddate)))

    # Add references to methods here
    # tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForApps(startdate, enddate, client, log)))
    tasks.append(asyncio.ensure_future(newrelic.collectTransactionsForApps(startdate, enddate, client, log)))
    # tasks.append(asyncio.ensure_future(newrelic.collectTransactionErrorsForApps(startdate, enddate, client, log)))
    # tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForMicroservices(startdate, enddate, client, log)))
# TODO: Need to create a ID to add to the logs so i knwo what async thread i am looking at.
    #print(datetime.datetime.now().strftime('%H:%M.%S') + " Sleeping 60 sec")
    #time.sleep(60)
    #print(datetime.datetime.now().strftime('%H:%M.%S') + " Waking up")

    await asyncio.gather(*tasks)

print(datetime.datetime.now().strftime('%H:%M.%S') + " Starting")
loop = asyncio.get_event_loop()
client = aiohttp.ClientSession(loop=loop)
log = Metrics()

loop.run_until_complete(main(log, client))

client.close()
loop.close()
#print("Total = " +log.get_newrelic_requestCount())
print(datetime.datetime.now().strftime('%H:%M.%S') + " stopping")
