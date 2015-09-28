# -*- coding: utf-8 -*-
import logging
from bg import BreakpointGraph
from bg.bg_io import GRIMMReader
from gos.exceptions import GOSIOError
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

    def read_gene_order_data(self):
        self.logger.debug("Creating breakpoint graph to incorporate gene orders")
        self.breakpoint_graph = BreakpointGraph()
        silent_io_fail = self.config[Configuration.INPUT][Configuration.GENOMES][Configuration.IO_SILENT_FAIL]
        merge_edges = self.config[Configuration.INPUT][Configuration.GENOMES][Configuration.MERGE_EDGES]

        self.logger.debug('"merge edges" flag is set to {merge_edges}'.format(merge_edges=merge_edges))
        self.logger.debug('"silent io fail" flag is set to {silent_io_fail}'.format(silent_io_fail=silent_io_fail))
        for file_name in self.config[Configuration.INPUT][Configuration.GENOMES][Configuration.SOURCE_FILES]:
            self.logger.info('Processing gene order file {file_name}'.format(file_name=file_name))
            try:
                with open(file_name, mode="rt") as source:
                    self.breakpoint_graph.update(GRIMMReader.get_breakpoint_graph(source), merge_edges=merge_edges)
            except ValueError as err:
                self.logger.error("Error during processing of {file_name}: (error_message)".format(file_name=file_name,
                                                                                                   error_message=err))
                self.logger.debug("Silent io fail is set {silent_fail}".format(silent_fail=silent_io_fail))
                if silent_io_fail:
                    continue
                else:
                    self.logger.critical("Error during processing of gene order file {file_name}. "
                                         "Silent io fail flag is set to {silent_io_fail}, application can not continue"
                                         "".format(file_name=file_name, silent_io_fail=silent_io_fail))
                    raise GOSIOError("Error during processing {file_name} gene order file".format(file_name=file_name))
            except FileNotFoundError:
                self.logger.error("No gene order file {file_name} was found".format(file_name=file_name))
                self.logger.debug("Silent io fail is set {silent_fail}".format(silent_fail=silent_io_fail))
                if silent_io_fail:
                    continue
                else:
                    self.logger.critical("Error during search for gene order file {file_name}. "
                                         "Silent io fail flag is set to {silent_io_fail}, application can not continue"
                                         "".format(file_name=file_name, silent_io_fail=silent_io_fail))
                    raise GOSIOError("No gene order file {file_name} was found".format(file_name=file_name))
