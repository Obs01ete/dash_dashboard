import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px


def main():
    df = pd.DataFrame(data=[
        ["Moscow", 2019, 10_000_000],
        ["Moscow", 2020, 11_000_000],
        ["Nizhny Novgorod", 2019, 1_300_000],
        ["Nizhny Novgorod", 2020, 1_100_000],
    ], columns=["name", "year", "population"])
    df["year"] = df["year"].astype(str)
    cities = df["name"].unique().tolist()

    app = dash.Dash()

    app.layout = html.Div(id="main", children=[
        html.H1(children="Dmitrii's dashboard"),
        dcc.Checklist(id='cities_cb',
                      options=[{"label": c, "value": c} for c in cities],
                      value=cities),
        dcc.Graph(id="graph")
    ])

    @app.callback(
        Output(component_id="graph", component_property="figure"),
        [Input(component_id="cities_cb", component_property="value")],
    )
    def cities_cb_callback(city_options):
        print(city_options)
        df_selected = df[df["name"].isin(city_options)]
        print(df_selected)
        figure = px.bar(df_selected, x="name", y="population", color="year", barmode="group", width=800)
        return figure

    app.run_server(debug=True)


if __name__ == "__main__":
    main()
