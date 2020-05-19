import sqlite3


class DatabaseConnection:
    def __init__(self):
        self.con = sqlite3.connect('marvel.db')

    def store_characters(self, data):
        """ Stores character's id and name to the 'characters' table """
        data.to_sql("characters", self.con, if_exists="append")

    def character_id(self, name):
        """ Queries 'characters' table for an ID using a name """
        cur = self.con.cursor()
        cur.execute(f'SELECT id FROM characters WHERE name = "{name}";')
        id = cur.fetchall()
        if id:
            return id[0][0]

    def store_characters_comics(self, data):
        """
        Stores character's comics' titles to the 'characters_comics' table
        """
        data.to_sql("characters_comics", self.con, if_exists="append")

    def characters_comics(self, id):
        """ Queries 'characters_comics' by ID and returns a list of comics """
        cur = self.con.cursor()
        cur.execute(
            f'SELECT title FROM characters_comics WHERE character_id = {id};')
        comics = cur.fetchall()
        if comics:
            return [comic[0] for comic in comics]

    def is_cached(self, id):
        """ Returns True if character exists in 'characters_comics' table """
        cur = self.con.cursor()

        # determine if table exists
        cur.execute(
            """
            SELECT count(name)
            FROM sqlite_master
            WHERE type='table' AND name='characters_comics'
            """
        )
        if cur.fetchone()[0] != 1:
            return False

        cur.execute(
            f"""
            SELECT character_id
            FROM characters_comics
            WHERE character_id = {id} LIMIT 1;
            """
        )
        comics = cur.fetchall()
        if comics:
            return True

    def close(self):
        """ Closes database connection """
        self.con.close()
