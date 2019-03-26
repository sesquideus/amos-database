import sys
import os
import requests
import argparse
import numpy as np

def main():
    args = getArgs()
    data = makeData()
    send('http://127.0.0.1:4805/meteors/receive', data, args.filename)

def getArgs():
    parser = argparse.ArgumentParser(
        description = "AMOS HTTP POST request testbed",
    )
    parser.add_argument('filename', type = argparse.FileType('rb')) 
    return parser.parse_args()

def send(url, data, image):
    print(url)
    print(data)
    print(image)
    r = requests.post(url, data = data, files = {'file': ('image', image, 'image/png')})
    print(r.text)
    print(r.status_code)

def makeData():
    return {
        'mag': np.random.pareto(2) * 0.01,
        'az': np.random.uniform(0, 360),
        'alt': np.arccos(np.random.uniform(0, 1)),
    }

main()
