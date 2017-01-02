# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from zengine.messaging.model import Message, Channel, Subscriber
from .personel import *
from .auth import *
from .ogrenci import *
from .hitap.hitap import *
from .buildings_rooms import *
from .form import *
from .ders_sinav_programi import *
from zengine.models.workflow_manager import DiagramXML, WFInstance, Task, BPMNWorkflow
from .zato import *
