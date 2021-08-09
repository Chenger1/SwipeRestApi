from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

from _db.models.user import User

from _db.models.choices import *
from _db.models.validators import validate_file_extension


class House(models.Model):
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    long = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    lat = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    image = models.ImageField(upload_to='media/houses', blank=True, null=True)
    status = models.CharField(choices=status_choices, default='FLAT', max_length=7)
    type = models.CharField(choices=type_choices, default='MANE', max_length=9)
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

    def get_files(self):
        return [self.image]


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
    file = models.FileField(upload_to='media/documents', validators=[validate_file_extension])
    house = models.ForeignKey(House, related_name='documents', on_delete=models.CASCADE)

    @property
    def user(self):
        return self.house.user


class Building(models.Model):
    number = models.IntegerField()
    house = models.ForeignKey(House, related_name='buildings', on_delete=models.CASCADE)

    @classmethod
    def get_last(cls, house_pk: int):
        objects = cls.objects.fitler(house__pk=house_pk)
        if objects:
            last = objects.last().number
            return last + 1
        return 1

    @property
    def user(self):
        return self.house.user


class Section(models.Model):
    number = models.IntegerField()
    building = models.ForeignKey(Building, related_name='sections', on_delete=models.CASCADE)

    @classmethod
    def get_last(cls, building_pk: int):
        objects = cls.objects.fitler(building__pk=building_pk)
        if objects:
            last = objects.last().number
            return last + 1
        return 1

    @property
    def user(self):
        return self.building.user


class Floor(models.Model):
    number = models.IntegerField()
    section = models.ForeignKey(Section, related_name='floors', on_delete=models.CASCADE)

    @classmethod
    def get_last(cls, section_pk: int):
        objects = cls.objects.fitler(section__pk=section_pk)
        if objects:
            last = objects.last().number
            return last + 1
        return 1

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
    heating = models.CharField(choices=heating_choices, default='NO', max_length=8)

    floor = models.ForeignKey(Floor, related_name='flats', on_delete=models.CASCADE)
    client = models.ForeignKey(User, related_name='flats', on_delete=models.SET_NULL, blank=True, null=True)
    booked = models.BooleanField(default=False)  # If client booked flat - no one else can do it. BUT he does`t own it
    owned = models.BooleanField(default=False)  # If owned is True = client is displaying in house list.

    @property
    def booking_status(self):
        return 'Booked' if self.booked else 'Free'

    @property
    def user(self):
        return self.floor.user

    def get_files(self):
        return [self.schema, self.schema_in_house]


class RequestToChest(models.Model):
    house = models.ForeignKey(House, related_name='requests', on_delete=models.CASCADE)
    flat = models.ForeignKey(Flat, related_name='requests', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    @property
    def user(self):
        return self.house.user


class Post(models.Model):
    LIMIT = 5  # Max posts for unsubscribed users

    number = models.IntegerField(unique=True, blank=True)
    living_type = models.CharField(choices=type_choices, default='MANY', max_length=9, blank=True, null=True)
    payment_options = models.CharField(choices=payment_options_choices, max_length=8)
    agent_coms = models.CharField(choices=agent_coms_choices, max_length=7, blank=True, null=True)
    communications = models.CharField(choices=communication_choices, max_length=7,
                                      default='BOTH')
    description = models.TextField(blank=True, null=True)
    price = models.IntegerField()
    flat = models.ForeignKey(Flat, related_name='posts', on_delete=models.CASCADE)
    house = models.ForeignKey(House, related_name='posts', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='posts', on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    views = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    rejected = models.BooleanField(default=False)
    reject_message = models.CharField(choices=reject_message_choices, max_length=5, blank=True, null=True)
    main_image = models.ImageField(upload_to='media/posts/')

    likers = models.ManyToManyField(User, related_name='liked')
    dislikers = models.ManyToManyField(User, related_name='disliked')
    in_favorites = models.ManyToManyField(User, related_name='favorites')

    weight = models.IntegerField(default=0)  # User for order post

    def get_files(self):
        return [self.main_image]

    @classmethod
    def set_limit(cls, value):
        cls.LIMIT = value

    @classmethod
    def get_next_number(cls):
        last = cls.objects.last()
        if last:
            return last.number + 1
        return 1


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='media/posts')

    @property
    def user(self):
        return self.post.user

    def get_files(self):
        return [self.image]


class Complaint(models.Model):
    post = models.ForeignKey(Post, related_name='complaints', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name='complaints', on_delete=models.CASCADE)
    type = models.CharField(choices=reject_message_choices, max_length=5)
    description = models.TextField(blank=True, null=True)
    rejected = models.BooleanField(default=False)
    # Administrator decides if complaint is fair


class PromotionType(models.Model):
    name = models.CharField(max_length=30)
    price = models.IntegerField()
    efficiency = models.IntegerField(default=1,
                                     validators=[MaxValueValidator(100),
                                                 MinValueValidator(1)])


class Promotion(models.Model):
    # One Post can only have one promotion
    post = models.OneToOneField(Post, related_name='promotion', on_delete=models.CASCADE)
    phrase = models.CharField(choices=phrase_choices, max_length=10, blank=True, null=True)
    color = models.CharField(choices=color_choices, max_length=10, blank=True, null=True)
    price = models.IntegerField(blank=True)  # Price calculates automatically
    paid = models.BooleanField(default=True)
    type = models.ForeignKey(PromotionType, related_name='promotions', on_delete=models.SET_NULL,
                             blank=True, null=True)
    end_date = models.DateField(blank=True)
