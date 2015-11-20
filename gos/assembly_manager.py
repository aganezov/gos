# -*- coding: utf-8 -*-
from gos.configuration import Configuration
from gos.tasks import TaskLoader


class AssemblyManager(object):
    def __init__(self, config):
        self.configuration = config
        self.tasks_classes = {}
        self.tasks_instances = {}

    def initiate_tasks(self):
        self.tasks_classes = TaskLoader().load_tasks(paths=self.configuration[Configuration.ALGORITHM][Configuration.TASKS][Configuration.PATHS])

    def instantiate_tasks(self):
        self.tasks_instances = {task_name: task_class() for task_name, task_class in self.tasks_classes.items()}

