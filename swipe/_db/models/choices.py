status_choices = (
    ('FLATS', 'Квартиры'),
    ('OFFICES', 'Офисы'),
)
type_choices = (
    ('MANY', 'Многоквартирный'),
    ('ONE', 'Частный'),
    ('NOVOSTROY', 'Новострой'),
    ('SECONDARY', 'Вторичный рынок'),
    ('COTTAGES', 'Коттеджи'),
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
    ('PAYMENTS', 'Платежи'),
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
flat_type_choices = (
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

#  Post only
agent_coms_choices = (
    ('SMALL', '10 000 грн.'),
    ('AVERAGE', '50 000 грн.'),
    ('BIG', '100 000 грн.')
)

communication_choices = (
    ('CALL', 'Звонок'),
    ('MESSAGE', 'Сообщение'),
    ('BOTH', 'Звонок + сообщение')
)

reject_message_choices = (
    ('PRICE', 'Некорректная цена'),
    ('PHOTO', 'Некорректное фото'),
    ('DESC', 'Некорректное описание'),
)

# Promotion only
phrase_choices = (
    ('GIFT', 'Подарок при покупке'),
    ('TRADE', 'Возможен торг'),
    ('SEA', 'Квартира у моря'),
    ('SLEEP', 'В спальном районе'),
    ('PRICE', 'Вам повезло с ценой'),
    ('BIG_FAMILY', 'Для большой семьи'),
    ('FAMILY', 'Семейное гнездышко'),
    ('CAR_PARK', 'Отдельная парковка')
)

color_choices = (
    ('PINK', 'Розовый'),
    ('GREEN', 'Зеленый')
)
