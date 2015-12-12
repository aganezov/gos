# -*- coding: utf-8 -*-

import os
from gos.exceptions import GOSExecutableContainerException
from gos.utils.load import Loader

DEFAULT_SELF_LOOP = False


class ExecutableContainer(object):
    name = "executable_container"
    type_name = "executable_container"

    def __init__(self, name=None, self_loop=DEFAULT_SELF_LOOP, do_self_loop=False, entries_names=None, entries=None,
                 entries_type_names=None, logger=None):
        self.name = self.__class__.name if name is None else name
        self.group_reference_name = self.group_reference_name if \
            hasattr(self, "group_reference_name") and self.group_reference_name is not None else \
            self._get_default_group_reference_name()

        if entries_names is None:
            entries_names = self.entries_names if hasattr(self, "entries_names") else []
        self.entries_names = entries_names
        if entries_type_names is None:
            entries_type_names = self.entries_type_names if hasattr(self, "entries_type_names") else []
        self.entries_type_names = entries_type_names
        self.entries = [] if entries is None else entries

        self.self_loop = self_loop
        self.do_self_loop = do_self_loop
        self.logger = logger

    def _get_default_group_reference_name(self):
        return self.name + "s"

    def run(self, manager):
        pass

    @staticmethod
    def setup_from_config(config, entries_names_list_reference="entries"):
        result = ExecutableContainer()
        try:
            result.name = config["name"]
        except KeyError:
            raise GOSExecutableContainerException()
        result.self_loop = config.get("self_loop", DEFAULT_SELF_LOOP)
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
