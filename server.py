import json

import panel as pn
from tornado.web import RequestHandler

PORT = 5006


class LossExperienceHandler(RequestHandler):
    def get(self, portfolio_id):
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"portfolio_id": portfolio_id, "perils": []}))


def index():
    return pn.pane.Markdown("# Envira loss-experience service")


if __name__ == "__main__":
    pn.serve(
        {"/": index},
        port=PORT,
        address="localhost",
        show=False,
        extra_patterns=[
            (r"/portfolios/([^/]+)/loss-experience", LossExperienceHandler),
        ],
    )
