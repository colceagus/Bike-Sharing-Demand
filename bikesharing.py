__author__ = 'danielcolceag'

import numpy as np
from dateutil import parser

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
    headers = ["Date", "Season", "Holiday", "WorkingDay", "Weather", "Temp", "aTemp", "Humidity", "Windspeed", "Casual",
               "Registered", "Count"]
    datefunc = lambda x: parser.parse(x)
    dtype = [("Date", 'object')] + [(header, 'd') for header in headers[1:]]
    dataset = np.genfromtxt(filename, delimiter=',', skip_header=1, names=headers, dtype=dtype,
                            converters={"Date": datefunc})
    print "Done. "
    return dataset


def formatData(dataset):
    data = {}
    for d in dataset:
        season = int(d[1])
        year = int(d[0].strftime("%Y"))
        '''
            http://www.tutorialspoint.com/python/time_strftime.htm

            %U - week number of the current year, starting with the first Sunday as the first day of the first week.

            %V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at
                 least 4 days in the current year, and with Monday as the first day of the week.

            %W - week number of the current year, starting with the first Monday as the first day of the first week.

            %u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
        '''
        weekNumber = int(d[0].strftime("%W"))
        hourOfWeek = getHourOfWeek(d[0])
        weather = int(d[4])
        count = int(d[11])
        data[season, year, hourOfWeek, weekNumber, weather] = count

    for key in sorted(data.iterkeys()):
        print "{}: {}".format(key, data[key])

def main():
    global dataset, data
    dataset = readDataset('train.csv')
    data = formatData(dataset)


if __name__ == "__main__":
    main()