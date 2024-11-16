from django.test import TestCase
from django.test import TestCase
from django.utils import timezone
from user.models import User, Group
from bills.models import Bill, Debt


class UserGroupModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            first_name="Иван",
            last_name="Иванович",
            username="Ivan@gmail.com",
            password="1234"
        )
        self.group = Group.objects.create(
            name='Django Developers',
            creator=self.user
        )

        self.user.friends_groups.add(self.group)

    def test_user_first_name(self):
        self.assertEqual(self.user.first_name, "Иван")

    def test_user_last_name(self):
        self.assertEqual(self.user.last_name, "Иванович")

    def test_user_username(self):
        self.assertEqual(self.user.username, "Ivan@gmail.com")

    def test_user_password(self):
        self.assertEqual(self.user.password, "1234")

    def test_user_group_association(self):
        self.assertIn(self.group, self.user.friends_groups.all())

    def test_creator_group(self):
        self.assertEqual(self.group.creator, self.user)


class BillModelTest(TestCase):

    def setUp(self):
        self.user1 = User.objects.create_user(
            username='ivan@example.com',
            first_name='Иван',
            last_name='Иванов',
            password='password123'
        )

        self.group = Group.objects.create(name='Django Developers', creator=self.user1)

        self.bill = Bill.objects.create(
            name='Заем на проект',
            creator=self.user1,
            group=self.group,
            sum_debts=5000,
            expiration_date=timezone.now() + timezone.timedelta(days=30),
            creation_date=timezone.now(),
        )

    def test_bill_creation(self):
        self.assertEqual(self.bill.name, 'Заем на проект')
        self.assertEqual(self.bill.sum_debts, 5000)
        self.assertEqual(self.bill.creator, self.user1)
        self.assertEqual(self.bill.group, self.group)
        self.assertTrue(self.bill.expiration_date > self.bill.creation_date)

    def test_foreign_keys(self):
        self.assertEqual(self.bill.creator.username, 'ivan@example.com')
        self.assertEqual(self.bill.group.name, 'Django Developers')

    def test_bill_sum_debts_positive(self):
        self.assertGreater(self.bill.sum_debts, 0)

    def test_expiration_date(self):
        self.assertTrue(self.bill.expiration_date > self.bill.creation_date)

    def test_delete_bill(self):
        bill_id = self.bill.id
        self.bill.delete()
        with self.assertRaises(Bill.DoesNotExist):
            Bill.objects.get(id=bill_id)


