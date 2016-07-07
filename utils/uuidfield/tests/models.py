import uuid
from django.db import models
from uuidfield import UUIDField


# primary_key=True一定要加上，否则django自动加自增字段
class AutoUUIDField(models.Model):
    uuid = UUIDField(auto=True)


class ManualUUIDField(models.Model):
    uuid = UUIDField(auto=False)


class NamespaceUUIDField(models.Model):
    uuid = UUIDField(auto=True, namespace=uuid.NAMESPACE_URL, version=5)


class BrokenNamespaceUUIDField(models.Model):
    uuid = UUIDField(auto=True, namespace='lala', version=5)
