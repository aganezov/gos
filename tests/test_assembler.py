import logging
import os
import unittest
import shutil
from gos.assembler import AssemblyManager
from gos.configuration import Configuration
from tests.test_logging import MockingLoggingHandler

__author__ = 'aganezov'

LOGGING_INFO = 'INFO'
LOGGING_DEBUG = 'DEBUG'
LOGGING_ERROR = 'ERROR'
LOGGING_CRITICAL = 'CRITICAL'


class AssemblerManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.output_dir_name = self.config[Configuration.OUTPUT][Configuration.OUTPUT_DIRECTORY]
        if not os.path.exists(self.output_dir_name):
            os.mkdir(self.output_dir_name)

        self.logger = logging.getLogger(self.config[Configuration.LOGGING][Configuration.LOGGER_NAME])
        self.mocking_handler = MockingLoggingHandler(level=self.config[Configuration.LOGGING][Configuration.LOGGING_LEVEL])
        self.mocking_handler.setFormatter(logging.Formatter(self.config[Configuration.LOGGING][Configuration.LOGGING_FORMAT]))
        self.mocking_handler.reset()
        self.logger.addHandler(self.mocking_handler)
        self.assembler_manager = AssemblyManager(logger=self.logger, apply_configuration_to_logger=False)

    def tearDown(self):
        if os.path.exists(self.output_dir_name):
            shutil.rmtree(self.output_dir_name)
        self.mocking_handler.reset()

    def test_fields_on_initialization(self):
        manager = AssemblyManager()
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager.logger)
        self.assertIsNone(manager.breakpoint_graph)
        self.assertIsNone(manager.phylogenetic_tree)
        self.assertIsNone(manager.target_organisms)

    def test_logging_on_initialization(self):
        self.assertEqual(len(self.mocking_handler.messages[LOGGING_INFO]), 1)

    def test_default_logger_name(self):
        self.assertEqual(self.assembler_manager.logger.name,
                         self.assembler_manager.config[Configuration.LOGGING][Configuration.LOGGER_NAME])

    def test_logger_format(self):
        self.assertEqual(self.assembler_manager.logger.level,
                         self.assembler_manager.config[Configuration.LOGGING][Configuration.LOGGING_LEVEL])


if __name__ == '__main__':
    unittest.main()
