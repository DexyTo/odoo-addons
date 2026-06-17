from odoo.tests import TransactionCase
from odoo.exceptions import AccessError
from datetime import datetime, timedelta


class TestBookingSecurity(TransactionCase):

    @classmethod
    def setUp(cls):
        super(TestBookingSecurity, cls).setUpClass()
        
        cls.location = cls.env['meeting.room.location'].create({
            'floor': 1,
            'section': 'A',
        })
        
        cls.room = cls.env['meeting.room'].create({
            'name': 'Тестовая комната',
            'capacity': 10,
            'location_id': cls.location.id,
        })
        
        cls.group_manager = cls.env.ref('meeting_room_booking.group_meeting_room_manager')
        cls.group_user = cls.env.ref('base.group_user')
        
        cls.user_regular = cls.env['res.users'].create({
            'name': 'Обычный пользователь',
            'login': 'user@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        
        cls.user_manager = cls.env['res.users'].create({
            'name': 'Менеджер',
            'login': 'manager@test.com',
            'group_ids': [(6, 0, [cls.group_manager.id])],
        })
        
        cls.user_other = cls.env['res.users'].create({
            'name': 'Другой пользователь',
            'login': 'other@test.com',
            'group_ids': [(6, 0, [cls.group_user.id])],
        })
        
        cls.start_time = datetime.now() + timedelta(hours=1)
        cls.end_time = cls.start_time + timedelta(hours=2)

    def test_01_user_can_create_own_booking(self):
        """Тест: обычный пользователь может создать своё бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Моё бронирование',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        self.assertTrue(booking.id, "Пользователь должен создать бронирование")

    def test_02_user_can_edit_own_booking(self):
        """Тест: пользователь может редактировать своё бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Моё бронирование',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # Редактируем
        booking.with_user(self.user_regular).write({'name': 'Изменённое название'})
        self.assertEqual(booking.name, 'Изменённое название')

    def test_03_user_cannot_edit_other_booking(self):
        """Тест: пользователь НЕ может редактировать чужое бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Бронирование User Regular',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        with self.assertRaises(AccessError, msg="Пользователь не должен редактировать чужое бронирование"):
            booking.with_user(self.user_other).write({'name': 'Попытка изменить'})

    def test_04_user_cannot_delete_booking(self):
        """Тест: обычный пользователь НЕ может удалять бронирования"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Тест удаления',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # Пытаемся удалить своё бронирование
        with self.assertRaises(AccessError, msg="Обычный пользователь не может удалять бронирования"):
            booking.with_user(self.user_regular).unlink()

    def test_05_user_can_cancel_own_booking(self):
        """Тест: пользователь может отменить своё бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Тест отмены',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        booking.with_user(self.user_regular).action_cancel()
        self.assertEqual(booking.state, 'cancelled', "Пользователь должен отменить своё бронирование")

    def test_06_user_cannot_cancel_other_booking(self):
        """Тест: пользователь НЕ может отменить чужое бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Бронирование Regular',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
            'state': 'active',
        })
        
        # Пытаемся отменить от другого пользователя
        with self.assertRaises(AccessError, msg="Пользователь не может отменить чужое бронирование"):
            booking.with_user(self.user_other).action_cancel()

    def test_07_manager_can_edit_any_booking(self):
        """Тест: менеджер может редактировать любое бронирование"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Бронирование пользователя',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # Менеджер редактирует чужое бронирование
        booking.with_user(self.user_manager).write({'name': 'Изменено менеджером'})
        self.assertEqual(booking.name, 'Изменено менеджером', "Менеджер должен редактировать любое бронирование")

    def test_08_manager_can_delete_booking(self):
        """Тест: менеджер может удалять бронирования"""
        booking = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Тест удаления менеджером',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        booking_id = booking.id
        
        booking.with_user(self.user_manager).unlink()

        exists = self.env['room.booking'].search([('id', '=', booking_id)])
        self.assertFalse(exists, "Бронирование должно быть удалено")

    def test_09_user_can_read_all_bookings(self):
        """Тест: все пользователи видят все бронирования"""
        # Создаём бронирование от regular
        booking1 = self.env['room.booking'].with_user(self.user_regular).create({
            'name': 'Бронирование 1',
            'room_id': self.room.id,
            'partner_id': self.user_regular.partner_id.id,
            'start_time': self.start_time,
            'end_time': self.end_time,
        })
        
        # Создаём бронирование от other
        booking2 = self.env['room.booking'].with_user(self.user_other).create({
            'name': 'Бронирование 2',
            'room_id': self.room.id,
            'partner_id': self.user_other.partner_id.id,
            'start_time': self.start_time + timedelta(hours=3),
            'end_time': self.end_time + timedelta(hours=3),
        })
        
        bookings = self.env['room.booking'].with_user(self.user_regular).search([])
        self.assertIn(booking1.id, bookings.ids, "Должен видеть своё бронирование")
        self.assertIn(booking2.id, bookings.ids, "Должен видеть чужое бронирование")

    def test_10_user_cannot_manage_rooms(self):
        """Тест: обычный пользователь НЕ может управлять комнатами"""
        with self.assertRaises(AccessError, msg="Пользователь не должен создавать комнаты"):
            self.env['meeting.room'].with_user(self.user_regular).create({
                'name': 'Новая комната',
                'capacity': 5,
                'location_id': self.location.id,
            })

    def test_11_manager_can_manage_rooms(self):
        """Тест: менеджер может управлять комнатами"""
        room = self.env['meeting.room'].with_user(self.user_manager).create({
            'name': 'Комната от менеджера',
            'capacity': 15,
            'location_id': self.location.id,
        })
        
        self.assertTrue(room.id, "Менеджер должен создать комнату")
        
        room.with_user(self.user_manager).write({'capacity': 20})
        self.assertEqual(room.capacity, 20)

    def test_12_user_cannot_manage_locations(self):
        """Тест: обычный пользователь НЕ может управлять локациями"""
        with self.assertRaises(AccessError, msg="Пользователь не должен создавать локации"):
            self.env['meeting.room.location'].with_user(self.user_regular).create({
                'floor': 5,
                'section': 'Z',
            })

    def test_13_manager_can_manage_locations(self):
        """Тест: менеджер может управлять локациями"""
        location = self.env['meeting.room.location'].with_user(self.user_manager).create({
            'floor': 3,
            'section': 'B',
        })
        
        self.assertTrue(location.id, "Менеджер должен создать локацию")