# -*- coding: utf-8 -*-
from gos.exceptions import GOSExecutableContainerException


class ExecutableContainer(object):
    name = "executable_container"

    def __init__(self, name=None, self_loop=False, do_self_loop=False, entries_info=None, entries=None,
                 logger=None):
        if name is None:
            name = self.__class__.name
        self.name = name
        self.self_loop = self_loop
        self.do_self_loop = do_self_loop
        if entries_info is None:
            entries_info = {}
        self.entries_info = entries_info
        if entries is None:
            entries = []
        self.entries = entries
        self.logger = logger

    def run(self, assembler_manager):
        pass

    @staticmethod
    def setup_from_config(config):
        result = ExecutableContainer()
        try:
            result.name = config["name"]
        except KeyError:
            raise GOSExecutableContainerException()
