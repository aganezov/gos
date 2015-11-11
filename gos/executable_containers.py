# -*- coding: utf-8 -*-


class ExecutableContainer(object):
    name = "executable_container"

    def __init__(self, name=None, self_loop=False, do_self_loop=False, entries_info=None, entries=None):
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

    def run(self, assembler_manager):
        pass
