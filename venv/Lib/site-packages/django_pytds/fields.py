"""This module provides SQL Server specific fields for Django models."""
from django.db.models import AutoField, ForeignKey, BigIntegerField
from django.forms import ValidationError
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'BigAutoField',
    'BigForeignKey',
    'BigIntegerField',
)

class BigAutoField(AutoField):
    """A bigint IDENTITY field"""
    def get_internal_type(self):
        return "BigAutoField"

    def to_python(self, value):
        if value is None:
            return value
        try:
            return long(value)
        except (TypeError, ValueError):
            raise ValidationError(
                _("This value must be a long."))

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if value is None:
            return None
        return long(value)

class BigForeignKey(ForeignKey):
    """A ForeignKey field that points to a BigAutoField or BigIntegerField"""
    def db_type(self, connection=None):
        try:
            return BigIntegerField().db_type(connection=connection)
        except AttributeError:
            return BigIntegerField().db_type()
