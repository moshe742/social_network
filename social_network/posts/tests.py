from unittest import mock

from django.test import (
    Client,
    TestCase,
)


BASE_URL = 'http://localhost:8000'

SIGNUP = f'{BASE_URL}/api/signup/'
LOGIN = f'{BASE_URL}/api/token/'
POSTS_URL = f'{BASE_URL}/api/posts/'
POST_URL = f'{BASE_URL}/api/posts/1/'
LIKE_URL = f'{BASE_URL}/api/posts/1/like/'
UNLIKE_URL = f'{BASE_URL}/api/posts/1/unlike/'


class PostTestCase(TestCase):
    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def setUp(self, enrich_geo, is_valid_email) -> None:
        self.client = Client()
        is_valid_email.return_value = True
        self.client.post(SIGNUP,
                         {'username': 'moshe', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        login = self.client.post(LOGIN,
                                 {'username': 'moshe', 'password': 'hello'})
        self.token = f"Bearer {login.json()['access']}"

    def test_create_post_success(self):
        post = self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                                HTTP_AUTHORIZATION=self.token)
        self.assertEqual(201, post.status_code)
        self.assertEqual({'id': 1, 'title': 'title', 'body': 'body',
                          'owner': 'moshe', 'likes': []},
                         post.json())

    def test_create_post_post_with_like_doesnt_register_like(self):
        post = self.client.post(POSTS_URL, {'title': 'title', 'body': 'body',
                                       'likes': 1},
                                HTTP_AUTHORIZATION=self.token)
        self.assertEqual(201, post.status_code)
        self.assertEqual({'id': 1, 'title': 'title', 'body': 'body',
                          'owner': 'moshe', 'likes': []},
                         post.json())

    def test_create_post_cant_post_if_not_logged_in(self):
        post = self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'})
        self.assertEqual(401, post.status_code)

    def test_get_posts_success(self):
        post1 = self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                                 HTTP_AUTHORIZATION=self.token)
        first = self.client.get(POSTS_URL, HTTP_AUTHORIZATION=self.token)
        self.assertEqual([post1.json()], first.json())
        post2 = self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                                 HTTP_AUTHORIZATION=self.token)
        second = self.client.get(POSTS_URL, HTTP_AUTHORIZATION=self.token)
        self.assertEqual([post1.json(), post2.json()], second.json())

    def test_get_posts_cant_see_post_if_not_logged_in(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)
        first = self.client.get(POSTS_URL)
        self.assertEqual(401, first.status_code)

    def test_delete_post_success(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)

        delete = self.client.delete(POST_URL, HTTP_AUTHORIZATION=self.token)
        self.assertEqual(204, delete.status_code)

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_delete_post_not_owner_cant_delete(self, is_email_valid, enrich_geo):
        is_email_valid.return_value = True
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)
        self.client.post(SIGNUP,
                         {'username': 'moshe1', 'email': 'moshe1@gmail.com',
                          'password': 'hello'})
        login = self.client.post(LOGIN,
                                 {'username': 'moshe1', 'password': 'hello'})
        token = f"Bearer {login.json()['access']}"
        delete = self.client.delete(POST_URL, HTTP_AUTHORIZATION=token)
        self.assertEqual(403, delete.status_code)

    def test_delete_post_cant_delete_if_not_logged_in(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)

        delete = self.client.delete(POST_URL)
        self.assertEqual(401, delete.status_code)

    def test_patch_post_success(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)
        patch_result = self.client.patch(POST_URL, {'title': 'this is a title'},
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=self.token)
        self.assertEqual(200, patch_result.status_code)
        self.assertEqual({'title': 'this is a title', 'body': 'body', 'id': 1,
                          'likes': [], 'owner': 'moshe'},
                         patch_result.json())

    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def test_patch_post_cant_patch_if_not_owner(self, is_email_valid, enrich_geo):
        is_email_valid.return_value = True
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token)
        self.client.post(SIGNUP,
                         {'username': 'moshe1', 'email': 'moshe1@gmail.com',
                          'password': 'hello'})
        login = self.client.post(LOGIN,
                                 {'username': 'moshe1', 'password': 'hello'})
        token = f"Bearer {login.json()['access']}"
        patch_result = self.client.patch(POST_URL, {'title': 'this is a title'},
                                         content_type='application/json',
                                         HTTP_AUTHORIZATION=token)
        self.assertEqual(403, patch_result.status_code)

    def test_patch_post_cant_patch_if_not_logged_in(self):
        post = self.client.patch(POSTS_URL, {'title': 'title', 'body': 'body'},
                                 content_type='application/json')
        self.assertEqual(401, post.status_code)


class LikeTestCase(TestCase):
    @mock.patch('accounts.data_enrichment.is_valid_email')
    @mock.patch('accounts.data_enrichment.enrich_geo')
    def setUp(self, is_valid_email, enrich_geo) -> None:
        self.client = Client()
        is_valid_email.return_value = True
        self.client.post(SIGNUP,
                         {'username': 'moshe', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        self.client.post(SIGNUP,
                         {'username': 'moshe1', 'email': 'moshe@gmail.com',
                          'password': 'hello'})
        login1 = self.client.post(LOGIN,
                                  {'username': 'moshe', 'password': 'hello'})
        self.token_1 = f"Bearer {login1.json()['access']}"
        login2 = self.client.post(LOGIN,
                                  {'username': 'moshe1', 'password': 'hello'})
        self.token_2 = f"Bearer {login2.json()['access']}"

    def test_like_success(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token_1)

        like = self.client.patch(LIKE_URL, content_type='application/json',
                                 HTTP_AUTHORIZATION=self.token_2)
        self.assertEqual(200, like.status_code)
        self.assertEqual({'likes': [2]}, like.json())

    def test_like_cant_like_your_posts(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token_1)
        like = self.client.patch(LIKE_URL, content_type='application/json',
                                 HTTP_AUTHORIZATION=self.token_1)
        self.assertEqual(403, like.status_code)

    def test_like_cant_like_if_not_logged_in(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token_1)
        like = self.client.patch(LIKE_URL, content_type='application/json')
        self.assertEqual(401, like.status_code)

    def test_unlike_success(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token_1)
        like = self.client.patch(LIKE_URL, content_type='application/json',
                                 HTTP_AUTHORIZATION=self.token_2)

        unlike = self.client.patch(UNLIKE_URL, content_type='application/json',
                                   HTTP_AUTHORIZATION=self.token_2)
        self.assertEqual(200, unlike.status_code)
        self.assertEqual({'likes': []}, unlike.json())

    def test_like_404(self):
        self.client.post(POSTS_URL, {'title': 'title', 'body': 'body'},
                         HTTP_AUTHORIZATION=self.token_1)
        like = self.client.patch('http://localhost:8000/api/posts/10/like/',
                                 content_type='application/json',
                                 HTTP_AUTHORIZATION=self.token_2)
        self.assertEqual(404, like.status_code)
