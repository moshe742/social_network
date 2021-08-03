from django.db.models.signals import post_save
from django.dispatch import receiver

import accounts.data_enrichment
from accounts.models import User


@receiver(post_save, sender=User, dispatch_uid='post_save_enrich_user_data')
def enrich_user_data(sender, **kwargs):
    if kwargs.get('created'):
        instance = kwargs.get('instance')
        accounts.data_enrichment.enrich_geo(instance)
