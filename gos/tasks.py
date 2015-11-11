# -*- coding: utf-8 -*-
import sys

import importlib

import os
from gos.exceptions import GOSTaskException


class BaseTask(object):
    name = "BaseTask"
    self_loop = False
    do_self_loop = False

    def run(self, assembler_manager):
        raise NotImplemented("run method shall be implemented for all the subclasses of BaseTask")


class TaskLoader(object):

    def load_tasks_from_file(self, file_path):
        if not os.path.exists(file_path):
            raise GOSTaskException()
        if os.path.isdir(file_path):
            raise GOSTaskException()
        module_path, name = os.path.split(file_path)
        if not name.endswith((".py", ".pyc")):
            raise GOSTaskException()
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = name[:name.rfind(".")]
        module = importlib.import_module(module_name)
        objects = [getattr(module, attr_name) for attr_name in dir(module)]
        result = {}
        for entry in objects:
            try:
                if issubclass(entry, BaseTask):
                    if entry.__name__ != BaseTask.__name__ and entry.name == BaseTask.name:
                        raise GOSTaskException()
                    result[entry.name] = entry
            except TypeError:
                continue
        return result

    def load_tasks_from_dir(self, dir_path):
        if not os.path.exists(dir_path):
            raise GOSTaskException()
        if os.path.isfile(dir_path):
            raise GOSTaskException()
