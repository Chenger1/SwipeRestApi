from celery.schedules import crontab

from swipe.celery import app

from django.contrib.auth import get_user_model

import datetime

from _db.models.models import Promotion


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
    for user in users_with_subscription:
        user.subscribed = False
        user.save()


@app.task
def check_promotion():
    promotions = Promotion.objects.filter(end_date=datetime.date.today())
    for promo in promotions:
        post = promo.post
        weight = promo.type.efficiency
        promo.delete()
        post.weight -= weight
        post.save()
