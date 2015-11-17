# -*- coding: utf-8 -*-
import unittest

from gos.assembly_manager import AssemblyManager
from gos.configuration import Configuration


class AssemblyManagerTestCase(unittest.TestCase):
    def test_manager_init(self):
        config = Configuration()
        am = AssemblyManager(config=config)
        self.assertDictEqual(config, am.configuration)


if __name__ == '__main__':
    unittest.main()
