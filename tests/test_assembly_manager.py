# -*- coding: utf-8 -*-
import importlib

import tempfile
import unittest

from gos.assembly_manager import AssemblyManager
from gos.configuration import Configuration
from gos.tasks import BaseTask, TaskLoader
from tests.test_tasks import TaskLoaderTestCase


class AssemblyManagerTestCase(unittest.TestCase):
    def setUp(self):
        self.am = AssemblyManager(config=Configuration())

    def test_manager_init(self):
        config = Configuration()
        am = AssemblyManager(config=config)
        self.assertDictEqual(config, am.configuration)

    def create_correct_temporary_tasks_files(self):
        result = []
        tltc = TaskLoaderTestCase()
        for task_string_data in tltc.get_custom_task_files_values():
            tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
            tmp_file.write(tltc.get_base_task_import_code_string())
            tmp_file.write(task_string_data)
            tmp_file.flush()
            result.append(tmp_file)
        return result

    def test_manager_initiate_tasks(self):
        tmp_files = self.create_correct_temporary_tasks_files()  # have to keep reference to tmp_file objects,
                                                                 # otherwise object are deleted by garbage collector and
                                                                 # corresponding files are deleted
        self.am.configuration[Configuration.ALGORITHM][Configuration.TASKS] = {
            Configuration.PATHS: [f.name for f in tmp_files]
        }
        importlib.invalidate_caches()
        self.am.initiate_tasks()
        self.assertTrue(hasattr(self.am, "tasks_classes"))
        self.assertTrue(isinstance(self.am.tasks_classes, dict))
        for task_name in TaskLoaderTestCase.get_tasks_names():
            self.assertIn(task_name, self.am.tasks_classes)
            self.assertTrue(issubclass(self.am.tasks_classes[task_name], BaseTask))

    def test_manager_instantiate_tasks(self):
        self.am.tasks_classes = self.get_tasks_classes()
        self.am.instantiate_tasks()
        for task_name in self.am.tasks_classes:
            self.assertIn(task_name, self.am.tasks_instances)
            self.assertIsInstance(self.am.tasks_instances[task_name], BaseTask)
            self.assertIsInstance(self.am.tasks_instances[task_name], self.am.tasks_classes[task_name])

    def get_tasks_classes(self):
        tmp_files = self.create_correct_temporary_tasks_files()
        paths = [f.name for f in tmp_files]
        importlib.invalidate_caches()
        return TaskLoader().load_tasks(paths=paths)

if __name__ == '__main__':
    unittest.main()
