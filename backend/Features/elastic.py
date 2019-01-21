# make sure ES is up and running
import requests, re, os
from elasticsearch import Elasticsearch
from backend.Classes import JSON
from backend.HelperFunctions import Common
import config, time
import datetime
import pytz

cur_file = os.path.realpath(__file__)
appRoot = Common.Common.getRoot(cur_file)

dataDir = (os.sep).join([appRoot, "Data"])


def get_json_from_file(dir):
    """

    :param dir: location of json files
    :return data : json from json files
    """
    # TODO: Need to grab a specific amount so dont use too much memory.
    files = os.listdir(dir)

    data = {}
    for f in files:
        if f.endswith('.json'):
            new_data = JSON.load_json_file(f, dataDir)
            file_with_path = (os.sep).join([dataDir, f])
            file_with_new_path = (os.sep).join([dataDir, f + '.processed'])
            data.update(new_data)
            # os.rename(file_with_path, file_with_new_path)
    # TODO: Cleanup this to run for real.
    return data


def process_transactions(events, index, type, log):
    """
    adds each event given in data to the elastic search cluster.

    :param events: data that contains just events from new relic.
    :return:
    """
    # connect to our es cluster
    es = Elasticsearch([{'host': config.BaseConfig.es_host, 'port': 9200}])

    # add each event to elastic search
    cnt = 1
    for event in events:
        body = {}
        # get all entries and add to a string
        eventItems = event.keys()
        # print("event keys ")
        listOfKeys = []
        for key in eventItems:
            listOfKeys.append(key)
        for key in eventItems:
            if key == 'timestamp':
                t = datetime.datetime.fromtimestamp(float(event[key]) / 1000.) + datetime.timedelta(seconds=25200)
                event[key] = t.isoformat()

            if key not in config.BaseConfig.keysToIgnore:
                body.update({key: event[key]})

        if not es.indices.exists(index):
            # TODO: This index is temporary
            es.indices.create(index, ignore=400, body=config.BaseConfig.elasticSearchMapping)

        try:
            es.index(index=index, doc_type='doc', id=event[config.BaseConfig.elasticSearchIndex[type]["elastic-id"]], body=body)
            print("- Added - {event} {type} events to Elastic Search! ".format(event=str(len(events)), type=type))
            log.increment_newrelic_requestCount(len(events))
        except KeyError as e:
            try:
                es.index(index=index, doc_type='doc', id=event['appId'], body=body)
                log.increment_newrelic_requestCount(len(events))
                print("***** Error ***** There was an error with this Key {} on adding this index : {} ".format(e, body))
            except KeyError as f:
                print("**** Need to look at the event to find a valid unique ID. this is the error. " + str(f) )
        cnt = cnt + 1


#if __name__ == "__main__":
    # get json from files
    #data = get_json_from_file(dataDir)

    # TODO: parse json for just the events.
    #events = Common.Common.get_events_from_json(data)
    #print("got events")
    #process_transactions(events)
