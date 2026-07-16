from odoo.tests import TransactionCase
from odoo.exceptions import AccessError
from datetime import datetime, timedelta


class TestBookingSecurity(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super(TestBookingSecurity, cls).setUpClass()
        
        cls.group_manager = cls.env.ref('space_booking.group_space_booking_manager')
        cls.group_user = cls.env.ref('base.group_user')
        
        # Создаём пользователей
        cls.user_1 = cls.env['res.users'].create({
            'name': 'User 1',
            'login': 'user1',
            'email': 'user1@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        
        cls.user_2 = cls.env['res.users'].create({
            'name': 'User 2',
            'login': 'user2',
            'email': 'user2@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        
        cls.manager = cls.env['res.users'].create({
            'name': 'Manager',
            'login': 'manager',
            'email': 'manager@test.com',
            'group_ids': [(6, 0, [cls.group_manager.id])],
        })
        
        # Создаём помещение
        cls.space = cls.env['space'].create({
            'name': 'Test Room',
            'space_type': 'meeting_room',
            'capacity': 10,
        })

        cls.now = datetime.now()
        cls.start_time = datetime.now() + timedelta(hours=1)
        cls.end_time = datetime.now() + timedelta(hours=2)

    def test_user_can_create_booking(self):
        """Тест: пользователь может создать бронирование"""
        booking = self.env['space.booking'].with_user(self.user_1).create({
            'name': 'My Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_1.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        self.assertTrue(booking.id)

    def test_user_can_read_own_booking(self):
        """Тест: пользователь видит свои бронирования"""
        booking = self.env['space.booking'].create({
            'name': 'User 1 Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_1.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # User 1 должен видеть своё бронирование
        bookings = self.env['space.booking'].with_user(self.user_1).search([
            ('id', '=', booking.id)
        ])
        self.assertEqual(len(bookings), 1)


    def test_manager_sees_all_bookings(self):
        """Тест: менеджер видит все бронирования"""
        booking1 = self.env['space.booking'].create({
            'name': 'User 1 Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_1.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        booking2 = self.env['space.booking'].create({
            'name': 'User 2 Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_2.partner_id.id,
            'start_time': self.now + timedelta(hours=3),
            'end_time': self.now + timedelta(hours=4),
        })
        
        # Менеджер видит оба бронирования
        bookings = self.env['space.booking'].with_user(self.manager).search([
            ('id', 'in', [booking1.id, booking2.id])
        ])
        self.assertEqual(len(bookings), 2)

    def test_user_can_read_all_spaces(self):
        """Тест: все пользователи видят все помещения"""
        space = self.env['space'].with_user(self.user_1).search([
            ('id', '=', self.space.id)
        ])
        
        self.assertEqual(len(space), 1)

    def test_user_cannot_delete_booking(self):
        """Тест: пользователь НЕ может удалить бронирование"""
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_1.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        with self.assertRaises(AccessError):
            booking.with_user(self.user_1).unlink()

    def test_manager_can_delete_booking(self):
        """Тест: менеджер может удалить бронирование"""
        booking = self.env['space.booking'].create({
            'name': 'Test Meeting',
            'space_id': self.space.id,
            'partner_id': self.user_1.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # Менеджер может удалить
        booking.with_user(self.manager).unlink()
        self.assertFalse(booking.exists())