import re

from django.core.exceptions import ValidationError

from foodgram_backend.constants import FORBIDDEN_USERNAMES, USERNAME_REGEX


def validate_username(value):
    """Валидация username: запрет 'me' + проверка символов."""
    if value in FORBIDDEN_USERNAMES:
        raise ValidationError(f'Имя "{value}" запрещено.')
    if not re.match(USERNAME_REGEX, value):
        raise ValidationError('Недопустимые символы в имени пользователя.')
    return value
