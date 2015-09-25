import unittest
from gos.assembler import AssemblyManager

__author__ = 'aganezov'


class AssemblerTestCase(unittest.TestCase):
    def test_empty_initialization(self):
        manager = AssemblyManager()
        self.assertIsNone(manager.config)
        self.assertIsNone(manager.logger)

if __name__ == '__main__':
    unittest.main()
