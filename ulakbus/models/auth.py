# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import field
from pyoko import Model, ListNode
from passlib.hash import pbkdf2_sha512
from pyoko import LinkProxy

from zengine.auth.permissions import get_all_permissions
from zengine.dispatch.dispatcher import receiver
from zengine.signals import crud_post_save
from zengine.lib.cache import Cache

try:
    from zengine.lib.exceptions import PermissionDenied
except ImportError:
    class PermissionDenied(Exception):
        pass


class User(Model):
    username = field.String("Username", index=True)
    password = field.String("Password")
    avatar = field.File("Profile Photo", random_name=True)
    name = field.String("First Name", index=True)
    surname = field.String("Surname", index=True)
    superuser = field.Boolean("Super user", default=False)

    class Meta:
        app = 'Sistem'
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        search_fields = ['username', 'name', 'surname']

    def __unicode__(self):
        return "User %s" % self.username

    def __repr__(self):
        return "User_%s" % self.key

    def set_password(self, raw_password):
        self.password = pbkdf2_sha512.encrypt(raw_password, rounds=10000,
                                              salt_size=10)

    def check_password(self, raw_password):
        return pbkdf2_sha512.verify(raw_password, self.password)

    def get_role(self, role_id):
        return self.role_set.node_dict[role_id]


class Permission(Model):
    name = field.String("İsim", index=True)
    code = field.String("Kod Adı", index=True)
    description = field.String("Tanım", index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Yetki"
        verbose_name_plural = "Yetkiler"
        list_fields = ["name", "code", "description"]
        search_fields = ["name", "code", "description"]

    def __unicode__(self):
        return "%s %s" % (self.name, self.code)


class AbstractRole(Model):
    id = field.Integer("ID No", index=True)
    name = field.String("Name", index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Soyut Rol"
        verbose_name_plural = "Soyut Roller"
        search_fields = ['id', 'name']

    def __unicode__(self):
        return "%s" % self.name

    def get_permissions(self):
        return [p.permission.code for p in self.Permissions]

    def add_permission(self, perm):
        self.Permissions(permission=perm)
        PermissionCache.flush()
        self.save()

    def add_permission_by_name(self, code, save=False):
        if not save:
            return ["%s | %s" % (p.name, p.code) for p in
                    Permission.objects.filter(code__contains=code)]
        PermissionCache.flush()
        for p in Permission.objects.filter(code__contains=code):
            if p not in self.Permissions:
                self.Permissions(permission=p)
        if p:
            self.save()

    class Permissions(ListNode):
        permission = Permission()


class Unit(Model):
    name = field.String("Name", index=True)
    long_name = field.String("Name", index=True)
    yoksis_no = field.Integer("Yoksis ID", index=True)
    unit_type = field.String("Unit Type", index=True)
    parent_unit_no = field.Integer("Parent Unit ID", index=True)
    current_situation = field.String("Current Situation", index=True)
    language = field.String("Learning Language", index=True)
    learning_type = field.String("Learning Type", index=True)
    osym_code = field.String("ÖSYM Code", index=True)
    opening_date = field.Date("Opening Date", index=True)
    learning_duration = field.Integer("Learning Duration", index=True)
    english_name = field.String("Unit Name in English", index=True)
    quota = field.Integer("Unit Quota", index=True)
    city_code = field.Integer("City Code", index=True)
    district_code = field.Integer("District Code", index=True)
    unit_group = field.Integer("Unit Group", index=True)
    foet_code = field.Integer("FOET Code", index=True)  # yoksis KILAVUZ_KODU mu?
    is_academic = field.Boolean("Is Academic")
    is_active = field.Boolean("Is Active")
    uid = field.Integer(index=True)
    parent = LinkProxy('Unit', verbose_name='Üst Birim', reverse_name='alt_birimler')

    class Meta:
        app = 'Sistem'
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        search_fields = ['name']
        list_fields = ['name', 'unit_type']

    def __unicode__(self):
        return '%s - %s - %s' % (self.name, self.english_name, self.yoksis_no)


ROL_TIPI = [
    (1, 'Personel'),
    (2, 'Ogrenci'),
    (3, 'Harici')
]


class PermissionCache(Cache):
    PREFIX = 'PRM'

    def __init__(self, role_id):
        super(PermissionCache, self).__init__(role_id)


class Role(Model):
    abstract_role = AbstractRole()
    user = User()
    unit = Unit()
    typ = field.Integer("Rol tipi", choices=ROL_TIPI)
    name = field.String("Rol Adı", hidden=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Rol"
        verbose_name_plural = "Roller"
        search_fields = ['name']
        list_fields = []

    def get_user(self):
        return self.user

    def __unicode__(self):
        return "Role %s" % self.name or (self.key if self.is_in_db() else '')

    class Permissions(ListNode):
        permission = Permission()

        def __unicode__(self):
            return "%s" % self.permission

    def get_db_permissions(self):
        return [p.permission.code for p in self.Permissions] + (
            self.abstract_role.get_permissions() if self.abstract_role.key else [])

    def _cache_permisisons(self, pcache):
        perms = self.get_db_permissions()
        pcache.set(perms)
        return perms

    def get_permissions(self):
        pcache = PermissionCache(self.key)
        return pcache.get() or self._cache_permisisons(pcache)

    def add_permission(self, perm):
        self.Permissions(permission=perm)
        PermissionCache(self.key).delete()
        self.save()

    def add_permission_by_name(self, code, save=False):
        if not save:
            return ["%s | %s" % (p.name, p.code) for p in
                    Permission.objects.filter(code__contains=code)]
        PermissionCache(self.key).delete()
        for p in Permission.objects.filter(code__contains=code):
            if p not in self.Permissions:
                self.Permissions(permission=p)
        if p:
            self.save()

    def _make_name(self):
        if self.abstract_role.key or self.user.key:
            return "%s | %s" % (self.abstract_role.name, self.user.username)
        else:
            return "Role #%s" % self.key if self.is_in_db() else ''

    def save(self):
        self.name = self._make_name()
        super(Role, self).save()


class LimitedPermissions(Model):
    restrictive = field.Boolean(default=False)
    time_start = field.String("Start Time", index=True)
    time_end = field.String("End Time", index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Sınırlandırılmış Yetki"
        verbose_name_plural = "Sınırlandırılmış Yetkiler"

    def __unicode__(self):
        return "%s - %s" % (self.time_start, self.time_end)

    class IPList(ListNode):
        ip = field.String()

    class Permissions(ListNode):
        permission = Permission()

    class AbstractRoles(ListNode):
        abstract_role = AbstractRole()

    class Roles(ListNode):
        role = Role()


class AuthBackend(object):
    def __init__(self, current):
        self.session = current.session
        self.current = current
        self.perm_cache = None

    def get_permissions(self):
        perm_cache = PermissionCache(self.session['role_id'])
        return perm_cache.get() or self.get_role().get_permissions()

    def has_permission(self, perm):
        # return True
        return perm in self.get_permissions()

    def get_user(self):
        # if 'user_data' in self.session:
        #     user = User()
        #     user.set_data(self.session['user_data'], from_db=True)
        #     user.key = self.session['user_id']
        # elif 'user_id' in self.session:
        if 'user_id' in self.session:
            user = User.objects.get(self.session['user_id'])
        else:
            user = User()
        return user

    def set_user(self, user):
        """
        insert current user's data to session

        :param User user: logged in user
        """
        user = user
        self.session['user_id'] = user.key
        self.session['user_data'] = user.clean_value()

        # TODO: this should be remembered from previous login
        default_role = user.role_set[0].role
        # self.session['role_data'] = default_role.clean_value()
        self.session['role_id'] = default_role.key
        self.current.user_id = default_role.key
        self.perm_cache = PermissionCache(default_role.key)
        self.session['permissions'] = default_role.get_permissions()

    def get_role(self):
        # if 'role_data' in self.session:
        #     role = Role()
        #     role.set_data(self.session['role_data'])
        # if 'role_id' in self.session:
        #     role.key = self.session['role_id']
        # return role
        if 'role_id' in self.session:
            return Role.objects.get(self.session['role_id'])
        else:
            # TODO: admins should be informed about a user without a role
            self.session.delete()
            raise PermissionDenied("Your don't have a \"Role\" in this system")

    def authenticate(self, username, password):
        user = User.objects.filter(username=username).get()
        is_login_ok = user.check_password(password)
        if is_login_ok:
            self.set_user(user)
        else:
            pass
            # TODO: failed login attempts for a user should be counted
            # for prevention of brute force attacks

        return is_login_ok


# invalidate permission cache on crud updates on Role and AbstractRole models
@receiver(crud_post_save)
def clear_perm_cache(sender, *args, **kwargs):
    if sender.model_class.__name__ == 'Role':
        PermissionCache(kwargs['object'].key).delete()
    elif sender.model_class.__name__ == 'AbstractRole':
        PermissionCache.flush()

def ulakbus_permissions():
    default_perms = get_all_permissions()
    from ulakbus.views.reports import ReporterRegistry
    report_perms = ReporterRegistry.get_permissions()
    return default_perms + report_perms
