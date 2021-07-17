from django.db import models
from django.dispatch import receiver

import os


def delete_file_path(path):
    if os.path.isfile(path):
        os.remove(path)


@receiver(models.signals.pre_save)
def delete_old_file_after_model_update(sender, instance, **kwargs):
    if not instance.pk:
        return False

    try:
        old_files = sender.objects.get(pk=instance.pk).get_files()
    except (models.ObjectDoesNotExist, AttributeError):
        return False

    if old_files:
        new_files = instance.get_files()
        if new_files:
            for new, old in zip(new_files, old_files):
                if old != new:
                    try:
                        delete_file_path(old.path)
                    except ValueError:
                        """ To fix 'The 'instance' attribute has no file associated with it.' """
                        continue


@receiver(models.signals.pre_delete)
def delete_diles_with_deleting_instance(sender, instance, **kwargs):
    try:
        files = instance.get_files()
        if files:
            for file in files:
                try:
                    delete_file_path(file.path)
                except ValueError:
                    """ To fix 'The 'instance' attribute has no file associated with it.' """
                    continue
    except AttributeError:
        return False
