import os
import unittest
from gos.assembler import AssemblyManager
from gos.configuration import Configuration

__author__ = 'aganezov'


class AssemblerManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.output_dir_name = self.config[Configuration.OUTPUT][Configuration.OUTPUT_DIRECTORY]
        try:
            os.stat(self.output_dir_name)
        except IOError:
            os.mkdir(self.output_dir_name)
        self.assembler_manager = AssemblyManager()

    def tearDown(self):
        try:
            os.stat(self.output_dir_name)
            os.rmdir(self.output_dir_name)
        except IOError:
            pass

    def test_empty_initialization(self):
        manager = AssemblyManager()
        self.assertIsNotNone(manager.config)
        self.assertIsNotNone(manager.logger)

    def test_default_logger_name(self):
        self.assertEqual(self.assembler_manager.logger.name,
                         self.assembler_manager.config[Configuration.LOGGING][Configuration.LOGGER_NAME])

    def test_logger_format(self):
        self.assertEqual(self.assembler_manager.logger.level,
                         self.assembler_manager.config[Configuration.LOGGING][Configuration.LOGGING_LEVEL])


if __name__ == '__main__':
    unittest.main()
