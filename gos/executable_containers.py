# -*- coding: utf-8 -*-
import importlib
import sys

import os
from gos.exceptions import GOSExecutableContainerException


class ExecutableContainer(object):
    name = "executable_container"

    DEFAULT_SELF_LOOP = False

    def __init__(self, name=None, self_loop=DEFAULT_SELF_LOOP, do_self_loop=False, entries_names=None, entries=None,
                 logger=None):
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
    def setup_from_file(file_path):
        if not os.path.exists(file_path):
            raise GOSExecutableContainerException()
        if os.path.isdir(file_path):
            raise GOSExecutableContainerException()
        module_path, file_name = os.path.split(file_path)
        if not file_name.endswith((".py", ".pyc")):
            raise GOSExecutableContainerException()
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        module = importlib.import_module(module_name)
        objects = [getattr(module, attr_name) for attr_name in dir(module)]
        result = {}
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
                    result[entry.name] = entry
            except TypeError:
                continue
        return result