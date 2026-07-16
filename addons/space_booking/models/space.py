from odoo import models, fields, api, exceptions


class Space(models.Model):
    _name = 'space'
    _description = 'Бронируемое помещение'
    _order = 'name'

    name = fields.Char(string='Помещение', required=True,
                       help='Название помещения (например, "Конференц-зал Главный')
    capacity = fields.Integer(string='Вместимость', required=True, default=1,
                              help='Максимальное количество человек, которое может разместиться в этом помещении')
    equipment = fields.Text(string='Доступное оборудование')
    active = fields.Boolean(string='Открыта', default=True,
                            help='Снимите флажок, чтобы заархивировать это помещение, не удаляя его')

    space_type = fields.Selection([
        ('meeting_room', 'Переговорная комната'),
        ('coworking', 'Коворкинг'),
        ('classroom', 'Учебная комната'),
        ('conference_hall', 'Конференц-зал'),
        ('training_room', 'Зал для тренировок'),
        ('event_space', 'Помещение для проведения мероприятий'),
        ('hall', 'Актовый зал'),
        ('other', 'Другое'),
    ], string='Тип помещения', required=True, default='meeting_room')

    display_name = fields.Char(
        compute='_compute_display_name',
        store=False, 
    )

    booking_ids = fields.One2many(
        'space.booking',
        'space_id',
        string='Бронирования'
    )

    location_id = fields.Many2one(
        'space.location',
        string='Местоположение',
        ondelete='restrict',
        help='Физическое местоположение, где расположено это помещение'
    )

    booking_count = fields.Integer(
        string='Общее количество бронирований',
        compute='_compute_booking_count',
        store=True,
        help='Общее количество бронирований этого помещения'
    )

    active_bookings_count = fields.Integer(
        compute='_compute_active_bookings_count',
        string='Количество активных бронирований',
        help='Количество активных в данный момент бронирований'
    )

    @api.depends('booking_ids')
    def _compute_booking_count(self):
        for space in self:
            space.booking_count = len(space.booking_ids)

    @api.depends('booking_ids.state')
    def _compute_active_bookings_count(self):
        for space in self:
            space.active_bookings_count = len(
                space.booking_ids.filtered(lambda b: b.state == 'active')
            )

    @api.constrains('capacity')
    def _check_capacity_positive(self):
        for space in self:
            if space.capacity < 1:
                raise exceptions.ValidationError(
                    "Вместимость должна составлять не менее 1 человека!")
    
    @api.depends('name', 'space_type', 'capacity')
    def _compute_display_name(self):
        type_labels = dict(self._fields['space_type'].selection)
        for space in self:
            type_label = type_labels.get(space.space_type, '')
            space.display_name = f"{space.name or '#'} ({type_label}, {space.capacity} чел.)"
 
    def name_get(self):
        return [(space.id, space.display_name) for space in self]
    
    def action_view_bookings(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Бронирования: {self.name}',
            'res_model': 'space.booking',
            'view_mode': 'list,form,calendar',
            'domain': [('space_id', '=', self.id)],
            'context': {'default_space_id': self.id},
        }
