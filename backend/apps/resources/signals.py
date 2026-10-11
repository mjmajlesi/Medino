"""Remove unreferenced uploaded files after Resource deletions commit."""

import logging

from django.db import transaction
from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Resource


logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Resource)
def delete_resource_file_after_commit(sender, instance, using, **kwargs):
    if not instance.file:
        return

    file_name = instance.file.name
    storage = instance.file.storage
    resource_id = instance.pk

    def cleanup():
        try:
            # A second Resource may intentionally reference the same stored file.
            if Resource.objects.using(using).filter(file=file_name).exists():
                return
            storage.delete(file_name)
        except FileNotFoundError:
            pass
        except Exception:
            # The database commit has succeeded; keep the HTTP result truthful and
            # log the orphan so operators can retry storage cleanup separately.
            logger.exception("File cleanup failed after deleting Resource %s.", resource_id)

    transaction.on_commit(cleanup, using=using)
