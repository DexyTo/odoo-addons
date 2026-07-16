from odoo import models, fields, api

class SpaceLocation(models.Model):
    _name = 'space.location'
    _description = 'Местоположение помещений'
    _order = 'name'

    name = fields.Char(
        string='Местоположение',
        required=True,
        help='Название здания или этажа (например, "Главное здание", "Этаж 3")'
    )

    address = fields.Text(
        string='Адрес',
        help='Физический адрес этого местоположения'
    )

    space_ids = fields.One2many(
        'space',
        'location_id',
        string='Помещения',
        help='Все помещения в этом месте'
    )
    
    space_count = fields.Integer(
        string='Количество помещений',
        compute='_compute_space_count',
        store=True,
        help='Общее количество помещений в этом месте'
    )
    
    @api.depends('space_ids')
    def _compute_space_count(self):
        for location in self:
            location.space_count = len(location.space_ids)

    def action_view_spaces(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Помещения в {self.name}',
            'res_model': 'space',
            'view_mode': 'list,form',
            'domain': [('location_id', '=', self.id)],
            'context': {'default_location_id': self.id},
        }