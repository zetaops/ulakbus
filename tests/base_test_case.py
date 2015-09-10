# -*-  coding: utf-8 -*-
from time import sleep
from ulakbus.models import User, AbstractRole, Role, Permission
from zengine.lib.test_utils import BaseTestCase as ZengineBaseTestCase, user_pass

class BaseTestCase(ZengineBaseTestCase):

    @classmethod
    def create_user(self):
        abs_role, new = AbstractRole.objects.get_or_create(id=1, name='W.C. Hero')
        self.client.user, new = User.objects.get_or_create({"password": user_pass},
                                                           username='test_user')
        if new:
            role = Role(user=self.client.user, abstract_role=abs_role).save()
            for perm in Permission.objects.raw("code:crud* OR code:login* OR code:User*"):
                role.Permissions(permission=perm)
            role.save()
            sleep(1)
            # pyoko dose not update the user instance
            self.client.user = User.objects.get(self.client.user.key)

