from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Книги библиотеки'
    _order = 'name'

    name = fields.Char(string='Название', required=True)
    isbn = fields.Char(string='ISBN', required=True, copy=False)
    publication_year = fields.Integer(string='Год выпуска')
    pages = fields.Integer(string='Количество страниц')
    description = fields.Text(string='Описание')
    
    author_ids = fields.Many2many('library.author', string='Авторы')
    
    age_years = fields.Integer(compute='_compute_age_years', string='Возраст', store=True)

    _check_isbn_unique = models.Constraint('UNIQUE(isbn)', 'ISBN должен быть уникальным!') 
    
    @api.depends('publication_year')
    def _compute_age_years(self):
        current_year = fields.Date.today().year
        for book in self:
            if book.publication_year:
                book.age_years = current_year - book.publication_year
            else:
                book.age_years = 0
    
    @api.constrains('publication_year')
    def _check_publication_year(self):
        current_year = fields.Date.today().year
        for book in self:
            if book.publication_year and book.publication_year > current_year:
                raise ValidationError('Год выпуска не может быть будущим!')
    
    @api.constrains('pages')
    def _check_pages(self):
        for book in self:
            if book.pages and book.pages <= 0:
                raise ValidationError('Количество страниц должно быть положительным числом!')