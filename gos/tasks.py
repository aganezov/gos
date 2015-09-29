# -*- coding: utf-8 -*-
import abc
from abc import ABCMeta

__author__ = "Sergey Aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "develop"


class BaseTask(object):

    def __init__(self):
        self.sub_tasks = []

    def execute(self):
        for sub_task in self.sub_tasks:
            sub_task.execute()
