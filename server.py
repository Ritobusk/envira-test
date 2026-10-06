import json

import pandas as pd
import panel as pn
from tornado.web import RequestHandler

from loss_experience import build_policy_table, load_data, loss_experience

PORT = 5006
POLICY_TABLE = build_policy_table(load_data())


class LossExperienceHandler(RequestHandler):
    def get(self, portfolio_id):
        table = loss_experience(POLICY_TABLE, portfolio_id)
        if table.empty:
            self.set_status(404)
            self.write({"error": f"no policies found for portfolio {portfolio_id}"})
            return
        print(f"loss experience for {portfolio_id}:\n{table.to_string(index=False)}")
        self.set_header("Content-Type", "application/json")
        self.write(json.dumps({"portfolio_id": portfolio_id, "perils": json.loads(table.to_json(orient="records"))}))


def watch_portfolio_input(text_input, dataframe):
    def update_table(event):
        dataframe.value = loss_experience(POLICY_TABLE, event.new.strip())

    text_input.param.watch(update_table, "value")


def index():
    text_input = pn.widgets.TextInput(name="Type portfolio ID")
    dataframe = pn.widgets.DataFrame(pd.DataFrame())
    watch_portfolio_input(text_input, dataframe)
    return pn.Column(
        pn.pane.Markdown("# Envira loss-experience service"),
        text_input,
        dataframe,
    )


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
