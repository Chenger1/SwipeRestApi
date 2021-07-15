from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from _db.models.user import User

from _db.models.choices import *


class House(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    long = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    image = models.ImageField(upload_to='media/houses', blank=True, null=True)
    status = models.CharField(choices=status_choices, default='FLAT', max_length=7)
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

    sales_department = models.ForeignKey(User, related_name='managed_houses', on_delete=models.CASCADE,
                                         blank=True)

    @property
    def user(self):
        return self.sales_department


class NewsItem(models.Model):
    title = models.CharField(max_length=100)
    text = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    house = models.ForeignKey(House, related_name='news', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.house.user


class Document(models.Model):
    name = models.CharField(max_length=100)
    file = models.FileField(upload_to='media/documents')
    house = models.ForeignKey(House, related_name='documents', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.house.user


class Building(models.Model):
    name = models.CharField(max_length=50)
    house = models.ForeignKey(House, related_name='buildings', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.house.user


class Section(models.Model):
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, related_name='sections', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.building.user


class Floor(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, related_name='floors', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.section.user


class Standpipe(models.Model):
    name = models.CharField(max_length=50)
    section = models.ForeignKey(Section, related_name='pipes', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.section.user


class Flat(models.Model):
    number = models.IntegerField()
    square = models.FloatField()
    kitchen_square = models.FloatField()
    price_per_metre = models.FloatField()
    price = models.FloatField()
    schema = models.ImageField(upload_to='media/flats/schema')
    schema_in_house = models.ImageField(upload_to='media/flats/schema_in_house', blank=True, null=True)
    number_of_rooms = models.IntegerField()
    state = models.CharField(choices=state_choices, max_length=5)
    foundation_doc = models.CharField(choices=foundation_doc_choices, max_length=5)
    type = models.CharField(choices=flat_type_choices, default='FLAT', max_length=6)
    plan = models.CharField(choices=plan_choices, max_length=8)
    balcony = models.CharField(choices=balcony_choices, max_length=3)

    floor = models.ForeignKey(Floor, related_name='flats', on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='flats', on_delete=models.SET_NULL, blank=True, null=True)
    booked = models.BooleanField(default=False)

    @property
    def booking_status(self):
        return 'Booked' if self.booked else 'Free'

    @property
    def user(self):
        return self.floor.user


class RequestToChest(models.Model):
    house = models.ForeignKey(House, related_name='requests', on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, related_name='requests', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)


class Post(models.Model):
    address = models.CharField(max_length=100)
    foundation_doc = models.CharField(choices=foundation_doc_choices, max_length=5, blank=True, null=True)
    type = models.CharField(choices=type_choices, default='FLAT', max_length=6, blank=True, null=True)
    number_of_rooms = models.IntegerField()
    plan = models.CharField(choices=plan_choices, max_length=8)
    state = models.CharField(choices=state_choices, max_length=5, blank=True, null=True)
    square = models.FloatField()
    kitchen_square = models.FloatField(blank=True, null=True)
    balcony = models.CharField(choices=balcony_choices, max_length=3, default='NO')
    heating = models.CharField(choices=heating_choices, default='NO', max_length=8)
    payment_options = models.CharField(choices=payment_options_choices, max_length=8)
    agent_coms = models.CharField(choices=agent_coms_choices, max_length=7, blank=True, null=True)
    communications = models.CharField(choices=communication_choices, max_length=7,
                                      default='BOTH')
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    house = models.ForeignKey(House, related_name='posts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    published = models.BooleanField(default=False)
    rejected = models.BooleanField(default=False)
    reject_message = models.CharField(choices=reject_message_choices, max_length=5, blank=True, null=True)


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='media/posts')


class Complaint(models.Model):
    post = models.ForeignKey(Post, related_name='complaints', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='complaints', on_delete=models.CASCADE)
    type = models.CharField(choices=reject_message_choices, max_length=5)


class PromotionType(models.Model):
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    efficiency = models.IntegerField(default=1,
                                     validators=[MaxValueValidator(100),
                                                 MinValueValidator(1)])


class Promotion(models.Model):
    post = models.ForeignKey(Post, related_name='promotions', on_delete=models.CASCADE)
    phrase = models.CharField(choices=phrase_choices, max_length=10)
    color = models.CharField(choices=color_choices, max_length=10)
    price = models.IntegerField()
    paid = models.BooleanField(default=True)
    type = models.ForeignKey(PromotionType, related_name='promotions', on_delete=models.SET_NULL,
                             blank=True, null=True)
