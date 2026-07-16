from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestSpaceBooking(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestSpaceBooking, cls).setUpClass()
        
        cls.space = cls.env['space'].create({
            'name': 'Test Room',
            'space_type': 'meeting_room',
            'capacity': 10,
        })
        
        cls.partner = cls.env['res.partner'].create({
            'name': 'Test User',
            'email': 'test@example.com',
        })

        cls.now = datetime.now()

    def test_create_booking(self):
        """Тест создания бронирования"""
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'partner_id': self.partner.id,
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2),
        })
        
        self.assertTrue(booking.id)
        self.assertEqual(booking.state, 'draft')

    def test_duration_computation(self):
        """Тест вычисления длительности"""
        start = datetime(2026, 12, 15, 10, 0, 0)
        end = datetime(2026, 12, 15, 12, 30, 0)
        
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'start_time': start,
            'end_time': end,
        })
        
        self.assertEqual(booking.duration, 2.5)

    def test_invalid_dates(self):
        """Тест проверки некорректных дат"""
        with self.assertRaises(ValidationError):
            self.env['space.booking'].create({
                'name': 'Invalid Booking',
                'space_id': self.space.id,
                'start_time': '2024-01-15 12:00:00',
                'end_time': '2024-01-15 10:00:00',  # Конец раньше начала
            })

    def test_conflict_detection(self):
        """Тест обнаружения конфликтов"""
        # Создаём первое бронирование
        booking1 = self.env['space.booking'].create({
            'name': 'Meeting 1',
            'space_id': self.space.id,
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2),
        })
        booking1.action_confirm()
        
        # Пытаемся создать конфликтующее бронирование
        booking2 = self.env['space.booking'].create({
            'name': 'Meeting 2',
            'space_id': self.space.id,
            'start_time': self.now + timedelta(minutes=70),
            'end_time': self.now + timedelta(hours=3),
        })
        
        with self.assertRaises(ValidationError):
            booking2.action_confirm()

    def test_workflow_transitions(self):
        """Тест переходов по статусам"""
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2),
        })
        
        # Draft → Active
        booking.action_confirm()
        self.assertEqual(booking.state, 'active')
        
        # Active → Done
        booking.action_done()
        self.assertEqual(booking.state, 'done')

    def test_cancel_booking(self):
        """Тест отмены бронирования"""
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2),
        })
        
        booking.action_confirm()
        booking.action_cancel()
        self.assertEqual(booking.state, 'cancelled')

    def test_name_get(self):
        """Тест отображения имени"""
        booking = self.env['space.booking'].create({
            'name': 'Team Sync',
            'space_id': self.space.id,
            'start_time': self.now + timedelta(hours=1),
            'end_time': self.now + timedelta(hours=2),
        })
        
        name = booking.name_get()[0][1]
        self.assertIn('Team Sync', name)
        self.assertIn('Test Room', name)