from sqlalchemy import text


def get_position(db):

    query = """
        SELECT *
        FROM Position
    """

    with db.engine.connect() as connection:
        result = connection.execute(text(query))

        return result.fetchall(), result.keys()
