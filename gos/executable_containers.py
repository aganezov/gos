# -*- coding: utf-8 -*-
import importlib
import sys

import os
from gos.exceptions import GOSExecutableContainerException
from gos.utils.load import Loader


class ExecutableContainer(object):
    name = "executable_container"
    type_name = "executable_container"

    DEFAULT_SELF_LOOP = False
    DEFAULT_ENTRIES_TYPE_NAME = None

    def __init__(self, name=None, self_loop=DEFAULT_SELF_LOOP, do_self_loop=False, entries_names=None, entries=None,
                 entries_type_name=DEFAULT_ENTRIES_TYPE_NAME, logger=None):
        if name is None:
            name = self.__class__.name
        self.name = name
        self.self_loop = self_loop
        self.do_self_loop = do_self_loop
        if entries_names is None:
            entries_names = []
        self.entries_names = entries_names
        if entries is None:
            entries = []
        self.entries = entries
        self.entries_type_name = entries_type_name
        self.logger = logger

    def run(self, assembler_manager):
        pass

    @staticmethod
    def setup_from_config(config, entries_names_list_reference="entries"):
        result = ExecutableContainer()
        try:
            result.name = config["name"]
        except KeyError:
            raise GOSExecutableContainerException()
        result.self_loop = config.get("self_loop", ExecutableContainer.DEFAULT_SELF_LOOP)
        result.entries_names = config.get(entries_names_list_reference, [])
        return result

    @staticmethod
    def setup_from_file(file_path, container_name):
        file_name, module_path, objects = Loader.import_custom_python_file(file_path)
        for entry in objects:
            try:
                if issubclass(entry, ExecutableContainer) and entry.__name__ != ExecutableContainer.__name__:
                    if entry.name == ExecutableContainer.name:
                        raise GOSExecutableContainerException(
                            "Class {class_name} form file {file_name} does not have a unique `name` class field. "
                            "All custom tasks must have a unique `name` class field for them, tat is used for future reference"
                            "".format(class_name=entry.name, file_name=os.path.join(module_path, file_name)))
                    elif not hasattr(entry, "setup"):
                        raise GOSExecutableContainerException()
                    if entry.name == container_name:
                        result = entry()
                        result.setup()
                        return result
            except TypeError:
                continue
        raise GOSExecutableContainerException()
