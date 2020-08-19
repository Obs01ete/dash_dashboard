import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import numpy as np


class Dashboard:
    def __init__(self):
        claims_df = pd.read_csv("claims_test.csv")
        # print(claims_df)
        # print(claims_df.columns)
        claims_df["CLAIM_SPECIALTY"] = claims_df["CLAIM_SPECIALTY"].str.lower()
        claims_df["CLAIM_SPECIALTY"] = claims_df["CLAIM_SPECIALTY"].apply(
            lambda v: v.strip(" \t") if isinstance(v, str) else v)

        # print(claims_df["SERVICE_CATEGORY"].unique())
        # print(len(claims_df["SERVICE_CATEGORY"].unique()))

        # print(claims_df["CLAIM_SPECIALTY"].unique())
        # print(len(claims_df["CLAIM_SPECIALTY"].unique()))

        # print(claims_df["PAYER"].unique())
        # print(len(claims_df["PAYER"].unique()))

        self.service_categories = claims_df["SERVICE_CATEGORY"].unique().tolist()
        self.payers = claims_df["PAYER"].unique().tolist()
        self.df = claims_df

        self.app = dash.Dash()

        self.category_cl = dcc.Checklist(
            id='category_cl',
            options=[{"label": c, "value": c} for c in self.service_categories],
            value=self.service_categories)

        self.payers_cl = dcc.Checklist(
            id='payers_cl',
            options=[{"label": p, "value": p} for p in self.payers],
            value=self.payers)

        self.months = np.sort(self.df["MONTH"].unique())
        self.index_to_month = {i + 1: str(month) for i, month in enumerate(self.months)}

        self.date_slider = dcc.RangeSlider(
            id='month_slider',
            updatemode='mouseup',
            count=1,
            min=1,
            max=len(self.months),
            step=1,
            value=[1, len(self.months)],
            marks=self.index_to_month,
            pushable=0,
        )

        self.app.layout = html.Div(id="main", children=[
            html.H1(children="My dashboard"),
            html.Br(),
            self.date_slider,
            html.Br(),
            html.Br(),
            self.category_cl,
            html.Br(),
            self.payers_cl,
            dcc.Graph(id="all_claims_graph"),
            dcc.Graph(id="specialty_graph"),
        ])

        self.app.callback(
            [
                Output(component_id="specialty_graph", component_property="figure"),
                Output(component_id="all_claims_graph", component_property="figure"),
            ],
            [
                Input(component_id="category_cl", component_property="value"),
                Input(component_id="payers_cl", component_property="value"),
                Input(component_id="month_slider", component_property="value"),
            ],
        )(self.render)

    def run(self):
        self.app.run_server(debug=False, host='0.0.0.0')

    def render(self, category_cl, payers_cl, month_slider_value):
        min_max_month = [self.months[i-1] for i in month_slider_value]
        df_range = self.df[(self.df["MONTH"] >= min_max_month[0]) & (self.df["MONTH"] <= min_max_month[1])]
        df_cat = df_range[df_range["SERVICE_CATEGORY"].isin(category_cl)]
        df_payers = df_cat[df_cat["PAYER"].isin(payers_cl)]
        # print(df_payers)

        df_all_claims = df_payers.groupby(["SERVICE_CATEGORY", "PAYER"])["PAID_AMOUNT"].sum().reset_index()
        # print(df_all_claims)
        color_discrete_map = {sc: color for sc, color in zip(self.service_categories, px.colors.qualitative.G10)}
        all_claims_fig = px.bar(
            df_all_claims,
            x="PAYER",
            y="PAID_AMOUNT",
            color="SERVICE_CATEGORY",
            barmode="group",
            color_discrete_map=color_discrete_map)

        df_specialty = df_payers.groupby(["CLAIM_SPECIALTY"])["PAID_AMOUNT"].sum().reset_index()
        # print(df_specialty)
        df_specialty_top = df_specialty.sort_values("PAID_AMOUNT", ascending=False).head(50)
        # print(df_specialty_top)
        figure_specialty = px.bar(
            df_specialty_top,
            x="CLAIM_SPECIALTY",
            y="PAID_AMOUNT",
        )

        return figure_specialty, all_claims_fig


def main():
    dashboard = Dashboard()
    dashboard.run()


if __name__ == "__main__":
    main()
