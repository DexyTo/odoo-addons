from odoo import models, fields, api, exceptions
from datetime import timedelta


class RoomBooking(models.Model):
    _name = 'room.booking'
    _description = 'Бронирование переговорной'
    _order = 'start_time desc'

    name = fields.Char(string='Цель брони', required=True)
    notes = fields.Text(string='Комментарий')
    start_time = fields.Datetime(string='С', required=True)
    end_time = fields.Datetime(string='По', required=True)

    state = fields.Selection([
        ('draft', 'Черновик'),
        ('active', 'Активно'),
        ('done', 'Завершено'),
        ('cancelled', 'Отменено'),
    ], string='Статус', default='draft', required=True, copy=False)

    room_id = fields.Many2one('meeting.room', string='Комната', required=True)
    partner_id = fields.Many2one(
        'res.partner', string='Организатор', required=True)

    duration = fields.Float(
        compute='_compute_duration',
        string='Длительность (часы)',
        store=True
    )

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for booking in self:
            if booking.start_time and booking.end_time:
                delta = booking.end_time - booking.start_time
                booking.duration = delta.total_seconds() / 3600.0
            else:
                booking.duration = 0.0

    @api.constrains('room_id', 'start_time', 'end_time', 'state')
    def _check_no_overlap(self):
        active_bookings = self.filtered(lambda b: b.state == 'active')
        if not active_bookings:
            return

        for booking in active_bookings:
            domain = [
                ('room_id', '=', booking.room_id.id),
                ('state', 'in', ['active']),
                ('id', '!=', booking.id),
                ('start_time', '<', booking.end_time),
                ('end_time', '>', booking.start_time),
            ]
            if self.search_count(domain, limit=1) > 0:
                raise exceptions.ValidationError(
                    "Время пересекается с другим бронированием!")

    @api.constrains('start_time')
    def _check_start_time_future(self):
        for booking in self:
            if booking.start_time:
                min_start = fields.Datetime.now() + timedelta(minutes=10)
                if booking.start_time < min_start:
                    raise exceptions.ValidationError(
                        "Бронирование возможно не ранее чем через 10 минут от текущего времени!"
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

                if duration_minutes < 15:
                    raise exceptions.ValidationError(
                        "Минимальная длительность бронирования — 15 минут!"
                    )

                if duration_minutes > 240:
                    raise exceptions.ValidationError(
                        "Максимальная длительность бронирования — 4 часа!"
                    )

    @api.constrains('partner_id', 'start_time', 'state')
    def _check_weekly_booking_limit(self):
        for booking in self:
            if booking.state not in ['active', 'done']:
                continue

            # Определяем текущую неделю для бронирования
            booking_week_start = booking.start_time - \
                timedelta(days=booking.start_time.weekday())
            booking_week_start = booking_week_start.replace(
                hour=0, minute=0, second=0, microsecond=0)
            booking_week_end = booking_week_start + timedelta(days=7)

            # Находим все бронирования пользователя в эту неделю
            week_bookings = self.search([
                ('partner_id', '=', booking.partner_id.id),
                ('id', '!=', booking.id),
                ('state', 'in', ['active', 'done']),
                ('start_time', '>=', booking_week_start),
                ('start_time', '<', booking_week_end),
            ])

            # Суммируем часы
            total_hours = sum(week_bookings.mapped(
                'duration')) + booking.duration

            if total_hours > 12:
                raise exceptions.ValidationError(
                    f"Превышен недельный лимит бронирования! "
                    f"Вы забронировали {total_hours:.1f} часов из 12 допустимых в эту неделю."
                )

    def action_confirm(self):
        for record in self:
            record.state = 'active'
        return True

    def action_done(self):
        for record in self:
            record.state = 'done'
        return True

    def action_cancel(self):
        for record in self:
            record.state = 'cancelled'
        return True

    def action_draft(self):
        for record in self:
            record.state = 'draft'
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
