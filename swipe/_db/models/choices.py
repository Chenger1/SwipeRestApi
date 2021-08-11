from django.utils.translation import gettext_lazy as _


status_choices = (
    ('FLATS', _('Квартиры')),
    ('OFFICES', _('Офисы')),
)
type_choices = (
    ('MANY', _('Многоквартирный')),
    ('ONE', _('Частный')),
    ('NOVOSTROY', _('Новострой')),
    ('SECONDARY', _('Вторичный рынок')),
    ('COTTAGES', _('Коттеджи')),
)
house_class_choices = (
    ('COMMON', _('Обычный')),
    ('ELITE', _('Элитный'))
)
tech_choices = (
    ('MONO1', _('Монолитный каркас с керамзитно-блочным заполнением')),
    ('MONO2', _('Монолитно-кирпичный')),
    ('MONO3', _('Монолитно-каркасный')),
    ('PANEL', _('Панельный')),
    ('FOAM', _('Пеноблок')),
    ('AREATED', _('Газобетон')),
)
territory_choices = (
    ('OPEN', _('Открытая территория')),
    ('CLOSE', _('Закрытая территория'))
)
gas_choices = (
    ('NO', _('Нет')),
    ('CENTER', _('Центрилизированный'))
)
heating_choices = (
    ('NO', _('Нет')),
    ('CENTER', _('Центральное')),
    ('PERSONAL', _('Индивидуальное'))
)
electricity_choices = (
    ('NO', _('Нет')),
    ('YES', _('Подключено'))
)
sewerage_choices = (
    ('NO', _('Нет')),
    ('CENTRAL', _('Центральная')),
    ('PERSONAL', _('Индивидуальная'))
)
water_supply_choices = (
    ('NO', _('Нет')),
    ('CENTRAL', _('Центральная')),
    ('PERSONAL', _('Индивидуальная'))
)
communal_payments_choices = (
    ('PAYMENTS', _('Платежи')),
)
completion_choices = (
    ('LAW', _('ЮСТИЦИЯ')),
    ('WILD', _('НЕ ЮСТИЦИЯ'))
)
payment_options_choices = (
    ('MORTGAGE', _('Ипотека')),
    ('CAPITAL', _('Материнский капитал')),
    ('PAYMENT', _('Прямая оплата'))
)
role_choices = (
    ('FLAT', _('Жилое помещение')),
    ('OFFICE', _('Офисное помещение'))
)
sum_in_contract_choices = (
    ('FULL', _('Полная')),
    ('NOTFULL', _('Неполная'))
)

state_choices = (
        ('BLANK', _('После ремонта')),
        ('ROUGH', _('Черновая')),
        ('EURO', _('Евроремонт')),
        ('NEED', _('Требует ремонта'))
    )
foundation_doc_choices = (
        ('OWNER', _('Собственность')),
        ('RENT', _('Аренда'))
    )
flat_type_choices = (
        ('FLAT', _('Апартаменты')),
        ('OFFICE', _('Офис')),
        ('STUDIO', _('Студия'))
    )
plan_choices = (
        ('FREE', _('Свободная планировка')),
        ('STUDIO', _('Студия')),
        ('ADJACENT', _('Смежные комнаты')),
        ('ISOLATED', _('Изолированные комнаты')),
        ('SMALL', _('Малосемейка')),
        ('ROOM', _('Гостинка'))
    )
balcony_choices = (
        ('YES', _('Да')),
        ('NO', _('Нет'))
    )

#  Post only
agent_coms_choices = (
    ('SMALL', _('10 000 грн.')),
    ('AVERAGE', _('50 000 грн.')),
    ('BIG', _('100 000 грн.'))
)

communication_choices = (
    ('CALL', _('Звонок')),
    ('MESSAGE', _('Сообщение')),
    ('BOTH', _('Звонок + сообщение'))
)

reject_message_choices = (
    ('PRICE', _('Некорректная цена')),
    ('PHOTO', _('Некорректное фото')),
    ('DESC', _('Некорректное описание')),
    ('ANY', _('Другое...'))
)

# Promotion only
phrase_choices = (
    ('GIFT', _('Подарок при покупке')),
    ('TRADE', _('Возможен торг')),
    ('SEA', _('Квартира у моря')),
    ('SLEEP', _('В спальном районе')),
    ('PRICE', _('Вам повезло с ценой')),
    ('BIG_FAMILY', _('Для большой семьи')),
    ('FAMILY', _('Семейное гнездышко')),
    ('CAR_PARK', _('Отдельная парковка'))
)

color_choices = (
    ('PINK', _('Розовый')),
    ('GREEN', _('Зеленый'))
)
