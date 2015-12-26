# -*- coding: utf-8 -*-
import logging

import os
from executable_containers import ExecutableContainer
from gos.configuration import Configuration
from gos.exceptions import GOSTaskException
from gos.tasks import TaskLoader

test_config = {
    "algorithm": {
        "tasks": {
            "paths": [os.path.dirname(__file__) + "/../draft/tasks.py"]
        },
        "executable_containers": [
            {
                "name": "stage",
                "reference": "stages"
            },
            {
                "name": "round",
                "reference": "rounds"
            }
        ],
        "stages": [
            {
                "name": "stage1",
                "entries_names": ["task1", "task2"]
            },
            {
                "name": "stage2",
                "entries_names": ["task3"]
            }
        ],

        "rounds": [
            {
                "name": "round1",
                "entries_names": ["stage1", "stage2"]
            },
            {
                "name": "round2",
                "entries_names": ["stage2"]
            }
        ],

        "pipeline": {
            "entries_names": ["round1", "round2"],
            "self_loop": True
        }
    }
}


class Manager(object):
    def __init__(self, config):
        self.configuration = config
        self.tasks_classes = {}
        self.tasks_instances = {}
        self.executable_containers_classes = {}
        self.executable_containers_instances = {}

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

    def initiate_executable_containers(self):
        for entry in self.configuration[Configuration.ALGORITHM]["executable_containers"]:
            reference = entry["reference"]
            for ec_config in self.configuration[Configuration.ALGORITHM][reference]:
                ec_config["group_reference_name"] = reference
                result = ExecutableContainer.setup_from_config(manager=self, config=ec_config)
                self.executable_containers_instances[result.name] = result
        if "pipeline" not in self.configuration[Configuration.ALGORITHM]["executable_containers"]:
            pipeline_config = self.configuration[Configuration.ALGORITHM]["pipeline"]
            if "name" not in pipeline_config:
                pipeline_config["name"] = "pipeline"
            self.executable_containers_instances["pipeline"] = ExecutableContainer.setup_from_config(manager=self,
                                                                                                     config=pipeline_config)

    def instantiate_executable_containers(self):
        for executable_container in self.executable_containers_instances.values():
            for entry_name in executable_container.entries_names:
                try:
                    entry = self.tasks_instances[entry_name]
                except KeyError:
                    entry = self.executable_containers_instances[entry_name]
                executable_container.entries.append(entry)

    def run(self):
        self.executable_containers_instances["pipeline"].run(manager=self)

    def get_task_instance(self, task_name):
        return self.tasks_instances[task_name]

    def get_executable_container_instance(self, ec_name):
        return self.executable_containers_instances[ec_name]


manager = Manager(config=test_config)
manager.logger = logging.getLogger()
manager.initiate_tasks()
manager.instantiate_tasks()
manager.initiate_executable_containers()
manager.instantiate_executable_containers()
a = 5
