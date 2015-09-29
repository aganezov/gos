# -*- coding: utf-8 -*-
import unittest
from gos.tasks import BaseTask

__author__ = "Sergey Aganezov"


class BaseTaskTestCase(unittest.TestCase):
    def test_execute_method_existence(self):
        self.assertTrue(hasattr(BaseTask(), 'execute'))
        self.assertTrue(callable(BaseTask().execute))
        self.assertTrue(hasattr(BaseTask(), 'sub_tasks'))
        self.assertIsInstance(BaseTask().sub_tasks, list)

if __name__ == '__main__':
    unittest.main()
