"""
#1 GETTING AND SAVING CHARACTERS
Are you storing the correct number of characters?
Are there duplicates in the stored characters?

"""

import unittest
from unittest.mock import Mock
from unittest.mock import patch

from marvel_client import Marvel


class TestMarvelInstantiation(unittest.TestCase):

    def test_instantiation(self):
        client = Marvel(private_key='123', public_key='abc')
        self.assertEqual(client._private_key, '123')
        self.assertEqual(client._public_key, 'abc')


class TestMarvelMethods(unittest.TestCase):

    def setUp(self):
        self.client = Marvel(private_key='123', public_key='abc')

    def _mock_response(
        self,
        status=200,
        content='CONTENT',
        json_data=None
    ):
        mock_resp = Mock()
        mock_resp.status_code = status
        mock_resp.content = content
        if json_data:
            mock_resp.json = Mock(
                return_value=json_data
            )
        return mock_resp

    @patch('marvel_client.Marvel._generate_hash')
    @patch('marvel_client.time')
    @patch('marvel_client.requests')
    def test_call_api_200(self, mock_requests, mock_time, mock_hash):
        # set up values
        mock_resp = self._mock_response(json_data={'test': 'data'})
        mock_requests.get.return_value = mock_resp
        mock_time.time.return_value = 1000
        mock_hash.return_value = 'hash'

        response = self.client._call_api(endpoint='endpoint', test='value')

        # assert that response returned correctly
        self.assertEqual(response, {'test': 'data'})

        # assert that request was called correctly
        mock_requests.get.assert_called_with(
            'https://gateway.marvel.com/v1/public/endpoint',
            params={
                'ts': str(1000 * 1000),
                'hash': 'hash',
                'apikey': self.client._public_key,
                'test': 'value',
            }
        )

    @patch('marvel_client.Marvel._generate_hash')
    @patch('marvel_client.time')
    @patch('marvel_client.requests')
    def test_call_api_404(self, mock_requests, mock_time, mock_hash):
        # set up values
        mock_resp = self._mock_response(status=404, json_data={'test': 'data'})
        mock_requests.get.return_value = mock_resp
        mock_time.time.return_value = 1000
        mock_hash.return_value = 'hash'

        # assert that error was raised
        self.assertRaises(ValueError, self.client._call_api, 'endpoint')

    @patch('marvel_client.hashlib')
    def test_generate_hash(self, mock_hashlib):
        self.client._generate_hash(ts='123')

        # assert that values are encoded and called correctly
        combined = '123' + self.client._private_key + self.client._public_key
        combined = combined.encode()
        mock_hashlib.md5.assert_called_with(combined)

    @patch('marvel_client.Marvel._call_api')
    def test_all(self, mock_call_api):
        mock_call_api.return_value = 'success'

        # assert that response is returned
        response = self.client.all()
        self.assertEqual(response, 'success')

        # assert that called with correct arguments
        mock_call_api.assert_called_with(
            endpoint='characters',
            offset=0,
            limit=100
        )

        # assert that called offset when provided
        self.client.all(offset=22)
        mock_call_api.assert_called_with(
            endpoint='characters',
            offset=22,
            limit=100
        )

    @patch('marvel_client.Marvel._call_api')
    def test_character(self, mock_call_api):
        mock_call_api.return_value = 'success'

        # assert that response is returned
        response = self.client.character(id=1)
        self.assertEqual(response, 'success')

        # assert that called with correct arguments
        mock_call_api.assert_called_with(
            endpoint='characters/1',
            offset=0,
            limit=100
        )

        # assert that called offset when provided
        self.client.character(id=1, offset=22)
        mock_call_api.assert_called_with(
            endpoint='characters/1',
            offset=22,
            limit=100
        )

    @patch('marvel_client.Marvel._call_api')
    def test_character_comics(self, mock_call_api):
        mock_call_api.return_value = 'success'

        # assert that response is returned
        response = self.client.character_comics(id=1)
        self.assertEqual(response, 'success')

        # assert that called with correct arguments
        mock_call_api.assert_called_with(
            endpoint='characters/1/comics',
            offset=0,
            limit=100
        )

        # assert that called offset when provided
        self.client.character_comics(id=1, offset=22)
        mock_call_api.assert_called_with(
            endpoint='characters/1/comics',
            offset=22,
            limit=100
        )


if __name__ == '__main__':
    unittest.main()
