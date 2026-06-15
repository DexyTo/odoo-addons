from odoo import models, fields, api

class MeetingRoom(models.Model):
    _name = 'meeting.room'
    _description = 'Переговорная комната'
    _order = 'name'

    name = fields.Char(string='Комната', required=True)
    capacity = fields.Integer(string='Вместимость', default=1)
    equipment = fields.Text(string='Доступное оборудование')
    active = fields.Boolean(string='Открыта', default=True)
    
    booking_ids = fields.One2many(
        'room.booking', 
        'room_id', 
        string='Бронирования'
    )

    location_id = fields.Many2one(
        'meeting.room.location',
        string='Местоположение',
        required=True,
        ondelete='restrict'  # Нельзя удалить локацию, если есть комнаты
    )

    active_bookings_count = fields.Integer(
        compute='_compute_active_bookings_count',
        string='Количество активных бронирований'   
    )
    
    @api.depends('booking_ids', 'booking_ids.state')
    def _compute_active_bookings_count(self):
        for room in self:
            room.active_bookings_count = len(
                room.booking_ids.filtered(lambda b: b.state == 'active')
            )