# make sure ES is up and running
import os
from elasticsearch import Elasticsearch
from backend.HelperFunctions import Common
import config
import datetime
logger = Common.Common.setup_custom_logger('elastic')

cur_file = os.path.realpath(__file__)
appRoot = Common.Common.getRoot(cur_file)

dataDir = (os.sep).join([appRoot, "Data"])


def process_transactions(events, index, type, log, thread_id):
    """
    adds each event given in data to the elastic search cluster.

    :param events: data that contains just events from new relic.
    :return:
    """
    # connect to our es cluster
    es = Elasticsearch([{'host': config.BaseConfig.es_host, 'port': 9200}])

    # add each event to elastic search
    cnt = 1
    for (i, event) in enumerate(events):
        body = {}
        # get all entries and add to a string
        eventItems = event.keys()
        # listOfKeys = []
        # for key in eventItems:
        #     listOfKeys.append(key)
        for key in eventItems:
            if key == 'timestamp':
                t = datetime.datetime.fromtimestamp(float(event[key]) / 1000.) + datetime.timedelta(seconds=25200)
                event[key] = t.isoformat()

            if key not in config.BaseConfig.keysToIgnore:
                body.update({key: event[key]})

        if not es.indices.exists(index):
            # TODO: This index is temporary
            es.indices.create(index,
                              ignore=400,
                              body=config.BaseConfig.elasticSearchMapping
                              )

        try:

            es.index(index=index,
                     doc_type='doc',
                     id=event[config.BaseConfig.elasticSearchIndex[type]["elastic-id"]],
                     body=body
                     )
            # print("{thread} - Added event number - {event} of {total} of "
            #       "{type} events to Elastic Search! ".format(thread=thread_id,
            #                                                  event=i+1,
            #                                                  total=str(len(events)),
            #                                                  type=type
            #                                                  ))
            log.increment_newrelic_requestCount(len(events))
        except KeyError as e:
            try:
                es.index(index=index,
                         doc_type='doc',
                         id=event['appId'],
                         body=body)
                log.increment_newrelic_requestCount(len(events))
                logger.info("{} ***** Error ***** There was an error with this Key {} "
                      "on adding this index : {} ".format(thread_id, e, body))
            except KeyError as f:
                logger.info("{} **** FATAL ****** Not Added to ES. \nNeed to look at the event to find a valid unique ID. "
                      "this is the error. {}".format(thread_id, str(f)))
        cnt = cnt + 1
