# from application.FrontEndMain import app

# app = app
from backend.Features import newrelic
from backend.Classes import Query
import datetime

save_location = '/Volumes/it-dept/QA/NewRelic-ExportData'
# cur_file = os.path.realpath(__file__)
# appRoot = cur_file
# appRoot = getRoot(appRoot) #temp test
appRoot = save_location

# pass Date and app from user form.
query = Query.Query()
livetimeframe = datetime.datetime.utcnow()
starttime = datetime.datetime.utcnow() - datetime.timedelta(seconds=15)
# query.setStartDate(datetime.datetime(2018, 11, 22, 23, 00, 00))
# query.setEndDate(datetime.datetime(2018, 11, 22, 23, 00, 1))
query.setStartDate(starttime)
query.setEndDate(livetimeframe)
newrelic.collectDataforTest(query, appRoot)
print("Completed getting Data for the following date range {} to {}".format(query.startDate, query.endDate))
