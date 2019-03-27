import sys
import os
import datetime
import requests
import argparse
import pytz
from pprint import pprint as pp
import numpy as np

def main():
    args = getArgs()
    data = makeData()
    send('http://192.168.0.177:4805/meteors/receive', data, args.filename)

def getArgs():
    parser = argparse.ArgumentParser(
        description = "AMOS HTTP POST request testbed",
    )
    parser.add_argument('filename', type = argparse.FileType('rb')) 
    return parser.parse_args()

def send(url, data, image):
    pp(url)
    pp(data)
    pp(image)
    r = requests.post(url, data = data, files = {'file': ('image', image, 'image/png')})
    print(r.text)
    print(r.status_code)

def makeData():
    timestamp           = datetime.datetime.now(tz = pytz.UTC) - datetime.timedelta(days = np.random.uniform(0, 1))
    velocityX           = np.random.normal(0, 20000)
    velocityY           = np.random.normal(0, 20000)
    velocityZ           = np.random.normal(0, 20000)

    beginningLatitude   = np.random.uniform(20, 60)
    beginningLongitude  = np.random.uniform(-20, 30)
    beginningAltitude   = np.random.normal(100000, 10000)
    beginningTime       = timestamp

    timeToLightmax      = np.random.uniform(0.1, 0.5)
    lightmaxLatitude    = beginningLatitude + velocityX * timeToLightmax / 100000
    lightmaxLongitude   = beginningLongitude + velocityY * timeToLightmax / 100000
    lightmaxAltitude    = beginningAltitude + velocityZ * timeToLightmax

    timeToEnd           = np.random.uniform(0.6, 1)
    endLatitude         = beginningLatitude + velocityX * timeToEnd / 100000
    endLongitude        = beginningLongitude + velocityY * timeToEnd / 100000
    endAltitude         = beginningAltitude + velocityZ * timeToEnd
    magnitude           = -2.5 * np.log(np.random.pareto(2) * 10) + 5

    return {
        'timestamp'             : timestamp.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
        'beginningLatitude'     : beginningLatitude,
        'beginningLongitude'    : beginningLongitude,
        'beginningAltitude'     : beginningAltitude,
        'beginningTime'         : beginningTime.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
        'velocityX'             : velocityX,
        'velocityY'             : velocityY,
        'velocityZ'             : velocityZ,

        'lightmaxLatitude'      : lightmaxLatitude,
        'lightmaxLongitude'     : lightmaxLongitude,
        'lightmaxAltitude'      : lightmaxAltitude,
        'lightmaxTime'          : (beginningTime + datetime.timedelta(seconds = timeToLightmax)).strftime("%Y-%m-%d %H:%M:%S.%f%z"),

        'endLatitude'           : endLatitude,
        'endLongitude'          : endLongitude,
        'endAltitude'           : endAltitude,
        'endTime'               : (beginningTime + datetime.timedelta(seconds = timeToEnd)).strftime("%Y-%m-%d %H:%M:%S.%f%z"),

        'magnitude'             : magnitude,
    }

main()
