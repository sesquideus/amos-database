import sys
import os
import requests
import argparse
import numpy as np

def main():
    args = getArgs()
    data = makeData()
    send('http://192.168.0.177:4805/receive', data, args.filename)

def getArgs():
    parser = argparse.ArgumentParser(
        description = "AMOS HTTP POST request testbed",
    )
    parser.add_argument('filename', type = argparse.FileType('rb')) 
    return parser.parse_args()

def send(url, data, image):
    r = requests.post(url, files = {'file': ('image.jpg', image)})
    print(r.text)
    print(r.status_code)

def makeData():
    return {
        'mag': np.random.pareto(2) * 0.01,
        'az': np.random.uniform(0, 360),
        'alt': np.arccos(np.random.uniform(0, 1)),
    }

main()
