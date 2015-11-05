.. Ulakbus API Documentation documentation master file, created by
sphinx-quickstart on Tue Nov  3 20:47:12 2015.
You can adapt this file completely to your liking, but it should at least
contain the root `toctree` directive.

Ulakbus API Documentation
=========================

Icindekiler:

.. toctree::
   :maxdepth: 3

ULAKBUS
#######

ZATO WRAPPER
++++++++++++
.. automodule:: ulakbus.services.zato_wrapper
   :members:
   :undoc-members:
   :show-inheritance:


HITAP
+++++

HITAP SERVISI YAZMAK
--------------------
.. currentmodule:: ulakbus.services.zato_wrapper

Hitap servislerini :func:ulakbus.services.HitapService extend edip kullanabilirsiniz.

.. autoclass:: HitapService

HIZMET CETVELI
--------------
Bilgilerin Hitaptan cekilmesi

.. autoclass:: HitapHizmetCetvelGetir

Bilgilerin Hitaptan cekilmesi ve senkronize edilmesi

.. autoclass:: HitapHizmetCetveliSenkronizeEt

PYOKO
#####
PYOKO MODEL
+++++++++++
.. automodule:: pyoko.db.base
 :members:
 :undoc-members:
 :show-inheritance:

