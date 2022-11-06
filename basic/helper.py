from django.db import models


def choice_to_json(choices: models.TextChoices):
    result = []
    index = 1
    for key, value in choices:
        entry = {
            'id': index,
            'name': value,
            'value': key
        }
        index += 1
        result.append(entry)
    return result
