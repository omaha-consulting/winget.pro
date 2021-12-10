from uuid import uuid4

from django.contrib.auth.models import User
from django.db.models import Model, ForeignKey, CASCADE, UUIDField


class Tenant(Model):

    user = ForeignKey(User, on_delete=CASCADE)
    uuid = UUIDField(unique=True, default=uuid4, editable=False)

    def __str__(self):
        return self.user.username