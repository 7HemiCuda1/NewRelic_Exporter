import sys
from queue import Queue
from threading import Thread
from backend.HelperFunctions.Common import Common
from backend.Features import newrelic
from backend.HelperFunctions.Common import Metrics
import datetime
logger = Common.setup_custom_logger('main')

import asyncio
import aiohttp
import random

class Worker(Thread):
    """ Thread executing tasks from a given tasks queue """
    def __init__(self, tasks):
        Thread.__init__(self)
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            try:

                func(*args, **kargs)

            except Exception as e:
                # An exception happened in this thread
                print(e)
            finally:
                # Mark this task as done, whether an exception happened or not
                self.tasks.task_done()


class ThreadPool:
    """ Pool of threads consuming tasks from a queue """
    def __init__(self, num_threads):
        self.tasks = Queue(num_threads)
        for _ in range(num_threads):
            Worker(self.tasks)

    def add_task(self, func, *args, **kargs):
        """ Add a task to the queue """
        self.tasks.put((func, args, kargs))

    def map(self, func, args_list):
        """ Add a list of tasks to the queue """
        for args in args_list:
            self.add_task(func, args)

    def wait_completion(self):
        """ Wait for completion of all the tasks in the queue """
        self.tasks.join()


if __name__ == "__main__":
    from random import randrange
    from time import sleep

    async def control(startdate, enddate, log, client):
        tasks = []
        # Transactions
        rand_int = random.randint(1, 2000) * 5
        thread_id = "t" + str(rand_int)
        tasks.append(asyncio.ensure_future(newrelic.collectTransactionsForApps(startdate, enddate, log, thread_id, client)))
        # Transaction Errors
        rand_int = random.randint(1, 2000) * 5
        thread_id = "t" + str(rand_int)
        tasks.append(asyncio.ensure_future(newrelic.collectTransactionErrorsForApps(startdate, enddate, log, thread_id, client)))
        # Process for Docker Microservices
        rand_int = random.randint(1, 2000) * 5
        thread_id = "t" + str(rand_int)
        tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForMicroservices(startdate, enddate, log, thread_id, client)))
        # Process for Apps
        rand_int = random.randint(1, 2000) * 5
        thread_id = "t" + str(rand_int)
        tasks.append(asyncio.ensure_future(
            newrelic.collectProcessInfoForApps(startdate, enddate, log, thread_id, client)))
        # Host (infrastructure)
        rand_int = random.randint(1, 2000) * 5
        thread_id = "t" + str(rand_int)
        tasks.append(asyncio.ensure_future(newrelic.collectProcessInfoForApps(startdate, enddate, log, thread_id, client)))

        await asyncio.gather(*tasks)


    # Function to be executed in a thread
    def wait_delay(d):
        print("sleeping for (%d)sec" % d)
        sleep(d)

    # Generate random delays
    delays = [randrange(3, 7) for i in range(50)]

    # Instantiate a thread pool with 5 worker threads
    pool = ThreadPool(100)

    # Add the jobs in bulk to the thread pool. Alternatively you could use
    # `pool.add_task` to add single jobs. The code will block here, which
    # makes it possible to cancel the thread pool with an exception when
    # the currently running batch of workers is finished.

    # *****************************************************************************************************

    log = Metrics()
    loop = asyncio.get_event_loop()
    client = aiohttp.ClientSession(loop=loop)

    startdate = datetime.datetime(2019, 1, 30, 9, 3, 00) + datetime.timedelta(seconds=25200)
    enddate = datetime.datetime(2019, 1, 30, 9, 3, 10) + datetime.timedelta(seconds=25200)

    loop_start_date = startdate + datetime.timedelta(seconds=-1)
    loop_end_date = startdate
    method_list = ["ta", "tea", "pm", "ps"]
    logger.info("Start app with the following times. {} tp {}".format(startdate, enddate))

    while loop_start_date <= enddate:
        loop_start_date = loop_end_date
        loop_end_date = loop_start_date + datetime.timedelta(seconds=1)

        logger.info("*" * 80)
        logger.info("*" * 80)

        logger.info("Initiate start interval {} to {} ".format(loop_start_date, loop_end_date))
        pool.add_task(loop.run_until_complete(control(startdate, enddate, log, client)))

        logger.info("*" * 80)
        logger.info("*" * 80)

    client.close()
    loop.close()
    # print("Total = " +log.get_newrelic_requestCount())
    logger.info(datetime.datetime.now().strftime('%H:%M.%S') + " stopping")

    # *****************************************************************************************************

    pool.map(wait_delay, delays)
    pool.wait_completion()
