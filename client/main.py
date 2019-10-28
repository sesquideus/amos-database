#!/usr/bin/env python

import argparse
import requests
import yaml
import dotmap
import asyncio
import logging
import datetime
import pytz
import time
import random
import numpy as np

import logger
import colour as c

from apscheduler.schedulers.background import BackgroundScheduler
from requests.exceptions import ConnectTimeout, ConnectionError 

log = logger.setupLog('root')

class Monitor():
    def __init__(self):
        self.args = self.getArgs()
        self.config = self.loadConfigFile(self.args.config)
        log.info("Initializing monitor")
        self.overrideConfig()

        self.address = f"http://{self.config.server.ip}:{self.config.server.port}/station/{self.config.station.id}"
        self.printInfo()
        
        self.scheduler = BackgroundScheduler()

        self.sendStatus()
        self.scheduler.add_job(self.sendStatus, trigger = 'interval', seconds = self.config.interval)
        
        self.sendSighting()
        self.scheduler.add_job(self.sendSighting, trigger = 'interval', seconds = self.config.interval * random.uniform(5, 10))
        self.scheduler.start()

        while True:
            time.sleep(1)

    def printInfo(self):
        """
            Prints configuration options.
            Should be called *after* config is loaded and overridden by command line options
        """
        log.info(f"Remote address is {c.path(self.address)}")
        log.info(f"Sending a status report every {c.param(self.config.interval)} seconds")

    def getLidStatus(self):
        """
            Get AMOS lid status
            Currently a mockup!
        """
        return "C"

    def getSynologyStatus(self):
        return "1"

    def getHeatingStatus(self):
        return "1"

    def getTemperature(self):
        return random.gauss(0, 10)

    def getHumidity(self):
        return random.uniform(0, 100)

    def getPressure(self):
        return random.gauss(100000, 1000)

    def status(self):
        return {
            'station':      self.config.station.id,
            'timestamp':    datetime.datetime.now(pytz.utc).isoformat(),
            'status':       'ok',
            'lid':          self.getLidStatus(),
            'synology':     self.getSynologyStatus(),
            'heating':      self.getHeatingStatus(),
            'temperature':  self.getTemperature(),
            'pressure':     self.getPressure(),
            'humidity':     self.getHumidity(),
        }

    def longtermStatus(self):
        return {
            'disk':         {
                                'total':        4.34e12,
                                'utilized':     3.12e12,
                            },
            'memory':       {
                                'total':        4.5*2**32,
                                'utilized':     8*2**32,
                            },
        }

    def makeSighting(station):
        timestamp           = datetime.datetime.now(tz = pytz.UTC) - datetime.timedelta(days = np.random.uniform(0, 1))
    
        alt0                = np.degrees(np.arcsin(np.random.random()))
        az0                 = np.random.random() * 360.0
        dalt                = np.random.normal(0, 3)
        daz                 = np.random.normal(0, 3)

        mag                 = 6 - 3 * np.random.pareto(2.3)
        cnt                 = int(np.floor(np.random.pareto(1.3) + 5))

        #mag = mag + np.random.random() if np.random.random() < x / cnt else mag - np.random.random()

        return {
            'timestamp'             : timestamp.strftime("%Y-%m-%d %H:%M:%S.%f%z"),
            'angularSpeed'          : np.random.normal(20, 5),
            'frames'                : [{
                                            'timestamp':            (timestamp + datetime.timedelta(seconds = x * 0.05)).strftime("%Y-%m-%d %H:%M:%S.%f%z"),
                                            'x':                    np.random.randint(0, 1600),
                                            'y':                    np.random.randint(0, 1200),
                                            'altitude':             alt0 + x * dalt,
                                            'azimuth':              az0 + x * daz,
                                            'magnitude':            np.random.normal(0, 2),
                                        } for x in np.arange(0, cnt)],
        }

    @classmethod
    def loadConfigFile(self, file):
        """
            Load the configuration file and return it as a static DotMap
        """
        try:
            config = yaml.safe_load(file)
        except FileNotFoundError as e:
            log.error("Could not load configuration file {}: {}".format(file, e))
            raise exceptions.CommandLineError()
        except yaml.composer.ComposerError as e:
            log.error("YAML composer error")
            raise exceptions.ConfigurationError(e) from e

        return dotmap.DotMap(config, _dynamic = False)
 
    def sendStatus(self):
        log.debug(f"Sending a status report")
        self.sendJSON(f"{self.address}/status/", self.status())

    def sendSighting(self):
        log.debug(f"Sending a sighting")
        self.sendJSON(f"{self.address}/sighting/", self.makeSighting())

    def sendJSON(self, address, data):
        log.debug(f"Sending a request to {c.path(address)}")
    
        try:
            prepared = requests.Request(
                'POST',
                address,
                json        = data,
                auth        = (self.config.user.name, self.config.user.password),
            ).prepare()

            printRequest(prepared)

            with requests.Session() as session:
                response = session.send(prepared, timeout = self.config.server.timeout)
                log.debug(f"Response received: code {c.ok(response.status_code)}, text {c.param(response.text)}")

        except ConnectionError:
            log.error("Connection refused")
        except ConnectTimeout:
            log.error("Connection timed out")


    def getArgs(self):
        parser = argparse.ArgumentParser(
            description = "AMOS station manager client",
        )
        parser.add_argument('config', type = argparse.FileType('r'))
        parser.add_argument('-i', '--interval', type = int)
        parser.add_argument('-d', '--debug', action = 'store_true')
        return parser.parse_args()

    def overrideConfig(self):
        if self.args.debug:
            log.warning(f"Debug output is {c.over('active')}")
            log.setLevel(logging.DEBUG)

        if self.args.interval is not None:
            log.warning(f"Overriding {c.over('interval')}")

def printRequest(req):
    log.debug("HTTP/1.1 {method} {url}\n{headers}\n{body}".format(
        method = req.method,
        url = req.url,
        headers = '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        body = req.body,
    ))

def main():
    monitor = Monitor()

main()
