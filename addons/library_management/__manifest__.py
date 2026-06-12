{
    'name': 'Управление библиотекой',
    'version': '1.0',
    'depends': ['base'],
    'author': 'Белянин Иван',
    'category': 'Библиотека',
    'description': """
        Система управления библиотекой
        =========================
        * Управление книгами
        * Управление авторами
        * Отслеживание заимствованных книг
    """,
    'data': [
        'security/ir.model.access.csv',
        
        'views/book_views.xml',
        'views/author_views.xml',
        'views/res_partner_views.xml',
        'views/library_menu_views.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
} # type: ignore