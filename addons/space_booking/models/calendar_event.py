from odoo import models, exceptions


class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    def write(self, vals):
        if 'start' in vals or 'stop' in vals:
            for event in self:
                booking = self.env['space.booking'].search(
                    [('calendar_event_id', '=', event.id)], limit=1
                )
                if booking:
                    raise exceptions.ValidationError(
                        "Нельзя изменить дату события, связанного с бронью помещения, в этом календаре.\nИзменяйте дату через саму бронь."
                    )
        return super().write(vals)
