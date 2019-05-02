### Temporary testing script to generate meteors for AMOS database. Not suitable for production!

import sys
import os
import datetime
import random
import requests
import argparse
import pytz
from pprint import pprint as pp
import numpy as np

def main():
    args = getArgs()
    meteor = makeMeteor()
    response = send(f'http://{args.ip}:4805/meteor/receive', meteor, args.filename)
    print(response)

def getArgs():
    parser = argparse.ArgumentParser(
        description = "AMOS HTTP POST request testbed",
    )
    parser.add_argument('ip', type = str)
    parser.add_argument('filename', type = argparse.FileType('rb')) 
    return parser.parse_args()

def printRequest(req):
    print("HTTP/1.1 {method} {url}\n{headers}\n\n{body}".format(
        method = req.method,
        url = req.url,
        headers = '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body = req.body,
    ))

def send(url, data, image):
    s = requests.Session()
    r = requests.Request('POST', url, data = data, files = {'file': ('image', image, 'image/png')}, auth = ('amos', 'meteorujeme'))
    prepared = r.prepare()
    printRequest(prepared)

    response = s.send(prepared)
    print(response.status_code)
    print(response.text)
    print(response.headers['Location'])

def makeMeteor():
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

def makeSighting(station):
    timestamp           = datetime.datetime.now(tz = pytz.UTC) - datetime.timedelta(days = np.random.uniform(0, 1))

    beginningAzimuth    = np.random.uniform(0, 360)
    beginningAltitude   = np.degrees(np.arcsin(np.random.uniform(0, 1)))
    beginningTime       = timestamp

    daz                 = np.random.normal(0, 30)
    dalt                = np.random.normal(0, 30)

    timeToLightmax      = np.random.uniform(0.1, 0.5)
    lightmaxAzimuth     = beginningAzimuth + daz * timeToLightmax
    lightmaxAltitude    = beginningAltitude + dalt * timeToLightmax

    timeToEnd           = np.random.uniform(0.6, 1)
    endAzimuth          = beginningAzimuth + daz * timeToEnd
    endAltitude         = beginningAltitude + dalt * timeToEnd
    
    angularSpeed        = np.random.normal(0, 30)
    magnitude           = -2.5 * np.log(np.random.pareto(2) * 10) + 5

    return {
        'timestamp'             : timestamp.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
        'beginningAzimuth'      : beginningAzimuth,
        'beginningAltitude'     : beginningAltitude,
        'beginningTime'         : beginningTime.strftime("%Y-%m-%d %H:%M:%S.%f%z"),

        'lightmaxAzimuth'       : lightmaxAzimuth,
        'lightmaxAltitude'      : lightmaxAltitude,
        'lightmaxTime'          : (beginningTime + datetime.timedelta(seconds = timeToLightmax)).strftime("%Y-%m-%d %H:%M:%S.%f%z"),

        'endAzimuth'            : endAzimuth,
        'endAltitude'           : endAltitude,
        'endTime'               : (beginningTime + datetime.timedelta(seconds = timeToEnd)).strftime("%Y-%m-%d %H:%M:%S.%f%z"),

        'angularSpeed'          : angularSpeed,
        'magnitude'             : magnitude,
        'station'               : station,
    }

main()
