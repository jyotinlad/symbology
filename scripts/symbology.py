from random import choice
from string import ascii_uppercase, digits
from cherrypy import expose, quickstart

from database import Database


class Symbology(object):

    # def __init__(self):
    #     self._db = Database()

    @expose
    def index(self):
        return """
        <html>
            <head></head>
            <body>
                <h1>Symbology System</h1>
                <form method="get" action="get">
                    <input type="text" value="Enter Symbol" name="alias" />
                    <button type="submit">Get</button>
                </form>
            </body>
        </html>
        """

    @staticmethod
    def _generate():
        code = "".join(choice(ascii_uppercase + digits) for _ in range(7))
        return f"SYM{code}"

    @expose
    def get(self, alias):
        if not isinstance(alias, str):
            raise ValueError("expected alias as a string")

        alias = alias.upper()

        db = Database()
        recs = db.select("symbols", filters=[{"column": "alias", "operator": "=", "value": alias}])

        # symbol already exists
        if recs:
            return recs[0].get("symbol")

        # generate symbol
        while True:
            symbol = self._generate()
            recs = db.select("symbols", filters=[{"column": "symbol", "operator": "=", "value": symbol}])
            if not recs:
                db.insert("symbols", {"symbol": symbol, "alias": alias})

                return symbol


if __name__ == "__main__":
    quickstart(Symbology())
