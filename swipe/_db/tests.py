from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

from django.conf import settings

import tempfile
import os
import datetime

from _db.models.models import *
from _db.models.user import User


class TestHouse(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(email='user@mail.com', phone_number='778787')
        self.inst = House.objects.create(name='test_house', address='address', tech='MONO1',
                                         payment_options='PAYMENT', role='FLAT', sales_department=self.user,
                                         city='Odessa')

    def test_create_house(self):
        inst = House.objects.create(name='house', address='address', tech='MONO1',
                                    payment_options='PAYMENT', role='FLAT', sales_department=self.user)
        self.assertEqual(inst.name, 'house')

    def test_edit_house(self):
        inst = House.objects.get(name='test_house')
        inst.tech = 'MONO2'
        inst.save()
        self.assertEqual(inst.tech, 'MONO2')

    def test_delete_house(self):
        House.objects.get(name='test_house').delete()
        counter = House.objects.all().count()
        self.assertEqual(counter, 0)

    def test_create_news_item(self):
        item = NewsItem.objects.create(title='News', house=self.inst)
        self.assertIn(item, self.inst.news.all())
        self.assertEqual(item.title, 'News')

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_document(self):
        file = SimpleUploadedFile('doc.docx', b'file_content', content_type='application/msword')
        doc = Document.objects.create(name='doc', house=self.inst,
                                      file=file)
        self.assertIn(doc, self.inst.documents.all())
        self.assertEqual(doc.name, 'doc')
        self.assertIn('.docx', file.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_building_section_floor_standpipe_flat(self):
        building = Building.objects.create(number=1, house=self.inst)
        self.assertIn(building, self.inst.buildings.all())

        section = Section.objects.create(number=1, building=building)
        self.assertIn(section, building.sections.all())

        floor = Floor.objects.create(number=1, section=section)
        self.assertIn(floor, section.floors.all())

        standpipe = Standpipe.objects.create(name='1', section=section)
        self.assertIn(standpipe, section.pipes.all())

        img = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        flat = Flat.objects.create(number=1, square=1, kitchen_square=1,
                                   price_per_metre=1, price=1,
                                   schema=img,
                                   schema_in_house=img,
                                   number_of_rooms=1, state='BLANK',
                                   foundation_doc='OWNER', plan='FREE', balcony='YES',
                                   floor=floor)
        self.assertIn(flat, floor.flats.all())

    def test_building_raising_error(self):
        with self.assertRaises(IntegrityError):
            Building.objects.create(number=1)

    def test_section_raising_error(self):
        with self.assertRaises(IntegrityError):
            Section.objects.create(number=1)

    def test_floor_raising_error(self):
        with self.assertRaises(IntegrityError):
            Floor.objects.create(number=1)

    def test_standpipe_raising_error(self):
        with self.assertRaises(IntegrityError):
            Standpipe.objects.create(name=1)


class TestPost(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='example@mail.com', phone_number='23123')
        self.house = House.objects.create(name='test_house', address='address', tech='MONO1',
                                          payment_options='PAYMENT', role='FLAT', sales_department=self.user)

    def init_house_structure(self):
        self.inst = House.objects.create(name='test_house', address='address', tech='MONO1',
                                         payment_options='PAYMENT', role='FLAT', sales_department=self.user,
                                         city='Odessa')
        house = House.objects.first()

        building = Building.objects.create(number=1, house=house)
        section = Section.objects.create(number=1, building=building)
        floor = Floor.objects.create(number=1, section=section)
        file1 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        file2 = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        flat1 = Flat.objects.create(number=1, square=100, kitchen_square=1, price_per_metre=100, price=100,
                                    number_of_rooms=2, state='BLANK', foundation_doc='OWNER', plan='FREE',
                                    balcony='YES', floor=floor, schema=file1)
        flat2 = Flat.objects.create(number=1, square=200, kitchen_square=1, price_per_metre=200, price=200,
                                    number_of_rooms=2, state='EURO', foundation_doc='OWNER', plan='FREE',
                                    balcony='YES', floor=floor, schema=file2)

        return house, building, section, floor, flat1, flat2

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_post(self):
        house, *_, flat = self.init_house_structure()
        inst = Post.objects.create(payment_options='PAYMENT', price=12,
                                   flat=flat, user=self.user, house=house, number=1)
        self.assertIn(inst, Post.objects.all())
        self.assertEqual(inst.price, 12)

        img = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        image = PostImage.objects.create(image=img, post=inst)
        self.assertIn(image, inst.images.all())

        complaint = Complaint.objects.create(post=inst, user=self.user, type='PRICE')
        self.assertIn(complaint, inst.complaints.all())

    def test_creating_promotion_type(self):
        inst = PromotionType.objects.create(name='1', price=1, efficiency=10)
        self.assertEqual(inst.price, 1)

    def test_create_promotion(self):
        house, *_, flat = self.init_house_structure()
        post = Post.objects.create(payment_options='PAYMENT', price=12,
                                   flat=flat, user=self.user, house=house, number=1)
        promotion_type = PromotionType.objects.create(name='first', price=1, efficiency=10)
        promo = Promotion.objects.create(post=post, type=promotion_type,
                                         phrase='GIFT', color='PINK', price=10, end_date=datetime.date.today())
        self.assertEqual(promo, Post.promotion.get_queryset().first())

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_auto_files_deleting(self):
        """ Ensure that after we delete instance or update file - old version will be deleted """
        house, *_, flat = self.init_house_structure()
        inst = Post.objects.create(payment_options='PAYMENT', price=12,
                                   flat=flat, user=self.user, house=house, number=1)
        MEDIA_ROOT = os.path.join(settings.MEDIA_ROOT, os.path.join('media', 'posts'))

        img = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        img2 = SimpleUploadedFile('new.jpeg', b'file_content', content_type='image/jpeg')

        image = PostImage.objects.create(image=img, post=inst)
        first_image = os.path.split(image.image.path)[-1]
        self.assertIn(first_image, os.listdir(MEDIA_ROOT))

        image.image = img2
        image.save()
        
        new_image = os.path.split(image.image.path)[-1]
        self.assertIn(new_image, os.listdir(MEDIA_ROOT))
        self.assertNotIn(first_image, os.listdir(MEDIA_ROOT))

    def test_post_migrate_signal(self):
        self.assertEqual(PromotionType.objects.count(), 3)
