import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import plotly.graph_objects as go
import dash_table

import pandas as pd
import time

df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/solar.csv')

data = pd.read_csv('tests.csv')
data['REQUESTED_DATE_TIME'] = pd.to_datetime(data['REQUESTED_DATE_TIME'])
data['RESULT'] = data['RESULT'].astype(str)
data = data[data['RESULT'].apply(lambda x: x.isdigit())]
data['RESULT'] = data['RESULT'].astype(float)
data = data[(~data['RESULT'].isna()) & (~data['UNITS'].isna())]

outcome = pd.read_csv('outcome.txt', sep='\t', encoding='gb2312')
outcome['DIAGNOSIS_DATE'] = pd.to_datetime(outcome['DIAGNOSIS_DATE'])
outcome = outcome[~outcome['TREAT_RESULT'].isna()]
last_outcome = outcome.groupby('PKEY')['DIAGNOSIS_DATE'].idxmax()
outcome = outcome[outcome.index.isin(last_outcome)]

outcome_dashboard_columns = ['PKEY', 'DIAGNOSIS_TYPE', 'TREAT_RESULT', 'DIAGNOSIS_DATE']

app = dash.Dash(__name__)

params = [
    'Weight', 'Torque', 'Width', 'Height',
    'Efficiency', 'Power', 'Displacement'
]


def get_options(unique_values):
    dict_list = []
    for i in unique_values:
        dict_list.append({'label': i, 'value': i})

    return dict_list


controls = dbc.Card(
    [
        dbc.FormGroup(
            [
                dbc.Label("Select a hospital"),
                dcc.Dropdown(
                    id="hospitalselector",

                    options=get_options(data["HCODE"].unique()),
                    multi=False,
                    searchable=True,
                    placeholder="Select a hospital",
                    style={"backgroundColor": "#1E1E1E", 'color': 'white'},
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a patient"),
                dcc.Dropdown(
                    id="patientselector",
                    multi=False,
                    options=[],
                    style={"backgroundColor": "#1E1E1E"},
                    searchable=True,
                    placeholder="Select a patient",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a visit"),
                dcc.Dropdown(
                    id="visitIdselector",
                    multi=False,
                    options=[],
                    style={"backgroundColor": "#1E1E1E"},
                    searchable=True,
                    placeholder="Select a visit",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a subject"),
                dcc.Dropdown(
                    id="subjectselector",
                    multi=False,
                    options=[],
                    style={"backgroundColor": "#1E1E1E"},
                    searchable=True,
                    placeholder="Select a subject",
                ),
            ]
        ),
        dbc.FormGroup(
            [
                dbc.Label("Select a report"),
                dcc.Dropdown(
                    id="reportselector",
                    multi=False,
                    options=[],
                    style={"backgroundColor": "#1E1E1E"},
                    searchable=True,
                    placeholder="Select a report",
                ),
            ]
        ),
    ],
    body=True,
)
graph = html.Div(

    children=[

        dcc.Loading(
            id="loading-1",
            children=[
                html.Div([html.Div(id="loading-output-1")]),
                dcc.Graph(
                    id="timeseries",
                    config={"displayModeBar": False},
                    animate=False,
                ),
            ],
            type="default",
        ),
    ],
)
table = html.Div(
        children=[
        dash_table.DataTable(
            id='table',
            columns=[{"name": i, "id": i} for i in outcome_dashboard_columns],
            data=[],
            style_header={'backgroundColor': 'rgb(30, 30, 30)'},
            style_cell={
                'backgroundColor': 'rgb(50, 50, 50)',
                'color': 'white'
            }
        )
    ]
)
app.layout = dbc.Container(
    [
        html.H1("Patient Visualization"),
        html.Hr(),
        dbc.Row(graph),

        dbc.Row(
            [
                dbc.Col(table, width={"size": 7, "order":"last"}),
                dbc.Col(controls, width={"size": 6, "order": 1})

            ]
        )
    ], fluid=True
)


@app.callback(dash.dependencies.Output("table", "data"),
              dash.dependencies.Input("patientselector", 'value'))
def generate_table(PKEY):
    if type(PKEY) == str:
        return outcome[outcome['PKEY'] == PKEY][['PKEY', 'DIAGNOSIS_TYPE', 'TREAT_RESULT',
                                             'DIAGNOSIS_DATE']].to_dict('records')
    else:
        return []


@app.callback(dash.dependencies.Output("loading-output-1", "children"),
              dash.dependencies.Input("loading-1", 'value'))
def input_triggers_spinner(value):
    time.sleep(2)
    return 'shenstan1@gmail.com'


@app.callback(
    dash.dependencies.Output('patientselector', 'options'),
    [dash.dependencies.Input('hospitalselector', 'value')])
def search_patient_options(value):
    if type(value) == str:
        slice = data[data['HCODE'] == value]
        return get_options(slice['PKEY'].unique())
    else:

        return []


@app.callback(
    dash.dependencies.Output('visitIdselector', 'options'),
    dash.dependencies.Input('hospitalselector', 'value'),
    dash.dependencies.Input('patientselector', 'value'))
def search_visitId_options(hospID, patientId):
    if type(hospID) == str:
        slice = data[(data['HCODE'] == hospID) & (data['PKEY'] == patientId)]
        return get_options(slice['VISIT_ID'].unique())
    else:

        return []


@app.callback(
    dash.dependencies.Output('subjectselector', 'options'),
    dash.dependencies.Input('hospitalselector', 'value'),
    dash.dependencies.Input('patientselector', 'value'),
    dash.dependencies.Input('visitIdselector', 'value'))
def search_visitId_options(hospID, patientId, visitId):
    if type(hospID) == str:
        slice = data[(data['HCODE'] == hospID) & (data['PKEY'] == patientId) & (data['VISIT_ID'] == visitId)]
        return get_options(slice['SUBJECT'].unique())
    else:

        return []


@app.callback(
    dash.dependencies.Output('reportselector', 'options'),
    dash.dependencies.Input('hospitalselector', 'value'),
    dash.dependencies.Input('patientselector', 'value'),
    dash.dependencies.Input('visitIdselector', 'value'),
    dash.dependencies.Input('subjectselector', 'value'))
def search_visitId_options(hospID, patientId, visitId, subjectId):
    if type(hospID) == str:
        slice = data[(data['HCODE'] == hospID) & (data['PKEY'] == patientId) & (data['VISIT_ID'] == visitId)
                     & (data['SUBJECT'] == subjectId)]
        return get_options(slice['REPORT_ITEM_NAME'].unique())
    else:

        return []


@app.callback(
    dash.dependencies.Output('timeseries', 'figure'),
    [dash.dependencies.Input('hospitalselector', 'value'),
     dash.dependencies.Input('patientselector', 'value'),
     dash.dependencies.Input('visitIdselector', 'value'),
     dash.dependencies.Input('subjectselector', 'value'),
     dash.dependencies.Input('reportselector', 'value')])
def search_visitId_options(hospID, patientId, visitId, subjectId, reportId):
    if type(reportId) == str:

        d = data[(data['HCODE'] == hospID) & (data['PKEY'] == patientId) & (data['VISIT_ID'] == visitId)
                 & (data['SUBJECT'] == subjectId) & (data['REPORT_ITEM_NAME'] == reportId)].sort_values(
            'REQUESTED_DATE_TIME')
        if d.shape[0] == 0:
            pass
        else:
            graph = go.Scatter(x=d['REQUESTED_DATE_TIME'],
                               y=d['RESULT'].astype(float),
                               mode='lines+markers',
                               opacity=0.7)

            traces = [[graph]]
            indata = [val for sublist in traces for val in sublist]
            figure = {'data': indata,
                      'layout': go.Layout(
                          colorway=['#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                          template='plotly_dark',
                          paper_bgcolor='rgba(0, 0, 0, 0)',
                          plot_bgcolor='rgba(0, 0, 0, 0)',
                          hovermode='x',
                          autosize=True,
                          title={'text': reportId, 'font': {'color': 'white'}, 'x': 0.5},
                          xaxis={'range': [d['REQUESTED_DATE_TIME'].min() - pd.DateOffset(1),
                                           d['REQUESTED_DATE_TIME'].max() + pd.DateOffset(1)]},
                          yaxis={'title': d['UNITS'].tolist()[0],
                                 'range': [d['RESULT'].min() - d['RESULT'].mean()/10,
                                           d['RESULT'].max()+d['RESULT'].mean()/10]},
                        transition={
                'duration': 1000,
                'easing': 'cubic-in-out'
            }
                      ),
                      }
            return figure

    return {'data': [],
            'layout': go.Layout(
                colorway=['#FF4F00', '#375CB1', '#FF7400', '#FFF400', '#FF0056'],
                template='plotly_dark',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                plot_bgcolor='rgba(0, 0, 0, 0)',
                hovermode='x',
                autosize=True,
                transition={
                    'duration': 1000,
                    'easing': 'cubic-in-out'
                }
            ),
            }


# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
