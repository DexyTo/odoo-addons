from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestRoomBooking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestRoomBooking, cls).setUpClass()
        
        cls.location = cls.env['meeting.room.location'].create({
            'floor': 1,
            'section': 'A',
        })
        
        cls.room = cls.env['meeting.room'].create({
            'name': 'Комната для тестов',
            'capacity': 10,
            'location_id': cls.location.id,
        })
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'Тестовый организатор',
        })
        
        cls.now = datetime.now()
        cls.start_time = cls.now + timedelta(hours=1)
        cls.end_time = cls.start_time + timedelta(hours=2)

    def test_01_booking_creation(self):
        """Тест создания бронирования"""
        booking = self.env['room.booking'].create({
            'name': 'Тестовое бронирование',
            'room_id': self.room.id,
            'partner_id': self.partner.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        self.assertTrue(booking.id, "Бронирование должно быть создано")
        self.assertEqual(booking.state, 'draft', "Новое бронирование в статусе draft")

    def test_02_duration_computation(self):
        """Тест вычисления длительности"""
        booking = self.env['room.booking'].create({
            'name': 'Тест длительности',
            'room_id': self.room.id,
            'partner_id': self.partner.id,
            'start_time': self.start_time,
            'end_time': self.start_time + timedelta(hours=3),
        })
        
        self.assertEqual(booking.duration, 3.0, "Длительность должна быть 3 часа")

    def test_03_invalid_dates(self):
        """Тест: время окончания должно быть позже начала"""
        with self.assertRaises(ValidationError, msg="Должна быть ошибка при неверных датах"):
            self.env['room.booking'].create({
                'name': 'Неверные даты',
                'room_id': self.room.id,
                'partner_id': self.partner.id,
                'start_time': self.end_time,
                'end_time': self.start_time, 
            })

    def test_04_booking_state_transitions(self):
        """Тест переходов между статусами"""
        booking = self.env['room.booking'].create({
            'name': 'Тест статусов',
            'room_id': self.room.id,
            'partner_id': self.partner.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # draft → active
        booking.action_confirm()
        self.assertEqual(booking.state, 'active')
        
        # active → cancelled
        booking.action_cancel()
        self.assertEqual(booking.state, 'cancelled')

    def test_05_copy_booking(self):
        """Тест дублирования бронирования"""
        original = self.env['room.booking'].create({
            'name': 'Оригинал',
            'room_id': self.room.id,
            'partner_id': self.partner.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        copy = original.copy()
        
        self.assertEqual(copy.state, 'draft', "Копия должна быть в статусе draft")
        self.assertIn('Копия', copy.name, "Название должно содержать '(Копия)'")

    def test_06_default_partner(self):
        """Тест автоподстановки партнёра"""
        # Создаём пользователя с партнёром
        user = self.env['res.users'].create({
            'name': 'Тестовый пользователь',
            'login': 'testuser@test.com',
        })
        
        # Создаём бронирование от имени этого пользователя
        booking = self.env['room.booking'].with_user(user).create({
            'name': 'Тест автоподстановки',
            'room_id': self.room.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        self.assertEqual(booking.partner_id, user.partner_id, "Партнёр должен подставляться автоматически")