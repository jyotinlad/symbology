from random import choice
from string import ascii_uppercase, digits
from cherrypy import dispatch, expose, quickstart, tools

from database import Database


@expose
class SymbologyWebService(object):

    @staticmethod
    def _generate():
        code = "".join(choice(ascii_uppercase + digits) for _ in range(7))
        return f"SYM{code}"

    @tools.accept(media='text/plain')
    def GET(self, alias):
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

    def POST(self):
        return None

    def PUT(self):
        return None

    def DELETE(self):
        return None


if __name__ == '__main__':
    conf = {
        '/': {
            'request.dispatch': dispatch.MethodDispatcher(),
            'tools.sessions.on': True,
            'tools.response_headers.on': True,
            'tools.response_headers.headers': [('Content-Type', 'text/plain')],
        }
    }
    quickstart(StringGeneratorWebService(), '/', conf)
