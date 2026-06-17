{
    'name': 'Бронирование переговорных',
    'version': '1.0',
    'depends': ['base', 'calendar'],
    'author': 'Белянин Иван',
    'category': 'Services',
    'description': """
        Модуль для бронирования переговорных комнат включающий:
        =========================
        * Управление комнатами
        * Бронирование с указанием временных интервалов
        * Выявление пересечений
        * Ограничения на бронирование пользователями
    """,
    'data': [
        'security/booking_security.xml',
        'security/ir.model.access.csv',

        'views/meeting_room_location_views.xml',
        'views/meeting_room_views.xml',
        'views/room_booking_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',

        'data/ir_cron.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
} # type: ignore