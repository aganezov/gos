# -*- coding: utf-8 -*-
import unittest

from gos.executable_containers import ExecutableContainer


class ExecutableContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.executable_container = ExecutableContainer()
        self.ec = self.executable_container

    def test_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "name"))

    def test_entries_info_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries_info"))

    def test_entries_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries"))

    def test_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "self_loop"))

    def test_do_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "do_self_loop"))

    def test_run_method_existence(self):
        self.assertTrue(hasattr(self.ec, "run"))
        self.assertTrue(callable(getattr(self.ec, "run")))

if __name__ == '__main__':
    unittest.main()
