from models import *
from pyoko.exceptions import ObjectDoesNotExist
from pyoko.model import super_context
import traceback

abs_role, new = AbstractRole(super_context).objects.get_or_create(id=1, name='W.C. Hero')
if new:
    print("AbstractRole is new")
user, new = User(super_context).objects.get_or_create({"password": '123'}, username='test_user')
if new:
    print("User is new")

try:
    r = Role(super_context).objects.get()
    for p in r.Permissions:
        print(p.permission.key)
    r.prnt()
    print("Role is already exists, will be cleaned!..")
    try:
        p.permission.role_set[0].role.prnt()
    except:
        print(traceback.format_exc())
        # raise
    for mdl in [AbstractRole, User, Role]:
        mdl(super_context).objects._clear_bucket()
except ObjectDoesNotExist:
    print("Role is New")
    r = Role(super_context, user=user, abstract_role=abs_role).save()
    perms = Permission(super_context).objects.raw("code:crud* OR code:login* OR code:User*")
    for perm in perms:
        r.Permissions(permission=perm)
    # r.prnt()
    r.save()
    Permission.objects.get(perm.key).prnt()




