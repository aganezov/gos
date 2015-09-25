# -*- coding: utf-8 -*-
__author__ = "aganezov"
__email__ = "aganezov(at)gwu.edu"
__status__ = "development"


class AssemblyManager(object):
    def __init__(self, config=None, logger=None):
        self.config = config
        self.logger = logger
