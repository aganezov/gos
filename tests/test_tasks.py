# -*- coding: utf-8 -*-
import importlib
import sys

import time

import os
import tempfile
import unittest

from gos.exceptions import GOSTaskException
from gos.tasks import BaseTask, TaskLoader


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


class TaskLoaderTestCase(unittest.TestCase):
    def test_load_from_file_file_does_not_exists(self):
        file_path = "non_existing_file_pass"
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_file(file_path)

    def test_load_from_file_dir_supplied(self):
        dir_path = os.path.dirname(__file__)
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_file(dir_path)

    def test_load_from_file_no_name_attribute_on_loaded_class(self):
        bad_class_code = """class MyTaskOne(BaseTask):\n\tdef run(self, assembler_manager):\n\t\tpass\n"""
        source_file = self.create_tmp_py_file()
        source_file.write(self.get_base_task_import_code_string())
        source_file.write(bad_class_code)
        source_file.flush()
        importlib.invalidate_caches()           # importlib invalidate_caches call is required due to this python issue: http://bugs.python.org/issue23412
        source_file_name = source_file.name
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_file(source_file_name)
        source_file.close()

    def test_load_from_file_non_python_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")
        importlib.invalidate_caches()
        with self.assertRaises(GOSTaskException):
            TaskLoader().load_tasks_from_file(tmp_file.name)

    def get_base_task_import_code_string(self):
        return "from gos.tasks import BaseTask\n"

    def get_custom_task_files_values(self):
        return [
            """class MyTaskOne(BaseTask):\n\tname = "my_task_one"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskTwo(BaseTask):\n\tname = "my_task_two"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
            """class MyTaskThree(BaseTask):\n\tname = "my_task_three"\n\tdef run(self, assembler_manager):\n\t\tpass\n"""
        ]

    def get_custom_non_task_classes_code_strings(self):
        return [
            """class MyNoneTaskClass(object):\n\tname = "my_none_base_task"\n\tdef run(self, assembler_manager):\n\t\tpass\n""",
        ]

    def test_load_from_file_single_custom_task_class(self):
        with tempfile.NamedTemporaryFile(mode="wt", suffix=".py") as source_file:
            custom_task_file_data = self.get_custom_task_files_values()[0]
            source_file.write(self.get_base_task_import_code_string())
            source_file.write(custom_task_file_data)
            source_file.flush()
            importlib.invalidate_caches()
            source_file_name = source_file.name
            result = TaskLoader().load_tasks_from_file(source_file_name)
            self.assertIn("my_task_one", result)
            self.assertTrue(issubclass(result["my_task_one"], BaseTask))

    def create_tmp_py_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        return tmp_file

    def test_load_from_file_multiple_custom_tasks_classes(self):
        source_file = self.create_tmp_py_file()
        source_file.write(self.get_base_task_import_code_string())
        for custom_task_code_string in self.get_custom_task_files_values():
            source_file.write(custom_task_code_string)
        source_file.write(self.get_custom_non_task_classes_code_strings()[0])
        source_file.flush()
        importlib.invalidate_caches()
        source_file_name = source_file.name
        result = TaskLoader().load_tasks_from_file(source_file_name)
        for task_name in ["my_task_one", "my_task_two", "my_task_three"]:
            self.assertIn(task_name, result)
            self.assertTrue(issubclass(result[task_name], BaseTask))
        self.assertNotIn("my_non_base_task", result)
        source_file.close()


if __name__ == '__main__':
    unittest.main()
