# -*- coding: utf-8 -*-


class BaseTask(object):
    name = "BaseTask"
    self_loop = False
    do_self_loop = False

    def run(self, assembler_manager):
        pass