from odoo import models, fields, api, exceptions
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    booking_ids = fields.One2many(
        'room.booking',
        'partner_id',
        string='Мои бронирования'
    )
    
    total_bookings_hours_month = fields.Float(
        compute='_compute_total_bookings_hours_month',
        string='Часы бронирования за месяц'
    )
    
    total_bookings_hours_week = fields.Float(
        compute='_compute_total_bookings_hours_week',
        string='Часы бронирования за неделю'
    )
    
    @api.depends('booking_ids', 'booking_ids.start_time', 'booking_ids.end_time', 'booking_ids.state')
    def _compute_total_bookings_hours_month(self):
        for partner in self:
            # Определяем начало и конец текущего месяца
            now = fields.Datetime.now()
            month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            
            if now.month == 12:
                month_end = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                month_end = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
            
            month_bookings = partner.booking_ids.filtered(
                lambda b: b.start_time >= month_start 
                and b.start_time < month_end
                and b.state in ['active', 'done']
            )
            
            total_hours = sum(month_bookings.mapped('duration'))
            partner.total_bookings_hours_month = total_hours
    
    @api.depends('booking_ids', 'booking_ids.start_time', 'booking_ids.end_time', 'booking_ids.state')
    def _compute_total_bookings_hours_week(self):
        for partner in self:
            # Определяем начало и конец текущей недели 
            now = fields.Datetime.now()
            week_start = now - timedelta(days=now.weekday()) 
            week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
            week_end = week_start + timedelta(days=7)
            
            week_bookings = partner.booking_ids.filtered(
                lambda b: b.start_time >= week_start 
                and b.start_time < week_end
                and b.state in ['active', 'done']
            )
            
            total_hours = sum(week_bookings.mapped('duration'))
            partner.total_bookings_hours_week = total_hours
    
    def action_view_bookings(self):
        self.ensure_one()
        return {
            'name': 'Мои бронирования',
            'type': 'ir.actions.act_window',
            'res_model': 'room.booking',
            'view_mode': 'list,form,calendar',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
