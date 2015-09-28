# -*- coding: utf-8 -*-
import logging
import os
from gos.configuration import Configuration

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class AssemblyManager(object):

    def __init__(self, configuration=None, logger=None, apply_configuration_to_logger=True):
        self.config = configuration if configuration is not None else Configuration()
        logging_file_path = os.path.join(
            self.config[Configuration.OUTPUT][Configuration.OUTPUT_DIRECTORY],
            self.config[Configuration.LOGGING][Configuration.IO_DESTINATION]
        )
        self.logger = logger if logger is not None else logging.getLogger(self.config[Configuration.LOGGING][Configuration.LOGGER_NAME])
        if apply_configuration_to_logger:
            handler = logging.FileHandler(logging_file_path)
            handler.setFormatter(logging.Formatter(self.config[Configuration.LOGGING][Configuration.LOGGING_FORMAT]))
            self.logger.setLevel(self.config[Configuration.LOGGING][Configuration.LOGGING_LEVEL])
            self.logger.addHandler(handler)

        self.breakpoint_graph = None
        self.phylogenetic_tree = None
        self.target_organisms = None
        self.fragments_data = None

        self.logger.info('Assembly manager Initialization')
