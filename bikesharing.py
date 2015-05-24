__author__ = 'danielcolceag'

import numpy as np
from dateutil import parser
import operator
import csv

dataset = []
data = {}


def getHourOfWeek(date):
    hourOfWeek = 0
    for day in range(int(date.strftime("%u"))-1):
        hourOfWeek += 24
    hourOfWeek += int(date.strftime("%H"))
    return int(hourOfWeek)

def readDataset(filename):
    dataset = []
    print "Loading DataSet...",
    headers = ["Date", "Season", "Holiday", "WorkingDay", "Weather", "Temp", "aTemp", "Humidity", "Windspeed"]

    if filename == 'train':
        headers.append("Casual")
        headers.append("Registered")
        headers.append("Count")

    datefunc = lambda x: parser.parse(x)
    dtype = [("Date", 'object')] + [(header, 'd') for header in headers[1:]]
    dataset = np.genfromtxt((filename + '.csv'), delimiter=',', skip_header=1, names=headers, dtype=dtype,
                            converters={"Date": datefunc})
    print "Done. "
    return dataset


def formatData(dataset, type='train', debug=False):
    data = {}
    for d in dataset:
        season = int(d[1])
        year = int(d[0].strftime("%Y"))
        '''
            http://www.tutorialspoint.com/python/time_strftime.htm

            %U - week number of the current year, starting with the first Sunday as the first day of the first week.

            %V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at
                 least 4 days in the current year, and with Monday as the first day of the week.

           *** %W - week number of the current year, starting with the first Monday as the first day of the first week.

           *** %u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
        '''
        weekNumber = int(d[0].strftime("%W"))
        hourOfWeek = getHourOfWeek(d[0])
        weather = int(d[4])
        count = 0 if (type == 'test') else int(d[11])

        '''
            TODO: Test if repacking of the date is the original
        '''
        data[season, year, hourOfWeek, weekNumber, weather] = (count, d[0])
        #data[season][year][hourOfWeek][weekNumber][weather] = count

    if debug == True:
        for key in sorted(data.iterkeys()):
            print "{}: {}".format(key, data[key])

    return data


def regenerateDate(key):
    pass


def compute(d):
    """
    Predict the count of bikes for the date specified
    Using weighted average.
    :param d: (key, value) in test dataset
    :return: count - number of bikes for key
    """
    # step 1, first breakdown by hour
    # take all days in history and compute the average
    (season, year, hour, weekNumber, weather) = d
    #print "Compute data for ",
    #print season, year, hour, weekNumber, weather,
    #print ". ",
    # iterate through dataset and get the count for same hour, no matter what year, weekNumber and weather

    # filtering phase 1
    keys = []
    for key in sorted(data.iterkeys()):
        (iter_season, iter_year, iter_hour, iter_weekNumber, iter_weather) = key
        if iter_season == season and iter_year <= year and iter_hour == hour and iter_weekNumber <= weekNumber:
            keys.append(key)

    # filtering phase 2
    if len(keys) < 3:
       pass

    # filtering phase 3
    if len(keys) < 3:
        pass

    predictedValue = 0
    if len(keys) != 0:
        #print keys
        #print len(keys),
        #print " values found.",
        values = [data[key][0] for key in sorted(keys)]
        #print values
        weights = [(1 - (round((x * (1.0/len(keys))),2))) for x in range(len(keys))]
        #print weights
        computed = [weights[i] * values[i] for i in range(len(keys))]
        # print computed
        #print sum(computed)
        #print sum(weights)
        predictedValue = sum(computed) / sum(weights)
        #print "Estimated Value is: ",
        #print predictedValue
    return round(predictedValue, 2)

def writeResults(dataset):

    with open('submission.csv', 'wb') as csvfile:
        fieldNames = ['datetime', 'count']
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(fieldNames)
        for key, dictkey in enumerate(dataset):
            writer.writerow([dictkey[1][1].strftime('%Y-%m-%d %H:%M:%S'), dictkey[1][0]])

def main():
    global dataset, data
    dataset = readDataset('train')
    data = formatData(dataset, 'train')

    testdataset = readDataset('test')
    testdata = formatData(testdataset, 'test')

    sortedTestKeys = sorted(testdata.iterkeys())

    print "Computing Results...",
    for i in range(len(sortedTestKeys)):
        testdata[sortedTestKeys[i]] = (compute(sortedTestKeys[i]), testdata[sortedTestKeys[i]][1])
    print "Done."

    print "Writing Results to CSV file...",
    sortedResults = sorted(testdata.items(), key=lambda x: x[1][1])
    writeResults(sortedResults)
    print "Done."

if __name__ == "__main__":
    main()