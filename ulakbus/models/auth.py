# -*-  coding: utf-8 -*-
"""Auth Modülü

Bu modül Ulakbüs uygulaması için authorization ile ilişkili data modellerini içerir.

"""

# Copyright (C) 2015 ZetaOps Inc.
#
# This file is licensed under the GNU General Public License v3
# (GPLv3).  See LICENSE.txt for details.
import hashlib

from pyoko import field
from pyoko import Model, ListNode
from passlib.hash import pbkdf2_sha512
from pyoko import LinkProxy
from pyoko.conf import settings
from pyoko.lib.utils import lazy_property

from zengine.auth.permissions import get_all_permissions
from zengine.dispatch.dispatcher import receiver

from zengine.signals import crud_post_save
from zengine.lib.cache import Cache
from zengine.messaging.lib import BaseUser

try:
    from zengine.lib.exceptions import PermissionDenied
except ImportError:
    class PermissionDenied(Exception):
        pass


class User(Model, BaseUser):
    """User modeli

    User modeli Ulakbus temel kullanıcı modelidir. Temel kullanıcı
    bilgilerini içerir. Ulakbus'de işlem yapan/yapılan her kullanıcıya
    ait bir ve tek kullanıcı olması zorunludur.

    """
    username = field.String("Username", index=True)
    password = field.String("Password")
    avatar = field.File("Profile Photo", random_name=True, required=False)
    name = field.String("First Name", index=True)
    surname = field.String("Surname", index=True)
    superuser = field.Boolean("Super user", default=False)

    class Meta:
        app = 'Sistem'
        verbose_name = "Kullanıcı"
        verbose_name_plural = "Kullanıcılar"
        search_fields = ['username', 'name', 'surname']

    @lazy_property
    def full_name(self):
        return "%s %s" % (self.name, self.surname)

    def pre_save(self):
        self.encrypt_password()

    def post_creation(self):
        self.prepare_channels()

    def get_avatar_url(self):
        if self.avatar:
            return BaseUser.get_avatar_url(self)
        else:
            # FIXME: This is for fun, remove when we resolve static hosting problem
            return "https://www.gravatar.com/avatar/%s" % hashlib.md5(
                "%s@gmail.com" % self.username).hexdigest()


class Permission(Model):
    """Permission modeli

    Kullanıcı yetkilerinin tanımlandığı bilgilerin bulunguğu modeldir.

    """
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

    def get_permitted_users(self):
        """
        Get users which has this permission

        Returns:
            User list
        """
        users = set()
        for ars in self.abstract_role_set.objects.filter():
            for r in ars.role_set.objects.filter():
                users.add(r.user)
        for r in self.role_set.objects.filter():
            users.add(r.user)
        return users

    def get_permitted_roles(self):
        """
        Get roles which has this permission

        Returns:
            Role list
        """
        roles = set()
        for ars in self.abstract_role_set.objects.filter():
            for r in ars.role_set.objects.filter():
                roles.add(r)
        for r in self.role_set.objects.filter():
            roles.add(r)
        return roles


class AbstractRole(Model):
    """AbstractRole Modeli

    Soyut Rol modeli yetkilerin gruplandığı temel role modelidir.

    """
    id = field.Integer("ID No", index=True)
    name = field.String("İsim", index=True)
    read_only = field.Boolean("Read Only")

    class Meta:
        app = 'Sistem'
        verbose_name = "Soyut Rol"
        verbose_name_plural = "Soyut Roller"
        search_fields = ['id', 'name']

    def __unicode__(self):
        return "%s" % self.name

    def get_permissions(self):
        """
        Soyut role ait Permission nesnelerini bulur ve code değerlerini
        döner.

        Returns:
            list: Permission code değerleri

        """
        return [p.permission.code for p in self.Permissions if p.permission.code]

    def add_permission(self, perm):
        """
        Soyut Role Permission nesnesi tanımlamayı sağlar.

        Args:
            perm (object):

        """
        self.Permissions(permission=perm)
        PermissionCache.flush()
        self.save()

    def add_permission_by_name(self, code, save=False):
        """
        Soyut role Permission eklemek veya eklenebilecek Permission
        nesnelerini verilen ``code`` parametresine göre listelemek olmak
        üzere iki şekilde kullanılır.

        Args:
            code (str): Permission nesnelerini filtre etmekte kullanılır
            save (bool): True ise Permission ekler, False ise Permission
                listesi döner.

        Returns:
            list: ``save`` False ise Permission listesi döner.

        """
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
    """Unit modeli

    Kullanıcılara rol tanımlarken kullanılan, kullanıcının hangı birimde
    olduğunu taşıyan modeldir.
    Akademik ve idari birimlerin özelliklerini taşır.

    """
    name = field.String("İsim", index=True)
    long_name = field.String("Uzun İsim", index=True)
    yoksis_no = field.Integer("Yoksis ID", index=True)
    unit_type = field.String("Birim Tipi", index=True)
    parent_unit_no = field.Integer("Üst Birim ID", index=True)
    current_situation = field.String("Guncel Durum", index=True)
    language = field.String("Öğrenim Dili", index=True)
    learning_type = field.String("Öğrenme Tipi", index=True)
    osym_code = field.String("ÖSYM Kodu", index=True)
    opening_date = field.Date("Açılış Tarihi", index=True)
    learning_duration = field.Integer("Öğrenme Süresi", index=True)
    english_name = field.String("İngilizce Birim Adı.", index=True)
    quota = field.Integer("Birim Kontenjan", index=True)
    city_code = field.Integer("Şehir Kodu", index=True)
    district_code = field.Integer("Semt Kodu", index=True)
    unit_group = field.Integer("Birim Grup", index=True)
    foet_code = field.Integer("FOET Kodu", index=True)  # yoksis KILAVUZ_KODU mu?
    is_academic = field.Boolean("Akademik")
    is_active = field.Boolean("Aktif")
    uid = field.Integer(index=True)
    parent = LinkProxy('Unit', verbose_name='Üst Birim', reverse_name='alt_birimler')

    @classmethod
    def get_user_keys(cls, unit_key):
        return cls.get_user_keys_by_yoksis(Unit.objects.get(unit_key).yoksis_no)
        stack = Role.objects.filter(unit_id=unit_key).values_list('user_id', flatten=True)
        for unit_key in cls.objects.filter(parent_id=unit_key).values_list('key', flatten=True):
            stack.extend(cls.get_user_keys(unit_key))
        return stack

    @classmethod
    def get_user_keys_by_yoksis(cls, yoksis_no):
        # because we don't refactor our data to use Unit.parent, yet!
        stack = Role.objects.filter(unit_id=Unit.objects.get(yoksis_no=yoksis_no).key).values_list('user_id', flatten=True)
        for yoksis_no in cls.objects.filter(parent_unit_no=yoksis_no).values_list('yoksis_no', flatten=True):
            stack.extend(cls.get_user_keys_by_yoksis(yoksis_no))
        return stack

    class Meta:
        app = 'Sistem'
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        search_fields = ['name', 'yoksis_no']
        list_fields = ['name', 'unit_type']

    def __unicode__(self):
        return '%s - %s - %s' % (self.name, self.english_name, self.yoksis_no)


ROL_TIPI = [
    (1, 'Personel'),
    (2, 'Ogrenci'),
    (3, 'Harici')
]


class PermissionCache(Cache):
    """PermissionCache sınıfı Kullanıcıya Permission nesnelerinin
    kontrolünü hızlandırmak için yetkileri cache bellekte saklamak ve
    gerektiğinde okumak için oluşturulmuştur.
    """
    PREFIX = 'PRM'

    def __init__(self, role_id):
        super(PermissionCache, self).__init__(role_id)


class Role(Model):
    """Role modeli
    Kullanıcıların rol ile ilişkilendiği modeldir. Kullanıcıların birden
    fazla rolü olabilir. Kullanıcıya atanmış Rol (Role) ve rolde
    tanımlanmış Soyut Rol (AbstractRole) nesnelerindeki yetkiler bir
    araya getirilerek kullanıcının yetkileri belirlenir.

    """
    abstract_role = AbstractRole()
    user = User()
    unit = Unit()
    typ = field.Integer("Rol Tipi", choices=ROL_TIPI)
    name = field.String("Rol Adı", hidden=True)

    class Meta:
        app = 'Sistem'
        verbose_name = "Rol"
        verbose_name_plural = "Roller"
        search_fields = ['name']
        list_fields = []
        crud_extra_actions = [{'name': 'İzinleri Düzenle', 'wf': 'permissions', 'show_as': 'button'}]

    @property
    def is_staff(self):
        return self.typ == 1

    @property
    def is_student(self):
        return self.typ == 2

    def get_user(self):
        """
        Returns:
            object: user nesnesi
        """
        return self.user

    def __unicode__(self):
        return "Role %s" % self.name or (self.key if self.is_in_db() else '')

    class Permissions(ListNode):
        permission = Permission()

        def __unicode__(self):
            return "%s" % self.permission

    def get_db_permissions(self):
        """
        Role nesnesinin AbstractRole özelliğine ait yetkileri getirir.

        Returns:
            list: yetki listesi

        """
        return [p.permission.code for p in self.Permissions if p.permission.code] + (
            self.abstract_role.get_permissions() if self.abstract_role.key else [])

    def _cache_permisisons(self, pcache):
        """
        Cache belleğe yetkileri yazar ve bu yetkileri döner.
        Args:
            pcache: PermissionCache nesnesi

        Returns:
            list: yetki listesi

        """
        perms = self.get_db_permissions()
        pcache.set(perms)
        return perms

    def get_permissions(self):
        """Bellekteki Permission nesnelerini döner.
        Returns:
            object:
        """
        pcache = PermissionCache(self.key)
        return pcache.get() or self._cache_permisisons(pcache)

    def add_permission(self, perm):
        """Yeni Permission ekler ve bellekteki Role nesnesine ait
        Permission nesnelerini siler.

        Args:
            perm: Permission nesnesi

        """
        self.Permissions(permission=perm)
        PermissionCache(self.key).delete()
        self.save()

    def remove_permission(self, perm):
        """
        Removes a :class:`Permission` from the role

        Args:
             perm: :class:`Permission` object.
        """
        del self.Permissions[perm.key]
        PermissionCache(self.key).delete()
        self.save()

    def add_permission_by_name(self, code, save=False):
        """
        Role nesnesine Permission eklemek veya eklenebilecek Permission
        nesnelerini verilen ``code`` parametresine göre listelemek olmak
        üzere iki şekilde kullanılır.

        Args:
            code (str): Permission nesnelerini filtre etmekte kullanılır.
            save (bool): True ise Permission ekler, False ise Permission
                listesi döner.

        Returns:
            list: ``save`` False ise Permission listesi döner.

        """
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
        """
        Nesnenin soyut rolü veya bir kullanıcısı varsa soyut rol ismi ve
        kullanıcı username'ini birleştirerek bir name stringi oluşturur.
        Bu iki özellik yok ise Role key'ini kullanarak bir string değer
        üretir.
        Returns:
            str:

        """
        if self.abstract_role.key or self.user.key:
            return "%s | %s" % (self.abstract_role.name, self.user.username)
        else:
            return "Role #%s" % self.key if self.is_in_db() else ''

    def pre_save(self):
        """
        Kayıt edilmeden önce nesnenin adını ``_make_name()`` metodunu
        çağırarak oluşturur.
        """
        self.name = self._make_name()


class LimitedPermissions(Model):
    """LimitedPermissions modeli
    Bu modelde tutulan bilgilerle mevcut yetkilere sınırlandırmalar
    getirilir.

    - Başlangıç ve bitiş tarihine göre sınırlandırma uygulanan yetkiler
    o tarih aralığında geçerli olur.

    - Verilen IPList özelliğine göre bu IPList listesi içindeki
    ip'lerden gelen requestlere cevap verecek şekilde kısıtlanır.

    """
    restrictive = field.Boolean("Sınırlandırıcı", default=False)
    time_start = field.String("Başlama Tarihi", index=True)
    time_end = field.String("Bitiş Tarihi", index=True)

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
    """AuthBackend sınıfı Auth modulüne ait işlemleri gerçekleştirmek
    için kullanılan bir dizi metodu içerir.

    """

    def __init__(self, current):
        self.session = current.session
        self.current = current
        self.perm_cache = None

    def get_permissions(self):
        """Bellekteki Permission nesnelerini döner.
        Returns:
            object:
        """
        perm_cache = PermissionCache(self.session['role_id'])
        return perm_cache.get() or self.get_role().get_permissions()

    def has_permission(self, perm):
        """Verilen ``perm`` Permission nesnesinin rolde bulunup
        bulunmadığını döner.

        Args:
            perm:

        Returns:
            bool:

        """
        # return True
        return perm in self.get_permissions()

    def get_user(self):
        """Session'da bir kullanıcı varsa sesion'daki kullanıcıyı yoksa
        boş bir kullanıcı nesnesi döner.

        Returns:
            object: User nesnesi

        """
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
        Kullanıcı datasını session'a yazar.

        Args:
            user: User nesnesi

        Returns:

        """
        user = user
        self.session['user_id'] = user.key
        self.session['user_data'] = user.clean_value()

        # TODO: this should be remembered from previous login
        default_role = user.role_set[0].role
        # self.session['role_data'] = default_role.clean_value()
        self.session['role_id'] = default_role.key
        self.current.role_id = default_role.key
        self.current.user_id = user.key
        self.perm_cache = PermissionCache(default_role.key)
        self.session['permissions'] = default_role.get_permissions()

    def get_role(self):
        """session'da bir role_id varsa bu id'deki Role nesnesini döner.
        Yoksa session objesini siler ve PermissionDenied hatası verir.

        Returns:
            object: Role nesnesi
        Raises:
            PermissionDenied:

        """
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
        """Kullanıcı adı ve şifresini kontrol eder ve eğer doğruysa
        kullanıcı datasını session'a yazar.

        Args:
            username:
            password:

        Returns:
            bool:

        """
        user = User.objects.get(username=username)
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
    """Verilen sender nesnesine bağlı Permission nesnelerini cache
    bellekten siler.

    Eğer sender nesnesi bir AbstractRole ise PermissionCache'i temizler.

    Args:
        sender:
        *args:
        **kwargs:

    """
    if sender.model_class.__name__ == 'Role':
        PermissionCache(kwargs['object'].key).delete()
    elif sender.model_class.__name__ == 'AbstractRole':
        PermissionCache.flush()


def ulakbus_permissions():
    """Bu metot Ulakbus'e ait tüm yetkileri birleştirerek döner.

    Returns:
        list: Ulakbus'e ait tüm yetkiler

    """
    default_perms = get_all_permissions()
    from ulakbus.views.reports import ReporterRegistry
    report_perms = ReporterRegistry.get_permissions()
    return default_perms + report_perms
