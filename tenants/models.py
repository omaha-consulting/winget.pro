from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, UUIDField, ManyToManyField
from uuid import uuid4

class Tenant(Model):

    users = ManyToManyField(User)
    uuid = UUIDField(unique=True, default=uuid4, editable=False)

    def __str__(self):
        # We have to check that `id` is set to avoid a `RecursionError`.
        if self.id:
            try:
                return self.users.earliest('date_joined').username
            except ObjectDoesNotExist:
                pass
        return str(self.uuid)