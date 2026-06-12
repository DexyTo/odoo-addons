from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    is_library_member = fields.Boolean(string='Читатель библиотеки', default=False)
    
    borrowed_book_ids = fields.Many2many('library.book', 'partner_book_rel', 'partner_id', 'book_id', string='Заимствованные книги')
    
    borrowed_books_count = fields.Integer(compute='_compute_borrowed_books_count', string='Количество заимствованных книг')
    
    @api.depends('borrowed_book_ids')
    def _compute_borrowed_books_count(self):
        for partner in self:
            partner.borrowed_books_count = len(partner.borrowed_book_ids)
    
    @api.constrains('borrowed_book_ids')
    def _check_borrowed_books_limit(self):
        for partner in self:
            if len(partner.borrowed_book_ids) > 5:
                raise ValidationError('Читатель не может взять в библиотеке больше 5 книг!')