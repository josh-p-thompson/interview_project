import unittest
from unittest.mock import Mock
from unittest.mock import patch
import json
import pandas as pd

import marvel
from marvel import CharacterFinder


class TestStoreCharactersMethod(unittest.TestCase):

    def test_store_characters_recursion(self):
        # mock API call using test data
        with open('test_data/all.json', 'r') as file:
            all_response = json.load(file)
        with open('test_data/all_final.json', 'r') as file:
            final_response = json.load(file)

        mock_client = Mock()
        mock_client.all.side_effect = [all_response, final_response]
        mock_db = Mock()
        marvel.store_characters(client=mock_client, db=mock_db)

        # recursion should cause client to call twice
        self.assertEqual(mock_client.all.call_count, 2)

        # confirm correct data was passed to database
        df = pd.DataFrame(final_response['data']['results'])[['name', 'id']]
        mock_db.store_characters.has_calls(df)


class TestCharacterFinder(unittest.TestCase):

    @patch('marvel.Marvel')
    @patch('marvel.DatabaseConnection')
    def setUp(self, mock_db, mock_marvel):
        self.character_finder = CharacterFinder('name')

    def test_name_attribute(self):
        self.assertEqual(self.character_finder.name, 'name')

    def test_find_no_match(self):
        self.character_finder._db.character_id.return_value = None
        self.assertRaises(ValueError, self.character_finder.find)

    @patch('marvel.CharacterFinder._get_attributes')
    def test_find_match(self, mock_attributes):
        self.character_finder._db.character_id.return_value = 1
        self.character_finder.find()
        self.assertTrue(mock_attributes.called)
        self.assertEqual(self.character_finder.id, 1)

    @patch('marvel.CharacterFinder._get_comics')
    def test_get_attributes_assignments(self, mock_comics):
        with open('test_data/character.json', 'r') as file:
            response = json.load(file)
        self.character_finder._client.character.return_value = response
        self.character_finder._db.characters_comics.return_value = [
            'a', 'b', 'c'
        ]
        self.character_finder.id = 1

        self.character_finder._get_attributes()

        # test that attributes are set correctly
        self.assertEqual(
            self.character_finder.description,
            response['data']['results'][0]['description']
        )
        self.assertEqual(
            self.character_finder.modified,
            response['data']['results'][0]['modified']
        )
        self.assertEqual(
            self.character_finder.urls,
            response['data']['results'][0]['urls']
        )
        self.assertEqual(
            self.character_finder.thumbnail,
            response['data']['results'][0]['thumbnail']
        )
        self.assertEqual(
            self.character_finder.comics,
            ['a', 'b', 'c']
        )

    @patch('marvel.CharacterFinder._get_comics')
    def test_get_attributes_is_cached(self, mock_comics):
        with open('test_data/character.json', 'r') as file:
            response = json.load(file)
        self.character_finder._client.character.return_value = response
        self.character_finder._db.characters_comics.return_value = [
            'a', 'b', 'c'
        ]
        self.character_finder.id = 1
        self.character_finder._db.is_cached.return_value = True

        self.character_finder._get_attributes()

        # test that cache prevented _get_comics() from being called
        self.assertFalse(mock_comics.called)

    @patch('marvel.CharacterFinder._get_comics')
    def test_get_attributes_not_cached(self, mock_comics):
        with open('test_data/character.json', 'r') as file:
            response = json.load(file)
        self.character_finder._client.character.return_value = response
        self.character_finder._db.characters_comics.return_value = [
            'a', 'b', 'c'
        ]
        self.character_finder.id = 1
        self.character_finder._db.is_cached.return_value = False

        self.character_finder._get_attributes()

        # test that cache prevented _get_comics() from being called
        self.assertTrue(mock_comics.called)

    def test_get_comics(self):
        with open('test_data/character_comics.json', 'r') as file:
            response = json.load(file)
        self.character_finder._client.character_comics.return_value = response
        self.character_finder.id = 1

        self.character_finder._get_comics()

        # assert that correct data was passed to database
        df = pd.DataFrame(response['data']['results'])[['title']]
        df['character_id'] = 1
        self.character_finder._db.store_characters_comics.has_calls(df)

    @patch('marvel.CharacterFinder')
    def test_overlaps_with(self, mock_character):
        self.character_finder.comics = ['a', 'b', 'c']
        overlap_comics = Mock()
        overlap_comics.comics = ['d', 'b', 'c']
        mock_character.return_value = overlap_comics

        result = self.character_finder.overlaps_with('other')
        self.assertEqual(set(result), set(['b', 'c']))


if __name__ == '__main__':
    unittest.main()
