from django.core.exceptions import ValidationError
from datetime import datetime


def validate_year(value):
    if value > datetime.now().year:
        raise ValidationError('Год выхода не может быть больше текущего!')
