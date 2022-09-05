from django.test import TestCase,Client
from django.contrib.auth.models import User
from core.models import Customer
class MyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('king','king@gmail.com','johnskog111')
        Customer.objects.create(user=self.user,phone=int('09081234564'),verified=True)

    def test_homepage_loads(self):
        home = self.client.get('/')
        self.assertEqual(home.status_code,200,"HomePage loads")

    def test_profile_loads(self):
        self.client.login(username='king',password='johnskog111')
        profile = self.client.get("/profile/")
        self.assertEqual(profile.status_code,200,"Profile loads")


