# -*-  coding: utf-8 -*-
"""
"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.

from pyoko import field
from pyoko.model import Model, ListNode
from passlib.hash import pbkdf2_sha512

try:
    from zengine.lib.exceptions import PermissionDenied
except ImportError:
    class PermissionDenied(Exception):
        pass


class User(Model):
    username = field.String("Username", index=True)
    password = field.String("Password")
    name = field.String("First Name", index=True)
    surname = field.String("Surname", index=True)
    superuser = field.Boolean("Super user", default=False)

    class Meta:
        app = 'Sistem'
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"

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
    name = field.String("Name", index=True)
    code = field.String("Code Name", index=True)
    description = field.String("Description", index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Yetki"
        verbose_name_plural = "Yetkiler"

    def __unicode__(self):
        return "%s %s" % (self.name, self.description)


class AbstractRole(Model):
    id = field.Integer("ID No", index=True)
    name = field.String("Name", index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Soyut Rol"
        verbose_name_plural = "Soyut Roller"

    def __unicode__(self):
        return "%s" % self.name

    class Permissions(ListNode):
        permission = Permission()


class Unit(Model):
    name = field.String("Name", index=True)
    long_name = field.String("Name", index=True)
    yoksis_id = field.Integer("Unit ID", index=True, choices="yoksis_program_id")
    unit_type = field.String("Unit Type", index=True)
    parent_unit_id = field.Integer("Parent Unit ID", index=True)
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

    class Meta:
        app = 'Sistem'
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        search_fields = ['name']
        list_fields = ['name', 'unit_type']

    def __unicode__(self):
        return '%s %s' % (self.name, self.key)


class Role(Model):
    abstract_role = AbstractRole()
    user = User()
    unit = Unit()

    class Meta:
        app = 'Sistem'
        verbose_name = "Rol"
        verbose_name_plural = "Roller"

    def __unicode__(self):
        try:
            return "%s %s" % (self.abstract_role.name, self.user.username)
        except:
            return "Role #%s" % self.key

    class Permissions(ListNode):
        permission = Permission()

    def get_permissions(self):
        return [p.permission.code for p in self.Permissions]

    def add_permission(self, perm):
        self.Permissions(permission=perm)
        self.save()

    def add_permission_by_name(self, code, save=False):
        if not save:
            return ["%s | %s" % (p.name, p.code) for p in
                    Permission.objects.filter(code='*' + code + '*')]
        for p in Permission.objects.filter(code='*' + code + '*'):
            if p not in self.Permissions:
                self.Permissions(permission=p)
        if p:
            self.save()


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

    def get_permissions(self):
        # TODO: We can move caching of permissions out of session to
        # speedup the login. with proper invalidation routine
        if 'permissions' in self.session:
            return self.session['permissions']
        else:
            perms = self.get_role().get_permissions()
            self.session['permissions'] = perms
            return perms

    def has_permission(self, perm):
        # return True
        return perm in self.get_permissions()

    def get_user(self):
        if 'user_data' in self.session:
            user = User()
            user.set_data(self.session['user_data'])
            user.key = self.session['user_id']
        elif 'user_id' in self.session:
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
