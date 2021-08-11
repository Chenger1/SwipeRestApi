from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from _db.models.manager import UserManager
from _db.models.validators import validate_file_extension


class CustomAbstractUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(_('first name'), max_length=150, blank=True,
                                  null=True)
    last_name = models.CharField(_('last_name'), max_length=150, blank=True,
                                 null=True)
    email = models.CharField(
        _('email'),
        max_length=150,
        unique=True,
        help_text=_('150 characters max. Available symbols: aA-wW, [0-9], @ . _'),
        blank=True, null=True
    )
    phone_number = models.CharField(max_length=30, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'phone_number'

    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        return None


class User(CustomAbstractUser):
    notification_choices = (
        ('ME', 'Мне'),
        ('MEANDAGENT', 'Мне и агенту'),
        ('AGENT', 'Агенту'),
        ('OFF', 'Отключить')
    )
    role_choices = (
        ('USER', 'Клиент'),
        ('AGENT', 'Агент'),
        ('NOTARY', 'Нотариус'),
        ('DEPART', 'Отдел продаж'),
        ('SYSTEM', 'Администрация Swipe')
    )

    notifications = models.CharField(choices=notification_choices,
                                     max_length=10, default='ME')
    subscribed = models.BooleanField(default=False)
    end_date = models.DateField(blank=True, null=True)
    role = models.CharField(choices=role_choices, max_length=8, default='USER')
    photo = models.ImageField(upload_to='media/users/', blank=True, null=True)
    ban = models.BooleanField(default=False)

    def get_files(self):
        return [self.photo]


class Contact(models.Model):
    user = models.ForeignKey(User, related_name='contacts', on_delete=models.CASCADE)
    contact = models.ForeignKey(User, related_name='users', on_delete=models.CASCADE)
    ban = models.BooleanField(default=False)


class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent', on_delete=models.SET_NULL,
                               blank=True, null=True)
    receiver = models.ForeignKey(User, related_name='received', on_delete=models.SET_NULL,
                                 blank=True, null=True)
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)


class Attachment(models.Model):
    message = models.ForeignKey(Message, related_name='attach', on_delete=models.CASCADE)
    file = models.FileField(upload_to='media/', validators=[validate_file_extension])

    def get_files(self):
        return [self.file]


class UserFilter(models.Model):
    market_choices = (
        ('NOVOSTROY', 'Новострой'),
        ('SECONDARY', 'Вторичный рынок'),
        ('COTTAGES', 'Коттеджи'),
        ('ALL', 'Все'),
    )
    number_of_rooms_choices = (
        (1, '1 комната'),
        (2, '2 комнаты'),
        (3, '3 комнаты'),
        (4, '4 комнаты'),
        (5, 'Больше 4-х комнат')
    )
    status_choices = (
        ('FLATS', 'Квартиры'),
        ('OFFICES', 'Офисы')
    )
    payment_conditions_choices = (
        ('MORTGAGE', 'Ипотека'),
        ('CAPITAL', 'Материнский капитал'),
        ('PAYMENT', 'Прямая оплата')
    )
    state_choices = (
        ('ROUGH', 'Черновая'),
        ('READY', 'В жилом состоянии'),
        ('RENOVATION', 'Требует ремонта')
    )
    LIMIT = 3  # Max filters for unsubscribed users

    name = models.CharField(max_length=100, blank=True, null=True)
    user = models.ForeignKey(User, related_name='filters', on_delete=models.CASCADE)
    market = models.CharField(choices=market_choices, default='ALL', max_length=9, blank=True, null=True)
    type = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(choices=status_choices, default='FLATS', max_length=7, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    #  city stores as regular string because we get all locations from all houses
    address = models.CharField(max_length=100, blank=True, null=True)
    number_of_rooms = models.IntegerField(choices=number_of_rooms_choices, default=1,
                                          blank=True, null=True)
    min_price = models.IntegerField(blank=True, null=True)
    max_price = models.IntegerField(blank=True, null=True)
    min_square = models.FloatField(blank=True, null=True)
    max_square = models.FloatField(blank=True, null=True)
    payment_cond = models.CharField(choices=payment_conditions_choices, max_length=10, blank=True, null=True)
    state = models.CharField(choices=state_choices, max_length=10, blank=True, null=True)

    @classmethod
    def set_limit(cls, value):
        cls.LIMIT = value


class AdminToken(models.Model):
    name = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
