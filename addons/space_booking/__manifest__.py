{
    'name': 'Бронирование помещений',
    'version': '19.0.1.0.0',
    'depends': ['base', 'mail', 'calendar'],
    'author': 'Белянин Иван',
    'category': 'Productivity',
    'summary': 'Бронируйте конференц-залы, коворкинги, учебные комнаты и другие помещения',
    'description': """
        Модуль бронирования помещений
        =========================

        Комплексное решение для управления резервированием пространства:
        
        Ключевые возможности:
        -------------
        * Поддержка различных типов помещений (переговорные комнаты, коворкинги, учебные классы, конференц-залы)
        * Выявление и проверка конфликтных ситуаций
        * Управление доступом на основе ролей (пользователь / менеджер)
        * Автоматизированные рабочие процессы и напоминания
        * Интерактивный просмотр календаря с возможностью перетаскивания брони
    """,
    'data': [
        'security/booking_security.xml',
        'security/ir.model.access.csv',

        'views/space_location_views.xml',
        'views/space_views.xml',
        'views/space_booking_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',

        'data/ir_cron.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'space_booking/static/src/css/space_booking.css'
        ],
    },
    'application': True,
    'license': 'LGPL-3',
} # type: ignore