import os
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png',
                        '.xlxs', '.xls', '.pptx']
    if not ext.lower() in valid_extensions:
        raise ValidationError('Unsupported file extension.')
