__author__ = 'danielcolceag'

import numpy as np
from dateutil import parser
import csv
import datetime
from collections import OrderedDict
import random

dataset = []
data = {}
testdataset = {}
testdata = {}

maxCount = 0


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
    return sorted(dataset, key=lambda x: x[0])


def getHourOfWeek(date):
    hourOfWeek = 0
    # day of week number
    dayNumber = int(date.strftime("%u")) - 1
    dayRange = range(dayNumber)
    for day in dayRange:
        hourOfWeek += 24
    hourOfWeek += int(date.strftime("%H"))
    return int(hourOfWeek)


def recoverDate(orig_date, year, hourOfWeek, weekNumber):
    # recover date

    # day of week : 0 - 6
    dayofweek = int(orig_date.strftime("%u")) - 1
    # if the first week (00) starts on another day than Monday, remove the hour difference from the previous days in the
    # week
    day = int((hourOfWeek - (dayofweek - 1) * 24) / 24)
    hour = hourOfWeek % 24
    month = weekNumber / 12 + 1

    return datetime.datetime(year, month, day, hour, 0, 0)


def formatData(dataset, type='train', debug=False):
    global maxCount
    data = {}
    data2 = OrderedDict()

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


        # print recoverDate(d[0], year, hourOfWeek, weekNumber)
        # datestring = date.strftime('yyyyMMdd HH:mm:ss')
        # recoveredDate = parser.parse(datestring)
        # print "date: {} - recoveredDate: {}".format(d[0],recoveredDate)

        data[season, year, hourOfWeek, weekNumber, weather] = (count, d[0])

        # Reformat Data Returned into OrderedDict
        if season not in data2:
            data2[season] = OrderedDict()
        if year not in data2[season]:
            data2[season][year] = OrderedDict()
        if hourOfWeek not in data2[season][year]:
            data2[season][year][hourOfWeek] = OrderedDict()
        if weekNumber not in data2[season][year][hourOfWeek]:
            data2[season][year][hourOfWeek][weekNumber] = OrderedDict()
        if weather not in data2[season][year][hourOfWeek][weekNumber]:
            data2[season][year][hourOfWeek][weekNumber][weather] = OrderedDict()

        data2[season][year][hourOfWeek][weekNumber][weather] = count

        if count > maxCount:
            maxCount = count

    if debug is True:
        for key in sorted(data.iterkeys()):
            print "{}: {}".format(key, data[key])

    return data


def compute(d):
    """
    Predict the count of bikes for the date specified
    Using weighted average.
    :param d: (key, value) in test dataset
    :return: count - number of bikes for key
    """
    # step 1, first breakdown by hour
    (season, year, hour, weekNumber, weather) = d
    # iterate through dataset and get the count for same hour, no matter what year, weekNumber and weather
    # filtering phase 1
    keys = []
    for key in sorted(data.iterkeys()):
        (iter_season, iter_year, iter_hour, iter_weekNumber, iter_weather) = key
        # date din acelasi sezon, indiferent de an, aceeasi ora, indiferent de numarul saptamanii
        if iter_year <= year:
            if iter_season == season:
                if iter_hour == hour:
                    # take in account the last 4-5 weeks
                    if iter_weekNumber <= weekNumber:
                        keys.append(key)
    if len(keys) <= 2:
        # no data in the same season, previous years => check for data in the previous season, same year or previous year
        for key in sorted(data.iterkeys()):
            # date din sezoanele precedente, anul curent
            (iter_season, iter_year, iter_hour, iter_weekNumber, iter_weather) = key
            if iter_year <= year:
                if iter_hour == hour:
                    if iter_weekNumber < weekNumber:
                        keys.append(key)
    '''
    if iter_season == season and iter_year <= year and iter_hour == hour and iter_weekNumber <= weekNumber:
        keys.append(key)
    '''
    """
    # interpolation of data
    if len(keys) < 2:
        # make an average between the next week, same hour and previous week, same hourfor key in sorted(data.iterkeys()):
        prevkeys = []
        nextkeys = []

        # for key in sorted(data.iterkeys()):
        #    (iter_season, iter_year, iter_hour, iter_weekNumber, iter_weather) = key

        #    if iter_season == season and iter_year == year and iter_weekNumber == weekNumber:

        for i in range(5):
            # check if previous 5 weeks have data for the same hour, no matter the weather
            # if we have more than 2 previous keys and 2 future keys with the same weather
            # as the weather we compute for, we pick those and average them to get the predicted value

            weather0 = (season, year, hour, weekNumber - i, 0)
            weather1 = (season, year, hour, weekNumber - i, 1)
            weather2 = (season, year, hour, weekNumber - i, 2)
            weather3 = (season, year, hour, weekNumber - i, 3)
            if weather0 in data:
                prevkeys.append(weather0)
            if weather1 in data:
                prevkeys.append(weather1)
            if weather2 in data:
                prevkeys.append(weather2)
            if weather3 in data:
                prevkeys.append(weather3)

            weather0 = (season,  year,  hour,  weekNumber + i, 0)
            weather1 = (season,  year,  hour,  weekNumber + i, 1)
            weather2 = (season,  year,  hour,  weekNumber + i, 2)
            weather3 = (season,  year,  hour,  weekNumber + i, 3)
            if weather0 in data:
                nextkeys.append(weather0)
            if weather1 in data:
                nextkeys.append(weather1)
            if weather2 in data:
                nextkeys.append(weather2)
            if weather3 in data:
                nextkeys.append(weather3)
        prevvalues = [data[key][0] for key in prevkeys]
        nextvalues = [data[key][0] for key in nextkeys]
        minlen = min(len(prevvalues), len(nextvalues))
        weights = [(1 - (round((x * (1.0/minlen)), 2))) for x in range(minlen)]
        prevsum = round(sum([weights[i] * prevvalues[i] for i in range(minlen)]),2)
        nextsum = round(sum([weights[i] * nextvalues[i] for i in range(minlen)]),2)
        predictedValue = 0
        if prevsum < nextsum:
            predictedValue = round(((prevsum * 0.5 + nextsum) / 1.5), 2)
        else:
            predictedValue = round(((prevsum + nextsum * 0.5) / 1.5), 2)

        if predictedValue > 0:
            return predictedValue
    """
    predictedValue = 0
    if len(keys) >= 1:
        # print keys
        # print len(keys),
        # print " values found.",
        values = [data[key][0] for key in sorted(keys)]
        # print values
        weights = [(1 - (round((x * (1.0 / len(keys))), 2))) for x in range(len(keys))]
        # print weights
        computed = [weights[i] * values[i] for i in range(len(keys))]
        # print computed
        # print sum(computed)
        # print sum(weights)
        predictedValue = sum(computed) / sum(weights)
        # print "Estimated Value is: ",
        # print predictedValue
    return round(predictedValue, 2)


def writeDataset(dataset):
    with open('dataset.csv', 'wb') as csvfile:
        fieldNames = ['datetime', 'count']
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(fieldNames)
        for key, dictkey in enumerate(dataset):
            writer.writerow([dictkey[0].strftime('%Y-%m-%d %H:%M:%S'), dictkey[1]])


def writeResults(dataset):
    with open('submission.csv', 'wb') as csvfile:
        fieldNames = ['datetime', 'count']
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(fieldNames)
        for key, dictkey in enumerate(dataset):
            writer.writerow([dictkey[1][1].strftime('%Y-%m-%d %H:%M:%S'), dictkey[1][0]])


def main():
    global dataset, data, testdataset, testdata
    dataset = readDataset('train')
    data = formatData(dataset, 'train')
    sortedData = sorted(data.items(), key=lambda x: x[0])
    writeResults(sortedData)
    testdataset = readDataset('test')
    testdata = formatData(testdataset, 'test')

    sortedTestKeys = sorted(testdata.iterkeys())
    sortedTestData = sorted(testdata.iteritems(), key=lambda x: x[1])
    print "Computing Results...",
    for d in sortedTestData:
        testdata[d[0]] = (compute(d[0]), d[1][1])
        data[d[0]] = testdata[d[0]]
    print "Done."

    print "Writing Results to CSV file...",
    sortedResults = sorted(testdata.items(), key=lambda x: x[1][1])

    writeResults(sortedResults)
    print "Done."


if __name__ == "__main__":
    main()