# -*-  coding: utf-8 -*-

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import Model, field
from zengine.lib.translation import gettext_lazy as __
from ulakbus.models.sqlalchemy.db_session import Base
from sqlalchemy import Column, Integer, String, Boolean


#
# >>> class User(Base):
# ...     __tablename__ = 'users'
# ...
# ...     id = Column(Integer, primary_key=True)
# ...     name = Column(String)
# ...     fullname = Column(String)
# ...     password = Column(String)
# ...
# ...     def __repr__(self):
# ...        return "<User(name='%s', fullname='%s', password='%s')>" % (
# ...                             self.name, self.fullname, self.password)


class ZatoServiceFile(Base):
    __tablename__ = 'zato_service_file'

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer)
    service_payload_name = Column(String)
    service_payload = Column(String)
    deploy = Column(Boolean, default=False)

    def __unicode__(self):
        return self.service_payload_name


class ZatoServiceChannel(Model):
    __tablename__ = 'zato_service_channel'

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer)
    channel_id = field.Integer(__(u"Channel id"))
    channel_name = Column(String)
    channel_connection = Column(String)
    channel_transport = Column(String)
    channel_url_path = Column(String)
    channel_data_format = Column(String)
    channel_is_internal = Column(Boolean, default=False)
    channel_is_active = Column(Boolean, default=True)
    service_id = field.Integer(__(u"Service Id"))
    service_name = Column(String)
    class_name = Column(String)
    module_path = Column(String)
    deploy = Column(Boolean, default=False)

    def __unicode__(self):
        return self.channel_name
