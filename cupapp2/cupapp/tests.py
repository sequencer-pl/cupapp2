from django.contrib.auth.models import User
from django.test import TestCase

from cupapp.models import Cup


class AdminTest(TestCase):
    cupName = 'CupOne'
    cupDesc = 'SomeDesc'

    def setUp(self):
        User.objects.create_superuser(username='testuser', email='test@test.com', password='pass')
        Cup.objects.create(name=self.cupName, description=self.cupDesc, form=('cup', 'cup'),
                           owner=User.objects.get(username='testuser'))

    def test_if_proper_cup_name_in_admin(self):
        cup_one = Cup.objects.get(name=self.cupName)
        assert str(cup_one) == f'{self.cupName} ({self.cupDesc})'
