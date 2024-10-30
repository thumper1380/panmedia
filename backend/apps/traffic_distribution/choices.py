from django.db import models
from django.utils.translation import gettext_lazy as _

class RuleChoices(models.TextChoices):
        UPPERCASE_LETTERS = 'UPPERCASE_LETTERS', _('Uppercase Letters')
        LOWERCASE_LETTERS = 'LOWERCASE_LETTERS', _('Lowercase Letters')
        NUMBERS = 'NUMBERS', _('Numbers')
        SPECIAL_CHARACTERS = 'SPECIAL_CHARACTERS', _('Special Characters')