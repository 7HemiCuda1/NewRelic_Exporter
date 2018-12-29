# from setup import basedir


class BaseConfig(object):
    SECRET_KEY = "SO_SECURE"
    DEBUG = True
    NR_APIKEY = "72Tk0aXkXF9-WZ98x_TiysGxGt1-UcmR"
    # SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
    # SQLALCHEMY_TRACK_MODIFICATIONS = True
    BLOCK_USER_CREATION = False
    NewRelicApps = {"apps": ["VO API", "DLV API", "AuthNet", "Kount"]}
    NewRelicMicroservices = {"services": ["Tax Service", "Shipping", "Shipping Importer",
                                          "Catalog Importer", "Catalog", "Address",
                                          "Contest Admin", "Contest Executor", "Contest Executor",
                                          "Contest", "VO Content Server"]}
    keysToIgnore = {"host.displayName"}
    es_host = 'localhost'
    #es_host = 'LEI-IT-LT-51693.yleo.us'
    elasticSearchIndex = 'jdtest'
    elasticSearchMapping = {
        # "mappings": {
        #     "_default_": {
        #         "_all": {
        #             "enabled": True,
        #             "norms": False
        #         }, "properties": {
        #             "@timestamp": {
        #                 "type": "date",
        #                 "include_in_all": True
        #             }, "@version": {
        #                 "type": "keyword",
        #                 "include_in_all": True
        #             }
        #         }
        #     }
        # }
    }


class TestingConfig(object):
    """Development configuration."""
    TESTING = True
    DEBUG = True
    WTF_CSRF_ENABLED = False
    # S SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG_TB_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False
