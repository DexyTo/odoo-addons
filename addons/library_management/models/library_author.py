from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryAuthor(models.Model):
    _name = 'library.author'
    _description = 'Авторы книг'
    _order = 'name'

    name = fields.Char(string='Имя', required=True)
    biography = fields.Text(string='Биография')
    birth_date = fields.Date(string='Дата рождения')
    
    book_ids = fields.Many2many('library.book', string='Книги')
    
    book_count = fields.Integer(compute='_compute_book_count', string='Количество книг', store=True)
    
    @api.depends('book_ids')
    def _compute_book_count(self):
        for author in self:
            author.book_count = len(author.book_ids)
  
    
    @api.constrains('birth_date')
    def _check_birth_date(self):
        today = fields.Date.today()
        for author in self:
            if author.birth_date and author.birth_date > today:
                raise ValidationError('Дата рождения не может быть будущей!')