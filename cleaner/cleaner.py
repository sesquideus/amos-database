#!/usr/bin/env python

import argparse
import os
import datetime
import shutil
import distutils
import yaml
import dotmap
import logging

from scalyca import Scalyca, logger
from scalyca import colour as c

log = logger.setupLog('root')


class Cleaner(Scalyca):
    def __init__(self):
        super().__init__(
            app_name            = "AMOS cleaner",
            description         = "AMOS directory cleaner",
        )

    def create_argparser(self):
        super().create_argparser()

        self.argparser.add_argument('-D', '--dry-run', action='store_true', help="Dry run, do not actually delete anything")

    def override_configuration(self):
        super().override_configuration()

        self.raw_config.dry_run = False
        if self.args.dry_run:
            self.override_warning("dry run", self.raw_config.dry_run, self.args.dry_run)
            self.raw_config.dry_run = True

    def list_files(self):
        count = 0
        for root, folder, files in os.walk(self.config.source):
            for filename in files:
                self.process_file(root, filename)
                count += 1
        log.info(f"{c.num(count)} files listed")
                
    def process_file(self, directory, filename):
        path = os.path.join(directory, filename)
        log.debug(f"Processing {c.path(path)}")

        modified = datetime.datetime.fromtimestamp(os.path.getmtime(path))
        age = (datetime.datetime.now() - modified) / datetime.timedelta(days=1)

        if filename in self.config.exclude:
            log.info(f"Skipping {c.path(path)} (excluded)")
            return
        if age < self.config.days:
            log.info(f"Skipping {c.path(path)} (too new)")
            return

    def remove_file(self, path):
        if self.config.dry_run:
            log.info(f"Would remove {c.path(path)}")
        else:
            log.info(f"Removing {c.path(path)}")
            os.remove(path)

if __name__ == "__main__":
    cleaner = Cleaner()
    cleaner.list_files()

