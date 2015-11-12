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
        """ Imports specified python module and returns subclasses of BaseTask from it

        :param file_path: a fully qualified file path for a python module to import CustomTasks from
        :type file_path: `str`
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        if not os.path.exists(file_path):
            raise GOSTaskException("Specified file to load custom tasks from does not exists")
        if os.path.isdir(file_path):
            raise GOSTaskException("Specified path for file to load custom tasks from corresponds to a directory, not a file")
        module_path, file_name = os.path.split(file_path)
        if not file_name.endswith((".py", ".pyc")):
            raise GOSTaskException("Specified path for file to load custom tasks from does not correspond to python file ")
        if module_path not in sys.path:
            sys.path.insert(0, module_path)
        module_name = file_name[:file_name.rfind(".")]
        module = importlib.import_module(module_name)
        objects = [getattr(module, attr_name) for attr_name in dir(module)]
        result = {}
        for entry in objects:
            try:
                if issubclass(entry, BaseTask):
                    if entry.__name__ != BaseTask.__name__ and entry.name == BaseTask.name:
                        raise GOSTaskException("Class {class_name} form file {file_name} does not have a unique `name` class field. "
                                               "All custom tasks must have a unique `name` class field for them, tat is used for future reference"
                                               "".format(class_name=entry.name, file_name=os.path.join(module_path, file_name)))
                    result[entry.name] = entry
            except TypeError:
                continue
        return result

    def load_tasks_from_dir(self, dir_path):
        """ Imports all python modules in specified directories and returns subclasses of BaseTask from them

        :param dir_path: fully qualified directory path, where all python modules will be search for subclasses of BaseTask
        :type dir_path: `str`
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        if not os.path.exists(dir_path):
            raise GOSTaskException()
        if os.path.isfile(dir_path):
            raise GOSTaskException()
        result = {}
        for file_basename in os.listdir(path=dir_path):
            full_file_path = os.path.join(dir_path, file_basename)
            try:
                result.update(self.load_tasks_from_file(full_file_path))
            except GOSTaskException:
                continue
        return result

    def load_tasks(self, paths):
        """ Loads all subclasses of BaseTask from modules that are contained in supplied directory paths or direct module paths

        :param paths: an iterable of fully qualified paths to python modules / directories, from where we import subclasses of BaseClass
        :type paths: `iterable`(`str`)
        :return: a dict of CustomTasks, where key is CustomTask.name, and value is a CustomClass task itself
        :rtype: `dict`
        """
        try:
            result = {}
            for path in paths:
                try:
                    if os.path.isdir(path):
                        result.update(self.load_tasks_from_dir(path))
                    elif os.path.isfile(path):
                        result.update(self.load_tasks_from_file(path))
                except GOSTaskException:
                    continue
            return result
        except TypeError:
            raise GOSTaskException("Argument for `load_tasks` method must be iterable")


