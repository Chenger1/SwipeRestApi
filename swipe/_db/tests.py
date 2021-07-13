from django.test import TestCase, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.utils import IntegrityError

import tempfile

from _db.models.models import *
from _db.models.user import User


class TestHouse(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create(uid='123', email='user@mail.com')
        self.inst = House.objects.create(name='test_house', address='address', tech='MONO1',
                                         payment_options='PAYMENT', role='FLAT', sales_department=self.user)

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
        building = Building.objects.create(name='1', house=self.inst)
        self.assertIn(building, self.inst.buildings.all())

        section = Section.objects.create(name='first', building=building)
        self.assertIn(section, building.sections.all())

        floor = Floor.objects.create(name='first-floor', section=section)
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
            Building.objects.create(name='1')

    def test_section_raising_error(self):
        with self.assertRaises(IntegrityError):
            Section.objects.create(name='1')

    def test_floor_raising_error(self):
        with self.assertRaises(IntegrityError):
            Floor.objects.create(name='1')

    def test_standpipe_raising_error(self):
        with self.assertRaises(IntegrityError):
            Standpipe.objects.create(name='1')


class TestPost(TestCase):
    def setUp(self):
        self.user = User.objects.create(email='example@mail.com', uid='123')
        self.house = House.objects.create(name='test_house', address='address', tech='MONO1',
                                          payment_options='PAYMENT', role='FLAT', sales_department=self.user)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_create_post(self):
        inst = Post.objects.create(address='1', foundation_doc='OWNER',
                                   number_of_rooms=1, plan='FREE', square=12,
                                   payment_options='PAYMENT', price=12,
                                   house=self.house, user=self.user)
        self.assertIn(inst, Post.objects.all())
        self.assertEqual(inst.address, '1')

        img = SimpleUploadedFile('image.jpeg', b'file_content', content_type='image/jpeg')
        image = PostImage.objects.create(name='1', image=img, post=inst)
        self.assertIn(image, inst.images.all())

        complaint = Complaint.objects.create(post=inst, user=self.user, type='PRICE')
        self.assertIn(complaint, inst.complaints.all())

    def test_creating_promotion_type(self):
        inst = PromotionType.objects.create(name='1', price=1, efficiency=10)
        self.assertEqual(inst.price, 1)

    def test_create_promotion(self):
        post = Post.objects.create(address='1', foundation_doc='OWNER',
                                   number_of_rooms=1, plan='FREE', square=12,
                                   payment_options='PAYMENT', price=12,
                                   house=self.house, user=self.user)
        promotion_type = PromotionType.objects.create(name='first', price=1, efficiency=10)
        promo = Promotion.objects.create(post=post, type=promotion_type,
                                         phrase='GIFT', color='PINK', price=10)
        self.assertIn(promo, post.promotions.all())
