from odoo import models, fields, api, exceptions
from datetime import timedelta


class SpaceBooking(models.Model):
    _name = 'space.booking'
    _description = 'Бронирование помещений'
    _order = 'start_time desc'

    name = fields.Char(string='Цель бронирования', required=True)
    notes = fields.Text(string='Комментарий')
    start_time = fields.Datetime(string='С', required=True)
    end_time = fields.Datetime(string='По', required=True)

    state = fields.Selection([
        ('draft', 'Черновик'),
        ('active', 'Активно'),
        ('done', 'Завершено'),
        ('cancelled', 'Отменено'),
    ], string='Статус', required=True, copy=False, default='draft')

    space_id = fields.Many2one(
        'space', string='Помещение', required=True, ondelete='restrict')
    partner_id = fields.Many2one('res.partner', string='Организатор', required=True, copy=False,
                                 default=lambda self: self.env.user.partner_id)

    duration = fields.Float(
        compute='_compute_duration',
        string='Длительность (часы)',
        store=True
    )

    display_name = fields.Char(
        compute='_compute_display_name',
        store=False
    )


    calendar_event_id = fields.Many2one(
        'calendar.event',
        string='Событие в календаре',
        ondelete='set null',
        copy=False
    )

    alarm_ids = fields.Many2many(
        'calendar.alarm',
        string='Напоминание',
        default=lambda self: self._get_default_alarm().ids
    )

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for booking in self:
            if booking.start_time and booking.end_time:
                delta = booking.end_time - booking.start_time
                booking.duration = delta.total_seconds() / 3600.0
            else:
                booking.duration = 0.0

    @api.constrains('space_id', 'start_time', 'end_time', 'state')
    def _check_no_overlap(self):
        active_bookings = self.filtered(lambda b: b.state == 'active')
        if not active_bookings:
            return

        # Вспомогательная функция для форматирования даты/времени в часовом поясе пользователя
        def _format_local_dt(record, dt):
            local_dt = fields.Datetime.context_timestamp(record, dt)
            return local_dt.strftime('%d.%m.%Y %H:%M')

        for booking in active_bookings:
            domain = [
                ('space_id', '=', booking.space_id.id),
                ('state', 'in', ['active']),
                ('id', '!=', booking.id),
                ('start_time', '<', booking.end_time),
                ('end_time', '>', booking.start_time),
            ]
            if self.search_count(domain, limit=1) > 0:
                conflicts = self.search(domain)
                conflict_details = "\n".join(
                    "Бронь #{} с {} по {}".format(
                        c.id,
                        _format_local_dt(booking, c.start_time),
                        _format_local_dt(booking, c.end_time)
                    ) for c in conflicts
                )
                raise exceptions.ValidationError(
                    "Помещение уже забронировано для выбранного времени!\n"
                    "Конфликт с:\n" + conflict_details
                )

    @api.constrains('start_time')
    def _check_start_time_future(self):
        for booking in self:
            if booking.start_time:
                min_start = fields.Datetime.now() + timedelta(minutes=10)
                if booking.start_time < min_start:
                    raise exceptions.ValidationError(
                        "Бронирование возможно не ранее чем через 10 минут от текущего времени!"
                    )

    @api.constrains('state')
    def _check_active_state_time(self):
        for booking in self:
            if booking.state == 'active' and booking.start_time:
                if booking.start_time <= fields.Datetime.now():
                    raise exceptions.ValidationError(
                        "Нельзя подтвердить бронирование, время начала которого уже прошло."
                    )

    @api.constrains('start_time', 'end_time')
    def _check_duration_limits(self):
        for booking in self:
            if booking.start_time and booking.end_time:
                if booking.end_time <= booking.start_time:
                    raise exceptions.ValidationError(
                        "Время окончания должно быть позже времени начала!"
                    )

                duration_minutes = (booking.end_time -
                                    booking.start_time).total_seconds() / 60

                if duration_minutes < 10:
                    raise exceptions.ValidationError(
                        "Минимальная длительность бронирования — 10 минут!"
                    )

                if duration_minutes > 1440:
                    raise exceptions.ValidationError(
                        "Максимальная длительность бронирования — 24 часа!"
                    )

    def _get_default_alarm(self):
        alarm = self.env['calendar.alarm'].search([
            ('alarm_type', '=', 'notification'),
            ('duration', '=', 15),
            ('interval', '=', 'minutes'),
        ], limit=1)

        if not alarm:
            alarm = self.env['calendar.alarm'].create({
                'name': 'Напоминание за 15 минут',
                'alarm_type': 'notification',
                'duration': 15,
                'interval': 'minutes',
            })
        return alarm

    def _create_calendar_event(self):
        self.ensure_one()
        if self.calendar_event_id:
            return

        partner_ids = []
        if self.partner_id:
            partner_ids.append(self.partner_id.id)

        alarms = self.alarm_ids
        event_vals = {
            'name': f"Бронирование: {self.name}",
            'start': self.start_time,
            'stop': self.end_time,
            'alarm_ids': [(6, 0, alarms.ids)],
            'partner_ids': [(6, 0, partner_ids)],
            'description': '',
            'user_id': self.env.user.id,
            'privacy': 'private',
        }

        event = self.env['calendar.event'].create(event_vals)
        self.calendar_event_id = event.id

    def _update_calendar_event(self):
        self.ensure_one()
        if not self.calendar_event_id:
            return

        self.calendar_event_id.write({
            'start': self.start_time,
            'stop': self.end_time,
            'name': f"Бронирование: {self.name}",
            'description': '',
        })

    def _delete_calendar_event(self):
        self.ensure_one()
        if self.calendar_event_id:
            self.calendar_event_id.unlink()
            self.calendar_event_id = False

    def copy(self, default=None):
        if default is None:
            default = {}

        default['name'] = f"{self.name} (Копия)"

        return super().copy(default)

    def write(self, vals):
        result = super(SpaceBooking, self).write(vals)

        if 'start_time' in vals or 'end_time' in vals:
            for booking in self:
                if booking.state == 'active' and booking.calendar_event_id:
                    booking._update_calendar_event()

        return result

    def action_confirm(self):
        for record in self:
            record.state = 'active'
            record._create_calendar_event()
        return True

    def action_done(self):
        for record in self:
            record.state = 'done'
            record._delete_calendar_event()
        return True

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
            record._delete_calendar_event()
        return True

    def action_draft(self):
        for record in self:
            record.state = 'draft'
            record._delete_calendar_event()
        return True

    def release_expired_bookings(self):
        now = fields.Datetime.now()
        expired_bookings = self.search([
            ('state', '=', 'active'),
            ('end_time', '<', now),
        ])

        if expired_bookings:
            expired_bookings.write({'state': 'done'})

        return True
    
    @api.depends('name', 'space_id.name')
    def _compute_display_name(self):
        for booking in self:
            booking.display_name = f"{booking.name} ({booking.space_id.name or ''})"
    
    def name_get(self):
        return [(booking.id, booking.display_name) for booking in self]
