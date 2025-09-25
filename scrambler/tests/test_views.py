from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile


class ViewTests(TestCase):
    def test_upload_flow_redirects_to_result(self):
        client = Client()
        upload = SimpleUploadedFile('test.txt', b'Hello world', content_type='text/plain')
        response = client.post(reverse('upload'), {'file': upload})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('result'))

    def test_result_view_shows_text(self):
        client = Client()
        session = client.session
        session['scrambled_text'] = 'abc'
        session.save()
        response = client.get(reverse('result'))
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'abc', response.content)

    def test_result_view_redirects_if_missing(self):
        client = Client()
        response = client.get(reverse('result'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('upload'))


