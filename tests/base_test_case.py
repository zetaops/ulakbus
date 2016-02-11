# -*-  coding: utf-8 -*-
from time import sleep
from pyoko.exceptions import MultipleObjectsReturned
from pyoko.model import super_context
from ulakbus.models import User, AbstractRole, Role, Permission
from zengine.lib.test_utils import BaseTestCase as ZengineBaseTestCase, user_pass
import sys

sys.TEST_MODELS_RESET = False


class BaseTestCase(ZengineBaseTestCase):
    """
    Bu sınıf ``ZengineBaseTestCase`` extend edilerek hazırlanmıştır.

    """

    @staticmethod
    def cleanup():
        """
        Bu metot ile modellerin içeriği temizlenir.

        """

        if not sys.TEST_MODELS_RESET:
            for mdl in [AbstractRole, User, Role]:
                mdl(super_context).objects._clear_bucket()
            sleep(2)
            sys.TEST_MODELS_RESET = True

    @classmethod
    def create_user(cls):
        """
        Bu metot ile yeni kullanıcı yaratılır ya da varolan kullanıcı getirilir.

        """

        # FIXME: To prevent existence of test_user in production,
        # this should be depend on an env. flag
        cls.cleanup()
        # Tanımlı parametrelere sahip soyut rol varsa rolü döndürür, yoksa soyut rol yaratır.
        abs_role, new = AbstractRole(super_context).objects.get_or_create(id=1, name='W.C. Hero')
        cls.client.user, new = User(super_context).objects.get_or_create({"password": user_pass},
                                                                         username='test_user')
        cls.client.user.superuser = True
        cls.client.user.save()

        if new:
            # Role modelinden role nesnesi yaratır.
            role = Role(super_context, user=cls.client.user, abstract_role=abs_role).save()
            # sleep(2)
            # role nesnesine, yetkiler eklenir.
            for perm in Permission(super_context).objects.raw(
                    "code:crud* OR code:login* OR code:logout* OR code:User* OR code:Personel* OR code:yeni*"):
                role.Permissions(permission=perm)
            role.save()
            sleep(1)

            # Kullanıcı güncellenir.
            cls.client.user = User(super_context).objects.get(cls.client.user.key)
