import os

import pandas as pd
from dotenv import load_dotenv

from marvel_client import Marvel
from db import DatabaseConnection

load_dotenv()

PUBLIC_KEY = os.getenv("PUBLIC_KEY")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")


def store_characters(client, db, offset=0):
    """
    Recursively stores all characters to database using Marvel client
    """
    characters = client.all(offset=offset)
    df = pd.DataFrame(characters['data']['results'])
    df = df[['name', 'id']]
    db.store_characters(df)
    next_offset = characters['data']['offset'] + characters['data']['count']
    if next_offset < characters['data']['total']:
        store_characters(client=client, db=db, offset=next_offset)
    else:
        db.close()


class CharacterFinder:
    def __init__(self, name):
        self._client = Marvel(public_key=PUBLIC_KEY, private_key=PRIVATE_KEY)
        self._db = DatabaseConnection()
        self.name = name

    def find(self):
        id = self._db.character_id(self.name)

        if id:
            self.id = id
            self._get_attributes()

        # raise error if no match is found for provided name
        else:
            raise ValueError(f'{self.name} is not a Marvel Character.')

    def _get_attributes(self):
        """
        Sets character's attributes retrieved using Marvel client
        """
        response = self._client.character(id=self.id)
        results = response['data']['results'][0]

        self.description = results['description']
        self.modified = results['modified']
        self.urls = results['urls']
        self.thumbnail = results['thumbnail']

        if not self._db.is_cached(self.id):
            self._get_comics()
        self.comics = self._db.characters_comics(self.id)

    def _get_comics(self, offset=0):
        """
        Recursively stores character's comics using Marvel client
        """
        comics = self._client.character_comics(id=self.id, offset=offset)
        df = pd.DataFrame(comics['data']['results'])
        df = df[['title']]
        df['character_id'] = self.id
        self._db.store_characters_comics(df)
        next_offset = comics['data']['offset'] + comics['data']['count']
        if next_offset < comics['data']['total']:
            self._get_comics(offset=next_offset)

    def overlaps_with(self, name):
        """
        Returns overlapping comics between two characters
        """
        overlap = CharacterFinder(name)
        overlap.find()
        # return intersection of each character's comics list
        return list(set(self.comics) & set(overlap.comics))


def main():

    print("Question 1 -> Store Characters To File")

    client = Marvel(public_key=PUBLIC_KEY, private_key=PRIVATE_KEY)
    db = DatabaseConnection()

    print('Storing characters to SQLite database...')
    store_characters(client=client, db=db)

    print("Question 2-4 -> Use CharacterFinder Class to Find Overlapping Comics")

    emma = CharacterFinder('Emma Frost')
    emma.find()
    comics = emma.overlaps_with('Storm')

    print(f'Emma Frost and Storm overlap in {len(comics)} comics.')
    # answer: 96 comics


if __name__ == '__main__':
    main()
