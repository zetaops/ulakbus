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
from pyoko import LinkProxy
from pyoko.conf import settings
from pyoko.lib.utils import lazy_property

from zengine.auth.permissions import get_all_permissions
from zengine.dispatch.dispatcher import receiver
from zengine.lib.decorators import role_getter

from zengine.signals import crud_post_save
from zengine.lib.cache import Cache
from zengine.lib.translation import gettext_lazy as _, gettext
from zengine.messaging.lib import BaseUser
from zengine.lib import translation

try:
    from zengine.lib.exceptions import PermissionDenied
except ImportError:
    class PermissionDenied(Exception):
        pass

from pyoko.exceptions import IntegrityError


class User(Model, BaseUser):
    """User modeli

    User modeli Ulakbus temel kullanıcı modelidir. Temel kullanıcı
    bilgilerini içerir. Ulakbus'de işlem yapan/yapılan her kullanıcıya
    ait bir ve tek kullanıcı olması zorunludur.

    """
    avatar = field.File(_(u"Profil Fotoğrafı"), random_name=True, required=False)
    username = field.String(_(u"Kullanıcı Adı"), index=True, unique=True)
    password = field.String(_(u"Parola"))
    e_mail = field.String(_(u"E-Posta"), index=True, unique=True)
    name = field.String(_(u"Ad"), index=True)
    surname = field.String(_(u"Soyad"), index=True)
    superuser = field.Boolean(_(u"Super user"), default=False)
    last_login_role_key = field.String(_(u"Son Giriş Yapılan Rol"))
    locale_language = field.String(
        _(u"Tercih Edilen Dil Formatı"),
        index=False,
        default=settings.DEFAULT_LANG,
        choices=translation.available_translations.items()
    )
    locale_datetime = field.String(_(u"Tercih Edilen Gün ve Zaman Formatı"), index=False,
                                   default=settings.DEFAULT_LOCALIZATION_FORMAT,
                                   choices=translation.available_datetimes.items())
    locale_number = field.String(_(u"Tercih Edilen Sayı Formatı"), index=False,
                                 default=settings.DEFAULT_LOCALIZATION_FORMAT,
                                 choices=translation.available_numbers.items())

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Kullanıcı")
        verbose_name_plural = _(u"Kullanıcılar")
        search_fields = ['username', 'name', 'surname']

    @lazy_property
    def full_name(self):
        return "%s %s" % (self.name, self.surname)

    def last_login_role(self):
        """
        Eğer kullanıcı rol geçişi yaparsa, kullanıcının last_login_role_key
        field'ına geçiş yaptığı rolün keyi yazılır. Kullanıcı çıkış yaptığında
         ve tekrardan giriş yaptığında son rolü bu field'dan öğrenilir. Eğer
        kullanıcının last_login_role_key field'ı dolu ise rol bilgisi oradan alınır.
        Yoksa kullanıcının role_set'inden default rolü alınır.

        """
        last_key = self.last_login_role_key
        return Role.objects.get(last_key) if last_key else self.role_set[0].role

    def pre_save(self):
        if not self.username or not self.password:
            raise IntegrityError
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

    def __unicode__(self):
        return "%s %s" % (self.name, self.surname)

class Permission(Model):
    """Permission modeli

    Kullanıcı yetkilerinin tanımlandığı bilgilerin bulunguğu modeldir.

    """
    name = field.String(_(u"İsim"), index=True)
    code = field.String(_(u"Kod Adı"), index=True)
    description = field.String(_(u"Tanım"), index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Yetki")
        verbose_name_plural = _(u"Yetkiler")
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
    id = field.Integer(_(u"ID No"), index=True)
    name = field.String(_(u"İsim"), index=True)
    read_only = field.Boolean(_(u"Read Only"))

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Soyut Rol")
        verbose_name_plural = _(u"Soyut Roller")
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
    name = field.String(_(u"İsim"), index=True)
    long_name = field.String(_(u"Uzun İsim"), index=True)
    yoksis_no = field.Integer(_(u"Yoksis ID"), index=True)
    unit_type = field.String(_(u"Birim Tipi"), index=True)
    parent_unit_no = field.Integer(_(u"Üst Birim ID"), index=True)
    current_situation = field.String(_(u"Guncel Durum"), index=True)
    language = field.String(_(u"Öğrenim Dili"), index=True)
    learning_type = field.String(_(u"Öğrenme Tipi"), index=True)
    osym_code = field.String(_(u"ÖSYM Kodu"), index=True)
    opening_date = field.Date(_(u"Açılış Tarihi"), index=True)
    learning_duration = field.Integer(_(u"Öğrenme Süresi"), index=True)
    english_name = field.String(_(u"İngilizce Birim Adı."), index=True)
    quota = field.Integer(_(u"Birim Kontenjan"), index=True)
    city_code = field.Integer(_(u"Şehir Kodu"), index=True)
    district_code = field.Integer(_(u"Semt Kodu"), index=True)
    unit_group = field.Integer(_(u"Birim Grup"), index=True)
    foet_code = field.Integer(_(u"FOET Kodu"), index=True)  # yoksis KILAVUZ_KODU mu?
    is_academic = field.Boolean(_(u"Akademik"))
    is_active = field.Boolean(_(u"Aktif"))
    uid = field.Integer(index=True)
    parent = LinkProxy('Unit', verbose_name=_(u'Üst Birim'), reverse_name='alt_birimler')
    # parent = field.String(verbose_name='Üst Birim') # fake

    @classmethod
    def get_role_keys(cls, unit_key):
        """recursively gets all roles (keys) under given unit"""
        return cls.get_role_keys_by_yoksis(Unit.objects.get(unit_key).yoksis_no)
        # stack = Role.objects.filter(unit_id=unit_key).values_list('user_id', flatten=True)
        # for unit_key in cls.objects.filter(parent_id=unit_key).values_list('key', flatten=True):
        #     stack.extend(cls.get_role_keys(unit_key))
        # return stack

    @classmethod
    def get_role_keys_by_yoksis(cls, yoksis_no):
        # because we don't refactor our data to use Unit.parent, yet!
        stack = Role.objects.filter(unit_id=Unit.objects.get(yoksis_no=yoksis_no).key).values_list('key', flatten=True)
        for yoksis_no in cls.objects.filter(parent_unit_no=yoksis_no).values_list('yoksis_no', flatten=True):
            stack.extend(cls.get_role_keys_by_yoksis(yoksis_no))
        return stack

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Unit")
        verbose_name_plural = _(u"Units")
        search_fields = ['name', 'yoksis_no']
        list_fields = ['name', 'unit_type']

    def __unicode__(self):
        return '%s - %s - %s' % (self.name, self.english_name, self.yoksis_no)


ROL_TIPI = [
    (1, _(u'Personel')),
    (2, _(u'Ogrenci')),
    (3, _(u'Harici'))
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
    typ = field.Integer(_(u"Rol Tipi"), choices=ROL_TIPI)
    name = field.String(_(u"Rol Adı"), hidden=True)

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Rol")
        verbose_name_plural = _(u"Roller")
        search_fields = ['name']
        list_fields = []
        crud_extra_actions = [{'name': _(u'İzinleri Düzenle'), 'wf': 'permissions', 'show_as': 'button'}]

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
        return gettext(u"Role %s") % self.name or (self.key if self.is_in_db() else '')

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


    @classmethod
    @role_getter("Bölüm Başkanları")
    def get_bolum_baskanlari(cls):
        """fake"""
        return []

    def send_notification(self, title, message, typ=1, url=None, sender=None):
        """
        sends a message to user of this role's private mq exchange

        """
        self.user.send_notification(title=title, message=message, typ=typ, url=url, sender=sender)


class LimitedPermissions(Model):
    """LimitedPermissions modeli
    Bu modelde tutulan bilgilerle mevcut yetkilere sınırlandırmalar
    getirilir.

    - Başlangıç ve bitiş tarihine göre sınırlandırma uygulanan yetkiler
    o tarih aralığında geçerli olur.

    - Verilen IPList özelliğine göre bu IPList listesi içindeki
    ip'lerden gelen requestlere cevap verecek şekilde kısıtlanır.

    """
    restrictive = field.Boolean(_(u"Sınırlandırıcı"), default=False)
    time_start = field.String(_(u"Başlama Tarihi"), index=True)
    time_end = field.String(_(u"Bitiş Tarihi"), index=True)

    class Meta:
        app = 'Sistem'
        verbose_name = _(u"Sınırlandırılmış Yetki")
        verbose_name_plural = _(u"Sınırlandırılmış Yetkiler")

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


        """
        self.session['user_id'] = user.key
        self.session['user_data'] = user.clean_value()
        role = user.last_login_role()
        self.session['role_id'] = role.key
        self.current.role_id = role.key
        self.current.user_id = user.key
        self.perm_cache = PermissionCache(role.key)
        self.session['permissions'] = role.get_permissions()

    def get_role(self):
        """session'da bir role_id varsa bu id'deki Role nesnesini döner.
        Yoksa session objesini siler ve PermissionDenied hatası verir.

        Returns:
            object: Role nesnesi
        Raises:
            PermissionDenied:

        """
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
