# -*- coding: utf-8 -*-
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
