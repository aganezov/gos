# -*- coding: utf-8 -*-

import unittest

from gos.tasks import BaseTask


class BaseTaskTestCase(unittest.TestCase):
    def setUp(self):
        self.task_class = BaseTask

    def test_name_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "name"))

    def test_self_loop_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "self_loop"))

    def test_do_self_loop_property(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "do_self_loop"))

    def test_run_method_existence(self):
        task = self.task_class()
        self.assertTrue(hasattr(task, "run"))
        self.assertTrue(callable(getattr(task, "run")))


if __name__ == '__main__':
    unittest.main()
