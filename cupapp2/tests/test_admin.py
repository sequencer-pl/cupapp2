from django.contrib.auth.models import User
from django.test import TestCase

from cupapp.models import Tournament


class AdminTest(TestCase):
    cupName = 'CupOne'
    cupDesc = 'SomeDesc'

    def setUp(self):
        User.objects.create_superuser(username='testuser', email='test@test.com', password='pass')
        Tournament.objects.create(name=self.cupName, description=self.cupDesc, form=('cup', 'cup'),
                                  owner=User.objects.get(username='testuser'))

    def test_if_proper_cup_name_in_admin(self):
        cup_one = Tournament.objects.get(name=self.cupName)
        self.assertEqual(str(cup_one), f'{self.cupName}')
