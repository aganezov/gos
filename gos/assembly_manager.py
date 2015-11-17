# -*- coding: utf-8 -*-
from gos.configuration import Configuration
from gos.tasks import TaskLoader


class AssemblyManager(object):
    def __init__(self, config):
        self.configuration = config
        self.tasks = {}

    def initiate_tasks(self):
        self.tasks = TaskLoader().load_tasks(paths=self.configuration[Configuration.ALGORITHM][Configuration.TASKS][Configuration.PATHS])

