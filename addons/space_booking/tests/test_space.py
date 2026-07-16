from odoo.tests import TransactionCase
from odoo.exceptions import ValidationError


class TestSpace(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestSpace, cls).setUpClass()
        
        cls.location = cls.env['space.location'].create({
            'name': 'Test Building',
            'address': '123 Test Street',
        })

    def test_create_space(self):
        """Тест создания помещения"""
        space = self.env['space'].create({
            'name': 'Test Conference Hall',
            'space_type': 'conference_hall',
            'capacity': 50,
            'location_id': self.location.id,
        })
        
        self.assertTrue(space.id)
        self.assertEqual(space.space_type, 'conference_hall')
        self.assertEqual(space.capacity, 50)
    
    def test_capacity_constraint(self):
        """Тест constraint на вместимость"""
        with self.assertRaises(ValidationError):
            self.env['space'].create({
                'name': 'Invalid Space',
                'space_type': 'meeting_room',
                'capacity': 0,  # Недопустимое значение
            })
    
    def test_booking_count(self):
        """Тест подсчёта бронирований"""
        space = self.env['space'].create({
            'name': 'Test Room',
            'space_type': 'meeting_room',
            'capacity': 10,
        })
        
        # Создаём бронирование
        self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': space.id,
            'start_time': '2026-12-15 10:00:00',
            'end_time': '2026-12-15 11:00:00',
        })
        
        self.assertEqual(space.booking_count, 1)

    def test_name_get(self):
        """Тест отображения имени"""
        space = self.env['space'].create({
            'name': 'Alpha',
            'space_type': 'meeting_room',
            'capacity': 12,
        })
        
        name = space.name_get()[0][1]
        self.assertIn('Alpha', name)
        self.assertIn('Переговорная комната', name)
        self.assertIn('12 чел.', name)
    
    def test_archive_space(self):
        """Тест архивирования помещения"""
        space = self.env['space'].create({
            'name': 'Test Space',
            'space_type': 'classroom',
            'capacity': 30,
            'active': True,
        })
        
        # Архивируем
        space.active = False
        self.assertFalse(space.active)





