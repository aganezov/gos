import unittest
from gos.assembler import AssemblyManager
from gos.configuration import Configuration

__author__ = 'aganezov'


class AssemblerManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.config = Configuration()
        self.assembler_manager = AssemblyManager()

    def test_empty_initialization(self):
        manager = AssemblyManager()
        self.assertIsNone(manager.config)
        self.assertIsNone(manager.logger)

if __name__ == '__main__':
    unittest.main()
