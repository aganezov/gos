# -*- coding: utf-8 -*-
from gos.configuration import Configuration
from gos.exceptions import GOSTaskException, GOSCriticalException
from gos.tasks import TaskLoader


class Manager(object):
    def __init__(self, config):
        self.configuration = config
        self.tasks_classes = {}
        self.tasks_instances = {}

    def initiate_tasks(self):
        """ Loads all tasks using `TaskLoader` from respective configuration option """
        self.tasks_classes = TaskLoader().load_tasks(
            paths=self.configuration[Configuration.ALGORITHM][Configuration.TASKS][Configuration.PATHS])

    def instantiate_tasks(self):
        """ All loaded tasks are initialized. Depending on configuration fails in such instantiations may be silent """
        self.tasks_instances = {}
        for task_name, task_class in self.tasks_classes.items():
            try:
                self.tasks_instances[task_name] = task_class()
            except Exception as ex:
                if not self.configuration[Configuration.ALGORITHM][Configuration.IOSF]:
                    raise GOSTaskException("An exception happened during the task instantiation."
                                           "{exception}".format(exception=ex))

    def get_task_instance(self, task_name):
        try:
            return self.tasks_instances[task_name]
        except KeyError:
            raise GOSCriticalException("Attempted to retrieve a task by name={task_name} which instance was not created"
                                       "".format(task_name=task_name))
