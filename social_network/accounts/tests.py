from unittest import mock

from django.test import (
    Client,
    TestCase,
)


BASE_URL = 'http://localhost:8000'

SIGNUP = f'{BASE_URL}/api/signup/'
LOGIN = f'{BASE_URL}/api/token/'
USER_DATA = f'{BASE_URL}/api/user_data/1/'


class AccountTestCase(TestCase):
    def setUp(self) -> None:
        self.client = Client()

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_signup_success_valid_email(self, is_valid_email, enrich_geo):
        is_valid_email.return_value = True
        res = self.client.post(SIGNUP,
                               {'username': 'moshe', 'email': 'moshe@gmail.com',
                                'password': 'hello'})
        self.assertEqual(201, res.status_code)

        expected_data = {
            'id': 1,
            'username': 'moshe',
            'email': 'moshe@gmail.com',
        }
        self.assertEqual(expected_data, res.json())

    @mock.patch('accounts.data_enrichment.is_valid_email')
    def test_signup_fail_invalid_email(self, is_valid_email):
        is_valid_email.return_value = False
        res = self.client.post(SIGNUP,
                               {'username': 'moshe', 'email': 'moshe@gmail',
                                'password': 'hello'})
        self.assertEqual(400, res.status_code)
        self.assertEqual({'error': 'The email format is not valid'}, res.json())

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_login_success(self, is_valid_email, enrich_geo):
        is_valid_email.return_value = True
        self.client.post(SIGNUP,
                         {'username': 'moshe', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        res = self.client.post(LOGIN,
                               {'username': 'moshe', 'password': 'hello'})
        res_json = res.json()

        self.assertEqual(200, res.status_code)
        self.assertIn('access', res_json.keys())
        self.assertIn('refresh', res_json.keys())

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_login_fail(self, is_valid_email, enrich_geo):
        is_valid_email.return_value = True
        self.client.post(SIGNUP,
                         {'username': 'moshe', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        res = self.client.post(LOGIN,
                               {'username': 'moshe', 'password': 'hello world'})

        self.assertEqual(401, res.status_code)
        self.assertEqual({
            'detail': 'No active account found with the given credentials'
        }, res.json())

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_get_user_data(self, is_valid_email, enrich_geo):
        is_valid_email.return_value = True
        self.client.post(SIGNUP,
                         {'username': 'moshe', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        res = self.client.post(LOGIN,
                               {'username': 'moshe', 'password': 'hello'})
        access_token = res.json()['access']
        user_data = self.client.get(USER_DATA,
                                    HTTP_AUTHORIZATION=f'Bearer {access_token}')
        user_json = user_data.json()
        self.assertEqual(200, user_data.status_code)
        self.assertEqual(user_json['username'], 'moshe')
        self.assertEqual(user_json['email'], 'moshe@gmail.com')
