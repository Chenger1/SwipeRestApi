from django.apps import AppConfig
from django.db.models.signals import post_migrate


def create_promotion_type_instances(sender, **kwargs):
    from _db.models.models import PromotionType
    _TYPES = [{'name': 'Большое объявление',
               'price': 399,
               'efficiency': 50},
              {'name': 'Поднять объявление',
               'price': 450,
               'efficiency': 75},
              {'name': 'Турбо',
               'price': 450,
               'efficiency': 100}]
    for inst in _TYPES:
        if not PromotionType.objects.filter(name=inst['name']).exists():
            PromotionType.objects.create(name=inst['name'], price=inst['price'], efficiency=inst['efficiency'])


def create_system_user(sender, **kwargs):
    from _db.models.user import User
    created, user = User.objects.get_or_create(notifications='OFF', role='SYSTEM', is_staff=True,
                                               uid=1, first_name='Администрация', last_name='Swipe',
                                               email='swipe@mail.com')


class DbConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '_db'

    def ready(self):
        post_migrate.connect(create_promotion_type_instances, sender=self)
        post_migrate.connect(create_system_user, sender=self)
