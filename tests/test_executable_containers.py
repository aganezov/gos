# -*- coding: utf-8 -*-
import importlib
import tempfile
import unittest

from gos.exceptions import GOSExecutableContainerException, GOSIOException
from gos.executable_containers import ExecutableContainer


class ExecutableContainerTestCase(unittest.TestCase):
    def setUp(self):
        self.executable_container = ExecutableContainer()
        self.ec = self.executable_container

    def test_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "name"))

    def test_entries_type_name_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries_type_name"))

    def test_entries_info_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries_names"))

    def test_entries_attribute(self):
        self.assertTrue(hasattr(self.ec, "entries"))

    def test_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "self_loop"))

    def test_do_self_loop_attribute(self):
        self.assertTrue(hasattr(self.ec, "do_self_loop"))

    def test_run_method_existence(self):
        self.assertTrue(hasattr(self.ec, "run"))
        self.assertTrue(callable(getattr(self.ec, "run")))

    def test_logger_attribute(self):
        self.assertTrue(hasattr(self.ec, "logger"))

    def test_setup_from_config_no_name(self):
        with self.assertRaises(GOSExecutableContainerException):
            ExecutableContainer.setup_from_config(config={})

    def test_setup_from_config_self_loop_value(self):
        ec = ExecutableContainer.setup_from_config({"name": "my_name",
                                                    "self_loop": False})
        self.assertFalse(ec.self_loop)

    def test_setup_from_config_entries_names(self):
        stage_name_list = ["stage1", "stage2", "stage3"]
        ec = ExecutableContainer.setup_from_config({"name": "my_name",
                                                    "stages": stage_name_list},
                                                   entries_names_list_reference="stages")
        self.assertListEqual(ec.entries_names, stage_name_list)

    def test_setup_from_file_file_does_not_exists(self):
        non_existing_path = "non_existing_path.py"
        with self.assertRaises(GOSIOException):
            ExecutableContainer.setup_from_file(non_existing_path, "executable_container")

    def test_setup_from_file_non_python_file(self):
        non_py_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".non_py")
        with self.assertRaises(GOSIOException):
            ExecutableContainer.setup_from_file(non_py_file.name, "executable_container")

    def test_setup_from_file_no_unique_name(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write("""class MyContainer(ExecutableContainer):\n\tdef setup(self):\n\t\tpass""")
        tmp_file.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSExecutableContainerException):
            ExecutableContainer.setup_from_file(tmp_file.name, "executable_container")

    def get_executable_container_import_string(self):
        return """from gos.executable_containers import ExecutableContainer\n"""

    def test_setup_from_file_no_setup_method(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write("""class MyContainer(ExecutableContainer):\n\tname="new_executable_container_name" """)
        tmp_file.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSExecutableContainerException):
            ExecutableContainer.setup_from_file(tmp_file.name, "executable_container")

    def test_setup_from_file_no_match_by_name_attribute(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write("""class MyContainer(ExecutableContainer):\n\tname="new_ec_name"\n\tdef setup(self):\n\t\tpass""")
        tmp_file.flush()
        importlib.invalidate_caches()
        with self.assertRaises(GOSExecutableContainerException):
            ExecutableContainer.setup_from_file(tmp_file.name, container_name="not_new_ec_name")

    def test_setup_from_file(self):
        tmp_file = tempfile.NamedTemporaryFile(mode="wt", suffix=".py")
        tmp_file.write(self.get_executable_container_import_string())
        tmp_file.write(
            """class MyContainer(ExecutableContainer):\n\tname="my_ec"\n\tdef setup(self):\n\t\tself.entries_names = ["entry1"]\n\t\tself.entries_type_name="task" """)
        tmp_file.flush()
        importlib.invalidate_caches()
        result = ExecutableContainer.setup_from_file(tmp_file.name, container_name="my_ec")
        self.assertIsInstance(result, ExecutableContainer)
        self.assertListEqual(result.entries_names, ["entry1"])
        self.assertEqual(result.entries_type_name, "task")


if __name__ == '__main__':
    unittest.main()
