from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta


class TestBookingConstraints(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestBookingConstraints, cls).setUpClass()
        
        cls.location = cls.env['space.location'].create({
            'name': 'Test Building',
            'address': '123 Test Street',
        })
        
        cls.space = cls.env['space'].create({
            'name': 'Помещение для тестов ограничений',
            'capacity': 10,
            'location_id': cls.location.id,
        })
        
        cls.partner1 = cls.env['res.partner'].create({'name': 'Партнёр 1'})
        cls.partner2 = cls.env['res.partner'].create({'name': 'Партнёр 2'})
        
        cls.start_time = datetime.now() + timedelta(hours=1)
        cls.end_time = cls.start_time + timedelta(hours=2)

    def test_01_no_overlap_same_room(self):
        """Тест: нельзя создать пересекающиеся бронирования одной комнаты"""
        booking1 = self.env['space.booking'].create({
            'name': 'Первое бронирование',
            'space_id': self.space.id,
            'partner_id': self.partner1.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        with self.assertRaises(ValidationError, msg="Должна быть ошибка при пересечении"):
            self.env['space.booking'].create({
                'name': 'Пересекающееся бронирование',
                'space_id': self.space.id,
                'partner_id': self.partner2.id,
                'start_time': self.start_time + timedelta(minutes=30),
                'end_time': self.end_time + timedelta(minutes=30),
                'state': 'active',
            })

    def test_02_overlap_different_rooms(self):
        """Тест: можно создавать одновременные бронирования разных комнат"""
        room2 = self.env['space'].create({
            'name': 'Комната 2',
            'capacity': 5,
            'location_id': self.location.id,
        })
        
        booking1 = self.env['space.booking'].create({
            'name': 'Бронирование 1',
            'space_id': self.space.id,
            'partner_id': self.partner1.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        booking2 = self.env['space.booking'].create({
            'name': 'Бронирование 2',
            'space_id': room2.id,
            'partner_id': self.partner2.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        self.assertTrue(booking2.id, "Бронирование другой комнаты должно быть создано")

    def test_03_draft_bookings_no_overlap_check(self):
        """Тест: черновики не проверяются на пересечение"""
        booking1 = self.env['space.booking'].create({
            'name': 'Активное',
            'space_id': self.space.id,
            'partner_id': self.partner1.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        # Черновик с пересечением - должен создаться
        booking2 = self.env['space.booking'].create({
            'name': 'Черновик',
            'space_id': self.space.id,
            'partner_id': self.partner2.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'draft',
        })
        
        self.assertTrue(booking2.id, "Черновик должен создаться даже при пересечении")
        
        # Но при подтверждении должна быть ошибка
        with self.assertRaises(ValidationError):
            booking2.action_confirm()

    def test_04_adjacent_bookings(self):
        """Тест: соседние бронирования (без пересечения) должны создаваться"""
        booking1 = self.env['space.booking'].create({
            'name': 'С 10 до 12',
            'space_id': self.space.id,
            'partner_id': self.partner1.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        booking2 = self.env['space.booking'].create({
            'name': 'С 12 до 14',
            'space_id': self.space.id,
            'partner_id': self.partner2.id,
            'start_time': self.end_time,  # Начало = конец первого
            'end_time': self.end_time + timedelta(hours=2),
            'state': 'active',
        })
        
        self.assertTrue(booking2.id, "Соседние бронирования должны создаваться")