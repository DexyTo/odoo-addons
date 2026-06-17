from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestMeetingRoom(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestMeetingRoom, cls).setUpClass()
        
        cls.location = cls.env['meeting.room.location'].create({
            'floor': 1,
            'section': 'A',
        })
        
        cls.room = cls.env['meeting.room'].create({
            'name': 'Тестовая комната',
            'capacity': 10,
            'location_id': cls.location.id,
            'equipment': 'Проектор, Доска',
        })

    def test_01_room_creation(self):
        """Тест создания комнаты"""
        self.assertTrue(self.room.id, "Комната должна быть создана")
        self.assertEqual(self.room.name, 'Тестовая комната')
        self.assertEqual(self.room.capacity, 10)
        self.assertTrue(self.room.active, "Новая комната должна быть активна")

    def test_02_room_capacity_positive(self):
        """Тест: вместимость должна быть положительной"""
        with self.assertRaises(ValidationError, msg="Должна быть ошибка при отрицательной вместимости"):
            self.room.capacity = -5

    def test_03_active_bookings_count(self):
        """Тест подсчёта активных бронирований"""
        partner = self.env['res.partner'].create({
            'name': 'Тестовый партнёр',
        })
        
        booking = self.env['room.booking'].create({
            'name': 'Тестовое бронирование',
            'room_id': self.room.id,
            'partner_id': partner.id,
            'start_time': datetime.now() + timedelta(hours=1),
            'end_time': datetime.now() + timedelta(hours=2),
            'state': 'active',
        })
        
        self.assertEqual(self.room.active_bookings_count, 1, "Должно быть 1 активное бронирование")
        
        booking.state = 'cancelled'
        self.assertEqual(self.room.active_bookings_count, 0, "После отмены активных бронирований быть не должно")

    def test_04_room_archive(self):
        """Тест архивации комнаты"""
        self.room.active = False
        self.assertFalse(self.room.active, "Комната должна быть архивирована")


class TestMeetingRoomLocation(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestMeetingRoomLocation, cls).setUpClass()

        cls.location = cls.env['meeting.room.location'].create({
            'floor': 2,
            'section': 'C',
        })

    def test_01_location_creation(self):
        """Тест создания локации"""
        self.assertTrue(self.location.id)
        self.assertEqual(self.location.floor, 2)
        self.assertEqual(self.location.section, 'C')

    def test_02_location_name_compute(self):
        """Тест вычисляемого поля name"""
        self.assertEqual(self.location.name, 'Этаж 2, Секция C', "Название должно формироваться автоматически")

    def test_03_room_count(self):
        """Тест подсчёта комнат в локации"""
        self.env['meeting.room'].create({
            'name': 'Комната 1',
            'capacity': 5,
            'location_id': self.location.id,
        })
        self.env['meeting.room'].create({
            'name': 'Комната 2',
            'capacity': 8,
            'location_id': self.location.id,
        })
        
        self.assertEqual(self.location.room_count, 2, "Должно быть 2 комнаты")