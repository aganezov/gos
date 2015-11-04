# -*- coding: utf-8 -*-
import logging

__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class Configuration(dict):

    ############################################################################################################
    #
    # {
    #   'INPUT': {
    #              'GENOMES': {
    #                           'SOURCE_FILES': ['file_1_path', 'file_2_path', ...],
    #                           'IO_SILENT_FAIL': True | False,
    #                           'MERGE_EDGES': True | False | [file_1_bool, file_2_bool, ...]
    #                         },
    #              'TREE': {
    #                           'SOURCE_FILES': ['file_1_path', 'file_2_path', ...],
    #                           'IO_SILENT_FAIL': True | False,
    #                      }
    #            },
    #   'LOGGING': {
    #               'IO_SILENT_FAIL': True | False,
    #               'IO_DESTINATION': 'file_path',
    #               'ENABLE_IO_LOGGING': True,
    #               'BREAKPOINT_GRAPH_CONSTRUCTION': 'file_path',           % defaults to IO_DESTINATION
    #               'ENABLE_BG_CONSTRUCTION_LOGGING': True | False,         % defaults to ENABLE_IO_LOGGING
    #               'TREE_PROCESSING': 'file_path',                         % defaults to IO_DESTINATION
    #               'ENABLE_TREE_PROCESSING_LOGGING': True | False,         % defaults to ENABLE_IO_LOGGING
    #               'ASSEMBLY_POINTS_IDENTIFICATION': 'file_path',          % defaults to IO_DESTINATION
    #               'ENABLE_POINTS_IDENTIFICATION_LOGGING': True | False,   % defaults to ENABLE_IO_LOGGING
    #               'ASSEMBLY_POINTS_GLUING': 'file_path',                  % defaults to IO_DESTINATION
    #               'ENABLE_POINTS_GLUING_LOGGING': True | False            % defaults to ENABLE_IO_LOGGING
    #              },
    #   'PROCESSING': {
    #                   'ASSEMBLY_TARGET_GENOMES': [],
    #                   'STRATEGIES': {
    #                                   'EXECUTE_SIMPLE_CC_strategy': True | False | [genome_1_bool, genome_2_bool, ...],
    #                                   'EXECUTE_PHYL_TREE_strategy': True | False | [genome_1_bool, genome_2_bool, ...]
    #                                   'PHYL_TREE_ASSEMBLY_SCORE_THRESHOLD': 2
    #                                 },
    #                 },
    #   'OUTPUT': {
    #               'OUTPUT_DIRECTORY': 'output'
    #               'OUTPUT_ASSEMBLIES': True | False | [genome_1_bool, genome_2_bool, ...],
    #               'OUTPUT_ASSEMBLIES_AS_CHAINS': True | False | [genome_1_bool, genome_2_bool, ...],
    #               'OUTPUT_ASSEMBLIES_DESTINATION_FILES': file_path | ['genome_1_file', 'genome_2_path', ...]
    #             }
    # }
    ############################################################################################################

    # top level keys
    LOGGER_NAME = 'LOGGER_NAME'
    LOGGING_FORMAT = 'LOGGING_FORMAT'
    LOGGING_LEVEL = 'LOGGING_LEVEL'
    INPUT = 'INPUT'
    LOGGING = 'LOGGING'
    PROCESSING = 'PROCESSING'
    OUTPUT = 'OUTPUT'

    # supplementary keys
    IO_SILENT_FAIL = 'IO_SILENT_FAIL'

    # input keys
    GENOMES = 'GENOMES'
    TREE = 'TREE'
    SOURCE_FILES = 'SOURCE_FILES'
    MERGE_EDGES = 'MERGE_FILES'

    # logging keys
    OUTPUT_DIRECTORY = 'OUTPUT_DIRECTORY'
    IO_DESTINATION = 'IO_DESTINATION'
    ENABLE_IO_LOGGING = 'ENABLE_IO_LOGGING'
    BREAKPOINT_GRAPH_CONSTRUCTION = 'BREAKPOINT_GRAPH_CONSTRUCTION'
    ENABLE_BG_CONSTRUCTION_LOGGING = 'ENABLE_BG_CONSTRUCTION_LOGGING'
    TREE_PROCESSING = 'TREE_PROCESSING'
    ENABLE_TREE_PROCESSING_LOGGING = 'ENABLE_TREE_PROCESSING_LOGGING'
    ASSEMBLY_POINTS_IDENTIFICATION = 'ASSEMBLY_POINTS_IDENTIFICATION'
    ENABLE_POINTS_IDENTIFICATION_LOGGING = 'ENABLE_POINTS_IDENTIFICATION_LOGGING'
    ASSEMBLY_POINTS_GLUING = 'ASSEMBLY_POINTS_GLUING'
    ENABLE_POINTS_GLUING_LOGGING = 'ENABLE_POINTS_GLUING_LOGGING'

    # processing keys
    STRATEGIES = 'STRATEGIES'
    ASSEMBLY_TARGET_GENOMES = 'ASSEMBLY_TARGET_GENOMES'
    EXECUTE_SIMPLE_CC_strategy = 'EXECUTE_SIMPLE_CC_strategy'
    EXECUTE_PHYL_TREE_strategy = 'EXECUTE_PHYL_TREE_strategy'
    PHYL_TREE_ASSEMBLY_SCORE_THRESHOLD = 'PHYL_TREE_ASSEMBLY_SCORE_THRESHOLD'

    # output keys
    OUTPUT_ASSEMBLIES = 'OUTPUT_ASSEMBLIES'
    OUTPUT_ASSEMBLIES_AS_CHAINS = 'OUTPUT_ASSEMBLIES_AS_CHAINS'
    OUTPUT_ASSEMBLIES_DESTINATION_FILES = 'OUTPUT_ASSEMBLIES_DESTINATION_FILES'

    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        if self.INPUT not in self:
            self[self.INPUT] = {
                self.GENOMES: {
                    self.SOURCE_FILES: [],
                    self.MERGE_EDGES: False,
                    self.IO_SILENT_FAIL: False
                },
                self.TREE: {
                    self.SOURCE_FILES: [],
                    self.IO_SILENT_FAIL: False
                }
            }
        if self.LOGGING not in self:
            self[self.LOGGING] = {
                self.LOGGING_LEVEL: logging.INFO,
                self.LOGGING_FORMAT: '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                self.IO_DESTINATION: 'log.txt',
                self.LOGGER_NAME: 'AssemblyManager',
                self.IO_SILENT_FAIL: True,
                self.ENABLE_IO_LOGGING: True,
                self.BREAKPOINT_GRAPH_CONSTRUCTION: '',
                self.ENABLE_BG_CONSTRUCTION_LOGGING: None,
                self.TREE_PROCESSING: '',
                self.ENABLE_TREE_PROCESSING_LOGGING: None,
                self.ASSEMBLY_POINTS_IDENTIFICATION: '',
                self.ENABLE_POINTS_IDENTIFICATION_LOGGING: None,
                self.ASSEMBLY_POINTS_GLUING: '',
                self.ENABLE_POINTS_GLUING_LOGGING: None
            }

        if self.PROCESSING not in self:
            self[self.PROCESSING] = {
                self.ASSEMBLY_TARGET_GENOMES: [],
                self.STRATEGIES: {
                    self.EXECUTE_SIMPLE_CC_strategy: True,
                    self.EXECUTE_PHYL_TREE_strategy: True,
                    self.PHYL_TREE_ASSEMBLY_SCORE_THRESHOLD: 2
                }
            }
        if self.OUTPUT not in self:
            self[self.OUTPUT] = {
                self.OUTPUT_DIRECTORY: 'output',
                self.OUTPUT_ASSEMBLIES: True,
                self.OUTPUT_ASSEMBLIES_AS_CHAINS: True,
                self.OUTPUT_ASSEMBLIES_DESTINATION_FILES: 'assemblies.txt'
            }
