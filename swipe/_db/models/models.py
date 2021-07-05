from django.db import models

from _db.models.user import User


class House(models.Model):
    status_choices = (
        ('FLATS', 'Квартиры'),
        ('OFFICES', 'Офисы'),
    )
    type_choices = (
        ('MANY', 'Многоквартирный'),
        ('ONE', 'Индивидуальный')  # TODO: уточнить
    )
    house_class_choices = (
        ('COMMON', 'Обычный'),
        ('ELITE', 'Элитный')
    )
    tech_choices = (
        ('MONO1', 'Монолитный каркас с керамзитно-блочным заполнением'),
        ('MONO2', 'Монолитно-кирпичный'),
        ('MONO3', 'Монолитно-каркасный'),
        ('PANEL', 'Панельный'),
        ('FOAM', 'Пеноблок'),
        ('AREATED', 'Газобетон'),
    )
    territory_choices = (
        ('OPEN', 'Открытая территория'),
        ('CLOSE', 'Закрытая территория')
    )
    gas_choices = (
        ('NO', 'Нет'),
        ('CENTER', 'Центрилизированный')
    )
    heating_choices = (
        ('NO', 'Нет'),
        ('CENTER', 'Центральное'),
        ('PERSONAL', 'Индивидуальное')
    )
    electricity_choices = (
        ('NO', 'Нет'),
        ('YES', 'Подключено')
    )
    sewerage_choices = (
        ('NO', 'Нет'),
        ('CENTRAL', 'Центральная'),
        ('PERSONAL', 'Индивидуальная')
    )
    water_supply_choices = (
        ('NO', 'Нет'),
        ('CENTRAL', 'Центральная'),
        ('PERSONAL', 'Индивидуальная')
    )
    communal_payments_choices = (
        ('PAYMENTS', 'Платежи')  # TODO: уточнить
    )
    completion_choices = (
        ('LAW', 'ЮСТИЦИЯ'),
        ('WILD', 'НЕ ЮСТИЦИЯ')
    )
    payment_options_choices = (
        ('MORTGAGE', 'Ипотека'),
        ('CAPITAL', 'Материнский капитал'),
        ('PAYMENT', 'Прямая оплата')
    )
    role_choices = (
        ('FLAT', 'Жилое помещение'),
        ('OFFICE', 'Офисное помещение')
    )
    sum_in_contract_choices = (
        ('FULL', 'Полная'),
        ('NOTFULL', 'Неполная')
    )

    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    image = models.ImageField(upload_to='media')
    status = models.CharField(choices=status_choices, default='FLAT', max_length=6)
    type = models.CharField(choices=type_choices, default='MANE', max_length=5)
    house_class = models.CharField(choices=house_class_choices, default='COMMON', max_length=6)
    tech = models.CharField(choices=tech_choices, max_length=10)  # TODO: Maybe we can dynamically add new tech
    territory = models.CharField(choices=territory_choices, max_length=5)
    distance_to_sea = models.IntegerField(blank=True, null=True, default=0)
    ceiling_height = models.FloatField(blank=True, null=True)
    gas = models.CharField(choices=gas_choices, default='NO', max_length=6)
    heating = models.CharField(choices=heating_choices, default='NO', max_length=8)
    electricity = models.CharField(choices=electricity_choices, default='YES', max_length=3)
    sewerage = models.CharField(choices=sewerage_choices, default='NO', max_length=8)
    water_supply = models.CharField(choices=water_supply_choices, default='NO', max_length=8)
    description = models.TextField(blank=True, null=True)
    communal_payments = models.CharField(choices=communal_payments_choices, default='PAYMENTS', max_length=8)
    completion = models.CharField(choices=completion_choices, default='LAS', max_length=4)
    payment_options = models.CharField(choices=payment_options_choices, max_length=8)
    role = models.CharField(choices=role_choices, max_length=6)
    sum_in_contract = models.CharField(choices=sum_in_contract_choices, default='FULL', max_length=7)

    # Benefits
    playground = models.BooleanField(default=False)
    car_park = models.BooleanField(default=False)
    shop = models.BooleanField(default=False)
    child_playground = models.BooleanField(default=False)
    high_speed_elevator = models.BooleanField(default=False)
    security = models.BooleanField(default=False)

    sales_department = models.ForeignKey(User, related_name='managed_houses', on_delete=models.SET_NULL, blank=True,
                                         null=True)


class Building(models.Model):
    name = models.CharField(max_length=50)
    house = models.ForeignKey(House, related_name='buildings', on_delete=models.CASCADE)


class Section(models.Model):
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, related_name='sections', on_delete=models.CASCADE)


class Floor(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, related_name='floors', on_delete=models.CASCADE)


class Standpipe(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, related_name='pipes', on_delete=models.CASCADE)


class Flat(models.Model):
    state_choices = (
        ('BLANK', 'После ремонта'),
        ('ROUGH', 'Черновая'),
        ('EURO', 'Евроремонт'),
        ('NEED', 'Требует ремонта')
    )
    foundation_doc_choices = (
        ('OWNER', 'Собственность'),
        ('RENT', 'Аренда')
    )
    type_choices = (
        ('FLAT', 'Апартаменты'),
        ('OFFICE', 'Офис'),
        ('STUDIO', 'Студия')
    )
    plan_choices = (
        ('FREE', 'Свободная планировка'),
        ('STUDIO', 'Студия'),
        ('ADJACENT', 'Смежные комнаты'),
        ('ISOLATED', 'Изолированные комнаты'),
        ('SMALL', 'Малосемейка'),
        ('ROOM', 'Гостинка')
    )
    balcony_choices = (
        ('YES', 'Да'),
        ('NO', 'Нет')
    )

    number = models.IntegerField()
    square = models.FloatField()
    kitchen_square = models.FloatField()
    price_per_metre = models.FloatField()
    price = models.FloatField()
    schema = models.ImageField(upload_to='media')
    schema_in_house = models.ImageField(upload_to='media')
    number_of_rooms = models.IntegerField()
    state = models.CharField(choices=state_choices, max_length=5)
    foundation_doc = models.CharField(choices=foundation_doc_choices, max_length=5)
    type = models.CharField(choices=type_choices, default='FLAT', max_length=6)
    plan = models.CharField(choices=plan_choices, max_length=8)
    balcony = models.CharField(choices=balcony_choices, max_length=3)

    floor = models.ForeignKey(Floor, related_name='flats', on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='flats', on_delete=models.SET_NULL, blank=True, null=True)
