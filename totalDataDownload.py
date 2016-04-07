
# initialization

from datetime import date, timedelta as td
import urllib2
import csv
from datetime import datetime
from dateutil import tz
import time


# define start and end dates

startDate = date(2013, 4, 29)
endDate = date(2013, 11, 8)
delta = endDate - startDate

# read in site names, site code, and type
# there are two types of URLs
dictNameCode = dict()
dictNameType = dict()
siteList = list()

with open('Met Site Names.csv', mode = 'r') as infile:
    reader = csv.reader(infile)
    for rows in reader:
        siteList.append(rows[0])
        dictNameCode.update({rows[0]:rows[1]})
        dictNameType.update({rows[0]:rows[2]})

# this function returns a url 
def makeURL(date, site):  
    if (dictNameType[site] == '1'):  
        url = 'http://www.wunderground.com/weatherstation/WXDailyHistory.asp?ID=' + \
        dictNameCode[site] + '&day=' + \
        str(date.day)+'&month='+str(date.month)+'&year='+str(date.year)+'&graphspan=day&format=1'
    elif (dictNameType[site] == '0'):
        url = 'http://www.wunderground.com/history/airport/' + \
        dictNameCode[site] + '/' +str(date.year) + '/' + \
        str(date.month) + '/' + str(date.day) +  \
        '/DailyHistory.html?req_city=Cypress&req_state=CA&req_statename=&reqdb.zip=90630&reqdb.magic=1&reqdb.wmo=99999&format=1'
    return url

# this function parse the text file and save data
def saveData(target_url, site):
    connection = False
    while not connection:
        try:    
            textFile = urllib2.urlopen(target_url)
            connection = True
        except:
            time.sleep(5)
            print 'sleeping ...'
            pass
    # these two lines are used to convert time from UTC to Pacific Time
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('America/Los_Angeles')
    for line in textFile:
        t = line.split(',')
        if len(t)>1:
            if (dictNameType[site] == '1'):
                if t[0] == 'Time':
                    continue
                else:
                    tTime = t[0]
                    tTemp = t[1]
                    tDew = t[2]
                    tPre = t[3]
                    tWD = t[4]
                    tWDD = t[5]
                    tWS = t[6]
                    tWSG = t[7]
                    tHum = t[8]
            elif (dictNameType[site] == '0'):
                if t[0] == 'TimePDT' or t[0] == 'TimePST':
                    continue
                else:
                    tTimeUTC0 = t[13].replace('<br />\n','')
                    if t[13] == 'DateUTC':
                        continue
                    else:
                        if len(tTimeUTC0) == 19:
                            tTimeUTC = datetime.strptime(tTimeUTC0, '%Y-%m-%d %H:%M:%S')
                        elif len(tTimeUTC0) == 16:
                            tTimeUTC = datetime.strptime(tTimeUTC0, '%Y-%m-%d %H:%M')
                        tTimeUTC2 = tTimeUTC.replace(tzinfo = from_zone)
                        tTimeUTC3 = tTimeUTC2.astimezone(to_zone)
                        tTime = tTimeUTC3.strftime('%m/%d/%Y %H:%M')
                        tTemp = t[1]
                        tDew = t[2]
                        tPre = t[4]
                        tWD = t[6]
                        tWDD = t[12]
                        tWS = t[7]
                        tWSG = t[8]
                        tHum = t[3]
            newRow = (site,tTime, tTemp, tDew, tPre, tWD, tWDD, tWS, tWSG, tHum,'\n')
            f.write(','.join(newRow))


# define the header
header = ('Site','Time', 'TemperatureF', 'DewpointF', 'PressureIn','WindDirection',
         'WindDirectionDegrees','WindSpeedMPH', 'WindSpeedGustMPH',
         'Humidity', '\n')

for site in siteList:
    filename = site + '_new.csv'
    f = open(filename, 'w')
    f.write(','.join(header))
    for i in range(delta.days+1):
        date = startDate+td(days=i)
        print 'Working on', site, date
        u = makeURL(date, site)
        saveData(u, site)
        time.sleep(1)
    f.close()
    print site, 'is Done!'

