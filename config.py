# from setup import basedir
import datetime, os
from backend.HelperFunctions import Common

class BaseConfig(object):
    ProdEnvironment = True
    SECRET_KEY = "SO_SECURE"
    # Used in logging events.
    DEBUG = True
    # This is the location the code is on local machine.
    appRoot = Common.Common.get_parent(os.path.realpath(__file__))
     # '/Volumes/it-dept/QA/NewRelic-ExportData'

    NR_APIKEY = "74qMRuukUiP4xaFbdlG8CaK4xCPuTVzd"
    BLOCK_USER_CREATION = False
    # decides if we should save files for backup as well as the elastic search.
    LogBackup = False
    # the date for the index
    indexDate = datetime.datetime.today().strftime("%Y-%m-%d")
    # the folowing dicts are used in the NRQL queries to know what apps to use for each env.

    # Prod Apps
    NewRelicApps = {
        "apps": [
            # "Address",
            # "AuthNet",
            # "Catalog Importer",
            # "Catalog",
            # "Classic DLV",
            # "Contest Admin",
            # "Contest Executor",
            # "Contest",
            # "Customer Programs Processor",
            # "Customer Programs",
            # "DLV API",
            # "Fraud",
            # "Kount",
            # "Notifications Tasks",
            # "Oily API",
            # "Order Payment",
            # "OrderFulfillmentAPI",
            # "Payment Service",
            # "Podcast Blog",
            # "Prod Queuing",
            # "Product Recommendation",
            # "Reference Importer",
            # "Reference Service",
            # "Shipping Importer",
            "Shipping",
            # "Tax Service",
            # "VO API",
            # "VO Content Server",
            # "VO.DLV Content Server",
            # "WWW Content Server",
            # "YL API",
            # "YLPC.ShipmentFulfillmentAPI",
            "YLPC"
        ]
    }

    SystemSampleApps = {
        "apps":
        [
            # "VO NSB Distributor",
            # "Kount",
            # "Cymbeo",
            # "ProPay",
            # "Classic DLV",
            # "VO Content",
            # "SQL",
            # "VO Micro Services",
            # "Taiwan",
            # "VO ACL Worker",
            # "VO",
            # "VO API",
            # "LIMS",
            "ORAPRD DB",
            # "Vertex",
            # "ORAVOPRD DB",
            # "Accounting",
            # "CVENT-API",
            # "VO NSB Worker",
            # "VO DLV API",
            # "Events",
            # "VO NSB Audit",
            # "Communication",
            # "GreatPlains",
            # "Classic",
            # "Oracle Apps",
            "CMS-Global"
        ]
    }

    ProcessSampleApp = {
        "apps":
        [
            # "VO NSB Distributor",
            # "LabVantage",
            # "Kount",
            # "Cymbeo",
            # "ProPay",
            # "Classic DLV",
            # "VO Memcached",
            # "VO Content",
            # "SQL",
            # "VO Micro Services",
            # "Taiwan",
            # "VO ACL Worker",
            # "VO",
            # "VO API",
            # "ORAPRD DB",
            # "LIMS",
            # "Vertex",
            # "ORAVOPRD DB",
            # "Accounting",
            # "BI",
            # "CVENT-API",
            # "VO NSB Worker",
            # "VO DLV API",
            # "Events",
            # "VO NSB Audit",
            # "Communication",
            # "GreatPlains",
            # "Zerto",
            # "Classic",
            "CMS-Global",
            "Oracle Apps"
        ]
    }

    NewRelicMicroservices = {"services":
        [
            # "prod_payments",
            # "prod_jmcustomersync",
            # "prod_address",
            # "prod_contest",
            # "prod_chinaagreementenforcement",
            # "prod_analytics",
            # "prod_notificationstasks",
            # "prod_invoicing",
            # "prod_contest-executor",
            # "prod_customerprograms-processor",
            # "prod_shipping_importer",
            # "prod_jmcommissionsync",
            # "prod_cybersource",
            # "prod_tax",
            # "prod_catalog",
            # "prod_jmordersync",
            # "prod_queuing",
            # "prod_authnet",
            # "prod_fraud",
            # "prod_contest-admin",
            # "prod_reference_importer",
            # "prod_customerprograms",
            # "prod_catalog-importer",
            # "prod_reference",
            # "prod_orderpayment",
            "prod_product-recommendation",
            "prod_shipping"
        ]
    }

    keysToIgnore = {"host.displayName",
                    "criticalViolationCount",
                    "warningViolationCount",
                    "diskUtilizationPercent",
                    "containerLabel_com.docker.swarm.task",
                    "containerLabel_com.docker.ucp.collection"}

    # ELASTIC SEARCH
    #es_host = 'localhost'
    #es_host = 'LEI-IT-LT-51693.yleo.us'
    es_host = 'slcesprd230.yleo.us'
    # es_host = '10.1.11.230'
    elasticSearchIndex = {
        "transactions": {
            "select": "*",
            "index-name": "test-transaction-",
            "elastic-id": "tripId",
            "nrqlQuery": "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' WHERE appName = '{appname}' and error IS NULL ",
            "nrqlQueryFrom": "Transaction",
            "nrqlQueryWhere":  "appName ",
            "nrqlQueryPostWhere": " and error IS NULL ",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "transaction-error": {
            "select": "*",
            "index-name": "test-transaction-error-",
            "elastic-id": "tripId",
            "nrqlQuery": "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' WHERE appName = '{appname}' and error IS NULL ",
            "nrqlQueryFrom": "Transaction",
            "nrqlQueryWhere": "appName ",
            "nrqlQueryPostWhere": " and error IS NOT NULL ",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "process-micro": {
            "select": "*",
            "index-name": "test-processstat-microservice-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM ProcessSample SINCE '{startDate}' until '{endDate}' WHERE `containerLabel_com.docker.swarm.service.name` LIKE '%{appname}%' and errorMessage IS NULL ",
            "nrqlQueryFrom": "ProcessSample",
            "nrqlQueryWhere": "`containerLabel_com.docker.swarm.service.name`",
            "nrqlQueryPostWhere": " and errorMessage IS NULL",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "process-app": {
            "select": "*",
            "index-name": "test-processstat-apps-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM ProcessSample SINCE '{startDate}' until '{endDate}' WHERE application LIKE '%{application}%' and errorMessage IS NULL ",
            "nrqlQueryFrom": "ProcessSample",
            "nrqlQueryWhere": "application ",
            "nrqlQueryPostWhere": "",
            "memberIdCheck": "",
            "memberIdWhere": ""
        },
        "host": {
            "select": "*",
            "index-name": "test-hoststat-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM SystemSample SINCE '{startDate}' until '{endDate}' WHERE application = '{appname}'",
            "nrqlQueryFrom": "SystemSample",
            "nrqlQueryWhere": "application ",
            "nrqlQueryPostWhere": "",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        }
    }

    url = "https://insights-api.newrelic.com/v1/accounts/1139936/query"
    headers = {
        'X-Query-Key': NR_APIKEY,
        'Accept': "application/json",
        'cache-control': "no-cache"
    }

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

    WTF_CSRF_ENABLED = False
    # S SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    DEBUG_TB_ENABLED = True
    PRESERVE_CONTEXT_ON_EXCEPTION = False

    ProdEnvironment = True
    SECRET_KEY = "SO_SECURE"
    # Used in logging events.
    DEBUG = True
    # This is the location the code is on local machine.
    appRoot = Common.Common.get_parent(os.path.realpath(__file__))
    # '/Volumes/it-dept/QA/NewRelic-ExportData'

    NR_APIKEY = "74qMRuukUiP4xaFbdlG8CaK4xCPuTVzd"
    BLOCK_USER_CREATION = False
    # decides if we should save files for backup as well as the elastic search.
    LogBackup = False
    # the date for the index
    indexDate = datetime.datetime.today().strftime("%Y-%m-%d")
    # the folowing dicts are used in the NRQL queries to know what apps to use for each env.

    #ProdClone Apps
    NewRelicApps = {
        "apps": [
            "Clone Address",
            "Clone API",
            "Clone AuthNet",
            "Clone Catalog Importer",
            "Clone Catalog",
            "Clone Contest Admin",
            "Clone Contest Executor",
            "Clone Contest",
            "Clone Customer Programs Processor",
            "Clone Customer Programs",
            "Clone Cybersource Service",
            "Clone DLV API",
            "Clone Fraud",
            "Clone JoyMain Commission Sync",
            "Clone JoyMain Customer Sync",
            "Clone JoyMain Order Sync",
            "Clone Order Payment",
            "Clone Payment Service",
            "Clone Product Recommendation",
            "Clone Queuing",
            "Clone Reference Importer",
            "Clone Reference Service",
            "Clone Shipping Importer",
            "Clone Shipping",
            "Clone Tax Service",
            "Clone VO API"
        ]
    }

    keysToIgnore = {"host.displayName",
                    "criticalViolationCount",
                    "warningViolationCount",
                    "diskUtilizationPercent",
                    "containerLabel_com.docker.swarm.task",
                    "containerLabel_com.docker.ucp.collection"}
    # ELASTIC SEARCH
    #es_host = 'localhost'
    #es_host = 'LEI-IT-LT-51693.yleo.us'
    es_host = 'slcesprd230.yleo.us'
    # es_host = '10.1.11.230'
    elasticSearchIndex = {
        "transactions": {
            "select": "*",
            "index-name": "test-transaction-",
            "elastic-id": "tripId",
            "nrqlQuery": "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' WHERE appName = '{appname}' and error IS NULL ",
            "nrqlQueryFrom": "Transaction",
            "nrqlQueryWhere":  "appName ",
            "nrqlQueryPostWhere": " and error IS NULL ",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "transaction-error": {
            "select": "*",
            "index-name": "test-transaction-error-",
            "elastic-id": "tripId",
            "nrqlQuery": "SELECT * FROM Transaction SINCE '{startDate}' until '{endDate}' WHERE appName = '{appname}' and error IS NULL ",
            "nrqlQueryFrom": "Transaction",
            "nrqlQueryWhere": "appName ",
            "nrqlQueryPostWhere": " and error IS NOT NULL ",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "process-micro": {
            "select": "*",
            "index-name": "test-processstat-microservice-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM ProcessSample SINCE '{startDate}' until '{endDate}' WHERE `containerLabel_com.docker.swarm.service.name` LIKE '%{appname}%' and errorMessage IS NULL ",
            "nrqlQueryFrom": "ProcessSample",
            "nrqlQueryWhere": "`containerLabel_com.docker.swarm.service.name`",
            "nrqlQueryPostWhere": " and errorMessage IS NULL",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        },
        "process-app": {
            "select": "*",
            "index-name": "test-processstat-apps-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM ProcessSample SINCE '{startDate}' until '{endDate}' WHERE application LIKE '%{application}%' and errorMessage IS NULL ",
            "nrqlQueryFrom": "ProcessSample",
            "nrqlQueryWhere": "application ",
            "nrqlQueryPostWhere": "",
            "memberIdCheck": "",
            "memberIdWhere": ""
        },
        "host": {
            "select": "*",
            "index-name": "test-hoststat-",
            "elastic-id": "entityId",
            "nrqlQuery": "SELECT * FROM SystemSample SINCE '{startDate}' until '{endDate}' WHERE application = '{appname}'",
            "nrqlQueryFrom": "SystemSample",
            "nrqlQueryWhere": "application ",
            "nrqlQueryPostWhere": "",
            "memberIdCheck": "uniques(MemberId)",
            "memberIdWhere": "and MemberId = '"
        }
    }

    url = "https://insights-api.newrelic.com/v1/accounts/1139936/query"
    headers = {
        'X-Query-Key': NR_APIKEY,
        'Accept': "application/json",
        'cache-control': "no-cache"
    }
    # Clone
    NewRelicMicroservices = {"services":
        [
            "Clone Contest",
            "Clone Address",
            "Clone Reference Importer",
            "Clone Shipping",
            "Clone API",
            "Clone Payment Service",
            "Clone Queuing",
            "Clone Contest Executor",
            "Clone Order Payment",
            "Clone Catalog Importer",
            "Clone Contest Admin",
            "Clone AuthNet",
            "Clone Reference Service",
            "Clone Customer Programs",
            "Clone VO API",
            "Clone Fraud",
            "Clone Catalog",
            "Clone Shipping Importer",
            "Clone Tax Service",
            "Clone DLV API",
            "Clone Customer Programs Processor",
            "Clone Product Recommendation"
        ]
    }

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