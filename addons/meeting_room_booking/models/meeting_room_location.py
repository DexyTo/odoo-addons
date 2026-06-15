from odoo import models, fields, api

class MeetingRoomLocation(models.Model):
    _name = 'meeting.room.location'
    _description = 'Местоположение переговорной комнаты'
    _order = 'floor, section'

    section = fields.Char(string='Секция', required=True)
    floor = fields.Integer(string='Этаж', required=True)

    name = fields.Char(
        string='Местоположение', 
        compute='_compute_name',
        default='В здании',
        store=True,  
    )

    room_ids = fields.One2many(
        'meeting.room',
        'location_id',
        string='Переговорные'
    )
    
    room_count = fields.Integer(
        string='Количество переговорных',
        compute='_compute_room_count'
    )
    
    @api.depends('room_ids')
    def _compute_room_count(self):
        for location in self:
            location.room_count = len(location.room_ids)
    
    @api.depends('section', 'floor')
    def _compute_name(self):
        for location in self:
            if location.section and location.floor:
                location.name = f"Этаж {location.floor}, Секция {location.section}"
            elif location.floor:
                location.name = f"Этаж {location.floor}"
            elif location.section:
                location.name = f"Секция {location.section}"
            else:
                location.name = "В здании"
    