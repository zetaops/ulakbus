# -*-  coding: utf-8 -*-
from __future__ import print_function, absolute_import, division

from __future__ import division
from io import BytesIO
from importlib import import_module

from SpiffWorkflow.bpmn.BpmnWorkflow import BpmnWorkflow
from SpiffWorkflow.bpmn.storage.BpmnSerializer import BpmnSerializer
from SpiffWorkflow.bpmn.storage.CompactWorkflowSerializer import CompactWorkflowSerializer
from SpiffWorkflow import Task
from SpiffWorkflow.specs import WorkflowSpec
from SpiffWorkflow.storage import DictionarySerializer
from SpiffWorkflow.bpmn.storage.Packager import Packager
from beaker.session import Session
from falcon import Request, Response
from pyoko.conf import settings
from zengine.camunda_parser import CamundaBMPNParser
from zengine.utils import DotDict

"""
ZEnging engine class
import, extend and override load_workflow and save_workflow methods
override the cleanup method if you need to run some cleanup code after each run cycle
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
__author__ = "Evren Esat Ozkan"


class InMemoryPackager(Packager):
    PARSER_CLASS = CamundaBMPNParser

    @classmethod
    def package_in_memory(cls, workflow_name, workflow_files):
        s = BytesIO()
        p = cls(s, workflow_name, meta_data=[])
        p.add_bpmn_files_by_glob(workflow_files)
        p.create_package()
        return s.getvalue()


class Condition(object):
    def __getattr__(self, name):
        return None

    def __str__(self):
        return self.__dict__


class Current(object):
    """
    :type task: Task | None
    :type response: Response | None
    :type request: Request | None
    :type spec: WorkflowSpec | None
    :type workflow: Workflow | None
    :type session: Session | None
    """
    def __init__(self, **kwargs):
        self.task_type = ''
        self.task_data = {}
        self.task = None
        self.name = ''
        self.input = {}
        self.output = {}
        self.response = None
        self.session = None
        self.spec = None
        self.workflow = None
        self.request = None
        self.workflow_name = ''
        self.update(**kwargs)

    def update(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


class ZEngine(object):
    ALLOWED_CLIENT_COMMANDS = ['edit_object', 'add_object', 'update_object', 'cancel', 'clear_wf']
    WORKFLOW_DIRECTORY = settings.WORKFLOW_PACKAGES_PATH,
    ACTIVITY_MODULES_PATH = settings.ACTIVITY_MODULES_IMPORT_PATH

    def __init__(self):
        self.use_compact_serializer = True
        if self.use_compact_serializer:
            self.serialize_workflow = self.compact_serialize_workflow
            self.deserialize_workflow = self.compact_deserialize_workflow
        self.current = Current()
        self.activities = {}
        self.workflow = BpmnWorkflow
        self.workflow_spec = WorkflowSpec

    def save_workflow(self, wf_name, serialized_wf_instance):
        if self.current.name.startswith('End'):
            del self.current.session['workflows'][wf_name]
            return
        if 'workflows' not in self.current.session:
            self.current.session['workflows'] = {}

        self.current.session['workflows'][wf_name] = serialized_wf_instance


    def load_workflow(self, workflow_name):
        try:
            return self.current.session['workflows'].get(workflow_name, None)
        except KeyError:
            return None

    def process_client_commands(self, request_data, wf_name):
        if 'clear_wf' in request_data and 'workflows' in self.current.session and \
                        wf_name in self.current.session['workflows']:
            del self.current.session['workflows'][wf_name]
        self.current.task_data = {'IS': Condition()}
        if 'cmd' in request_data and request_data['cmd'] in self.ALLOWED_CLIENT_COMMANDS:
            self.current.task_data[request_data['cmd']] = True
            self.current.task_data['cmd'] = request_data['cmd']
        else:
            for cmd in self.ALLOWED_CLIENT_COMMANDS:
                self.current.task_data[cmd] = None
        self.current.task_data['object_id'] = request_data.get('object_id', None)

    def _load_workflow(self):
        serialized_wf = self.load_workflow(self.current.workflow_name)
        if serialized_wf:
            return self.deserialize_workflow(serialized_wf)

    def deserialize_workflow(self, serialized_wf):
        return BpmnWorkflow.deserialize(DictionarySerializer(), serialized_wf)

    def compact_deserialize_workflow(self, serialized_wf):
        return CompactWorkflowSerializer().deserialize_workflow(serialized_wf,
                                                                workflow_spec=self.workflow.spec)

    def serialize_workflow(self):
        return self.workflow.serialize(serializer=DictionarySerializer())

    def compact_serialize_workflow(self):
        self.workflow.refresh_waiting_tasks()
        return CompactWorkflowSerializer().serialize_workflow(self.workflow, include_spec=False)

    def create_workflow(self):
        # wf_pkg_file = self.get_worfklow_spec()
        # self.workflow_spec = BpmnSerializer().deserialize_workflow_spec(wf_pkg_file)
        self.workflow_spec = self.get_worfklow_spec()
        return BpmnWorkflow(self.workflow_spec)

    def load_or_create_workflow(self):
        """
        Tries to load the previously serialized (and saved) workflow
        Creates a new one if it can't
        """
        self.workflow = self._load_workflow() or self.create_workflow()

    def get_worfklow_spec(self):
        """
        :return: workflow spec package
        """
        # FIXME: this is a very ugly workaround
        if isinstance(self.WORKFLOW_DIRECTORY, (str, unicode)):
            wfdir = self.WORKFLOW_DIRECTORY
        else:
            wfdir = self.WORKFLOW_DIRECTORY[0]
        # path = "{}/{}.zip".format(wfdir, self.current.workflow_name)
        # return open(path)
        path = "{}/{}.bpmn".format(wfdir, self.current.workflow_name)
        return BpmnSerializer().deserialize_workflow_spec(
            InMemoryPackager.package_in_memory(self.current.workflow_name, path))

    def _save_workflow(self):
        self.save_workflow(self.current.workflow_name, self.serialize_workflow())

    def set_current(self, **kwargs):
        """
        workflow_name should be given in kwargs
        :param kwargs:
        :return:
        """
        self.current.update(kwargs)
        self.current.session = self.current.request.env['session']
        self.current.input = self.current.request.context['data'],
        self.current.output = self.current.request.context['result'],
        if 'task' in kwargs:
            task = kwargs['task']
            self.current.task_type = task.task_spec.__class__.__name__
            self.current.spec = task.task_spec
            self.current.name = task.get_name()

    def complete_current_task(self):
        self.workflow.complete_task_from_id(self.current.task.id)

    def run(self):
        while 1:
            for task in self.workflow.get_tasks(state=Task.READY):
                self.set_current(task=task)
                self.current.task.data.update(self.current.task_data)
                print("TASK >> %s" % self.current.name, self.current.task.data, "TYPE",
                      self.current.task_type)
                if hasattr(self.current['spec'], 'service_class'):
                    print("RUN ACTIVITY: %s, %s" % (
                        self.current['spec'].service_class, self.current))
                    self.run_activity(self.current['spec'].service_class)
                else:
                    print('NO ACTIVITY!!')
                self.complete_current_task()
                if not self.current.task_type.startswith('Start'):
                    self._save_workflow()
            self.cleanup()

            if self.current.task_type == 'UserTask' or self.current.task_type.startswith('End'):
                break

    def run_activity(self, activity):
        """

        :param activity:
        :return:
        """
        if activity not in self.activities:
            mod_parts = activity.split('.')
            module = ".".join([self.ACTIVITY_MODULES_PATH] + mod_parts[:-1])
            method = mod_parts[-1]
            self.activities[activity] = getattr(import_module(module), method)
        self.activities[activity](self.current)

    # def process_activities(self):
    #     if 'activities' in self.current.spec.data:
    #         for cb in self.current.spec.data.activities:
    #             self.run_activity(cb)

    def cleanup(self):
        """
        this method will be called after each run cycle
        override this if you need some codes to be called after WF engine finished it's tasks and activities
        :return: None
        """
        pass
