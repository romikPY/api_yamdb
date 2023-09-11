from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.exceptions import ValidationError


username_validator = UnicodeUsernameValidator()


def me_username_validator(username):
    if username == 'me':
        raise ValidationError('Недопустимое значение!')
