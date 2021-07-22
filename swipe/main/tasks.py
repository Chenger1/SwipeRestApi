from celery.schedules import crontab

from swipe.celery import app

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

import datetime

from _db.models.models import Promotion, Post
from _db.models.user import UserFilter, Message


User = get_user_model()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Init task to check subscription date status
    sender.add_periodic_task(
        crontab(hour='1', minute=0),
        check_subscription
    )

    sender.add_periodic_task(
        crontab(hour='1', minute=0),
        check_promotion
    )


@app.task
def check_subscription():
    users_with_subscription = User.objects.filter(subscribed=True,
                                                  end_date=datetime.date.today())
    system_user = User.objects.filter(role='SYSTEM').first()
    for user in users_with_subscription:
        user.subscribed = False
        Message.objects.create(sender=system_user, receiver=user,
                               text='Your subscription has been expired')
        user.save()


@app.task
def check_promotion():
    promotions = Promotion.objects.filter(end_date=datetime.date.today())
    system_user = User.objects.filter(role='SYSTEM').first()
    for promo in promotions:
        post = promo.post
        user = post.user
        weight = promo.type.efficiency
        promo.delete()
        post.weight -= weight
        post.save()
        Message.objects.create(sender=system_user, receiver=user,
                               text='Your promotion plan has been expired')


@app.task
def check_filter_matching(post_pk, host):
    """
    If new post matches any user`s filter - this users will get notification about new post
    :param post_pk:
    :param host: site domains, like '127.0.0.1'
    """
    post = Post.objects.get(pk=post_pk)
    filters = UserFilter.objects.filter(
        (Q(market=post.living_type) |
         Q(payment_cond=post.payment_options) |
         Q(status=post.house.status) |
         Q(city=post.house.city) |
         Q(address=post.house.address) |
         Q(number_of_rooms=post.flat.number_of_rooms) |
         Q(state=post.flat.state) |
         Q(max_price=post.price) |
         Q(min_price=post.price) |
         Q(max_square=post.flat.square) |
         Q(min_square=post.flat.square)
         )
    )
    if filters.exists():
        system_user = User.objects.filter(role='SYSTEM').first()
        for filterr in filters:
            user = filterr.user
            url = f'http://{host}{reverse("main:posts-detail", args=[post.pk])}'
            text = f'Новое объявление подходит под один из ваших фильтров - {url}'
            Message.objects.create(sender=system_user, receiver=user,
                                   text=text)

