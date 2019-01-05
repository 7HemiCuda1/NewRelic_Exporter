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
#livetimeframe = datetime.datetime.utcnow() + datetime.timedelta(seconds=25200)
#starttime = datetime.datetime.utcnow() - datetime.timedelta(seconds=3600) + datetime.timedelta(seconds=25200)

#query.setStartDate(starttime)
#query.setEndDate(livetimeframe)

# Add the start time and end time in MST,
query.setStartDate(datetime.datetime(2019, 1, 4, 14, 00, 00) + datetime.timedelta(seconds=25200))
query.setEndDate(datetime.datetime(2019, 1, 4, 14, 10, 00)+ datetime.timedelta(seconds=25200))
print("Starting process with this date range, Start: {} EndTime: {}".format(str(query.startDate), str(query.endDate)))
newrelic.collectDataforTest(query, appRoot)
print("Completed getting Data for the following date range {} to {}".format(query.startDate, query.endDate))
