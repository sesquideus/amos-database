import argparse
import dotmap
import logging
import yaml

from . import colour as c
from . import exceptions
from . import logger


log = logging.getLogger('root')

"""
    Simple Console Application with Logging, Yaml Configuration and Argparse
"""
class Scalyca():
    def __init__(self, app_name, *, description):
        self.app_name           = app_name
        self.description        = description
        
        self.create_argparser()
        self.args = self.argparser.parse_args()

        try:
            self.hello()
            self.load_configuration()
            self.override_configuration()

            self.config = dotmap.DotMap(self.raw_config, _dynamic=False)
        except exceptions.ConfigurationError():
            pass            

    def __del__(self):
        log.info(f"{c.script(self.app_name)} finished")
        
    def create_argparser(self):
        self.argparser = argparse.ArgumentParser(description=self.description)
        self.argparser.add_argument('config',            type=argparse.FileType('r'),        help="Main configuration file")
        self.argparser.add_argument('-d', '--debug',     action='store_true',                help="Turn on verbose logging")

    def hello(self):
        log.info(f"Starting {c.script(self.app_name)}")

    def load_configuration(self):
        self.raw_config = dotmap.DotMap(yaml.safe_load(self.args.config), _dynamic=True)

    def override_configuration(self):
        log.setLevel(logging.DEBUG if self.args.debug else logging.INFO)

        if self.args.debug:
            log.warning(f"Debug output is {c.over('active')}")

    def configure(self):
        pass

    def override_warning(self, parameter, old, new):
        log.warning(f"Overriding {c.param(parameter)} ({c.over(old)} -> {c.over(new)})")

