
# Utilities
import os 
from datetime import datetime as dt
from datetime import timedelta
import pandas as pd
import numpy as np
import json
import sys
import warnings
    
# Suppress Warnings
if not sys.warnoptions:
    warnings.simplefilter("ignore") 

## Dash/Plotly
import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_table
    
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import flask
from flask import Flask, send_file, jsonify
import urllib
from zipfile import ZipFile
import io
import requests

# Initialize dash app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
server = Flask(__name__)
app = dash.Dash(__name__, server = server, external_stylesheets = external_stylesheets)
app.config['suppress_callback_exceptions'] = True
app.css.config.serve_locally = True
app.scripts.config.serve_locally = True

# Read in data
root_dir = "https://afs.stanford.edu/?path=/afs/ir/group/covid_power/WWW/data"
local_dir = "/Users/josebolorinos/Google Drive File Stream/My Drive/Research Stuff/Covid and the Grid/si_app/data"

df_dict = {}
df_names = ['figure1','figure12_sip','table1','figure2','table2','figure3','table3']
df_dict = {df_name: pd.read_csv(os.path.join(local_dir, df_name + '.csv')) for df_name in df_names}

# Format date variables
df_dict['figure1'].loc[:,'date'] = pd.to_datetime(df_dict['figure1']['date'])

# Get geographies for dropdown object
geographies = df_dict['figure1'].geography.unique()

# Layout objects
layoutChildren = [
    html.H1(
        children='Supplemental Data',
        style={
            'textAlign': 'center'   ,
            'font-size':'36px','whiteSpace':'pre'
        }
    ),
    html.Div(children = html.Hr(), style = {'padding-left': '100px', 'padding-right': '100px'}),
    html.Div(
        [
            dcc.Dropdown(
                id = 'geography-dropdown',
                options = [{'label': value, 'value': value} for value in geographies],
                value = 'Australia'
            ),
            html.Div([
                html.A(
                    'Download all data',
                    id = 'download-zip',
                    download = 'covid-data.zip',
                    href = "/download_csv/",
                    target = "_blank",
                    n_clicks = 0, className='button button-primary',
                    style = {'height': '45px', 'width': '282px','font-size': '15px'}
                )],
                style = {'padding': '1px','backgroundColor':'white','textAlign':'right'}
            ),
            html.Div(id = 'test')
        ],
    style = {'width': '20%', 'textAlign':'center', 'padding-left':'15%'}
    ),
    html.Div(
        id = 'figure1-div',
        children = [
            dcc.Graph(id = 'figure1-ci-graph'),
            dcc.Graph(id = 'figure1-time-series-graph'),
            html.Div(
                html.Div(
                    className = 'plot-title-container',
                    children = [
                        html.P(
                            "Fig. 1: ",
                            className ='plot-title-left'
                        ),
                        html.P(
                            "Government restrictions (CI levels) and percent change in mobility, electricity demand, Feb-May 2020",
                            className ='plot-title-right'
                        )
                    ]
                )
    
            )
        ],
        style = {'height': '95%','padding-top':'5%'},

    ),
    html.Div(
        id = 'table1-div',
        style = {
            'width': '50%', 'textAlign':'center', 'padding-left':'15%','padding-right':'35%',
            'height': '95%','padding-top':'5%',
        }
    ),
    html.Div(
        className = 'table-title-container',
        children = [
            html.P(
                "Table 1: ",
                className ='table-title-left'
            ),
            html.P(
                " Ordinary least squares regression model of daily electricity change and government restrictions (CI level), Feb-May 2020",
                className ='table-title-right'
            ),
        ]
    ),
    html.Div(children = html.Hr(), style = {'padding-left': '100px', 'padding-right': '100px'}),
    html.Div(
        id = 'figure2-div',
        className = 'app-header',
        children = [
            dcc.Graph(id = 'figure2-ci-graph'),
            dcc.Graph(id = 'figure2-time-series-graph'),
            html.Div(
                html.Div(
                    className = 'plot-title-container',
                    children = [
                        html.P(
                            "Fig. 2: ",
                            className ='plot-title-left'
                        ),
                        html.P(
                            "Multivariate Adaptive Regression Spline (MARS) model results of daily electricity change and government restrictions (CI level) vs. actual daily electricity change, Feb-May 2020",
                            className ='plot-title-right'
                        )
                    ]
                )
    
            )
        ],
        style = {'height': '95%','padding-top':'5%'}  
    ),
    html.Div(
        id = 'table2-div',
        style = {
            'width': '50%', 'textAlign':'center', 'padding-left':'15%','padding-right':'35%',
            'height': '95%','padding-top':'5%'
        }
    ), 
    html.Div(
        className = 'table-title-container',
        children = [
            html.P(
                "Table 2:",
                className ='table-title-left'
            ),
            html.P(
                "Elasticity coefficients measuring the relationship between changes in workplace, transit, residential, retail/recreation, grocery/pharmacy and parks mobility and changes electricity use, Feb-May 2020.",
                className ='table-title-right'
            ),
        ]
    ),
    html.Div(children = html.Hr(), style = {'padding-left': '100px', 'padding-right': '100px', 'padding-top': '100px'}),
    html.Div(
        children = [
            html.Div(
                id = 'figure3-div',
                children = [
                    dcc.Graph(id = 'figure3-graph'),
                    html.P(
                        "Fig. 3: ",
                        className ='figure-title-left-2col'
                    ),
                    html.P(
                        "Observed daily load shapes for workdays and weekends April 2016-2019 vs. April 2020.",
                        className ='figure-title-right-2col'
                    )
                ],
                style = {'height': '100%', 'padding-left':'8%'},
                className = 'column'
            ),
            html.Div(
                id = 'table3-div',
                style = {'height': '100%','padding-right':'20%','padding-top':'15%'},
                className = 'column'
            )
        ],
        className = 'row'
    ),
    html.Div(children = html.Hr(), style = {'padding-left': '100px', 'padding-right': '100px', 'padding-top': '50px'})  
]

app.layout = html.Div(
    id = 'page-content', 
    children = layoutChildren, 
    style = {'fontFamily':'sans-serif','backgroundColor':'white'}
)   


@app.callback(
    [
        Output('figure1-ci-graph','figure'), 
        Output('figure1-time-series-graph','figure'),
        Output('table1-div','children'),
        Output('figure2-ci-graph','figure'),
        Output('figure2-time-series-graph','figure'),
        Output('table2-div','children'),
        Output('figure3-graph','figure'),
        Output('table3-div','children')
    ],
    [Input('geography-dropdown','value')]
)

def filtered_si_results(geography):

    #================================== Figure 1 ==================================#
    figure1_filtered = df_dict['figure1'].loc[df_dict['figure1'].geography == geography,:]
    figure12_sip_filtered = df_dict['figure12_sip'].loc[df_dict['figure12_sip'].geography == geography,:]

    figure12_ci_plot_data = [
        go.Scatter(
            x = figure12_sip_filtered['date'],
            y = figure12_sip_filtered['SIP'],
            mode = 'lines',
            opacity = 0.8,  
            line_color = 'black',
            name = "CI Level"
        ),
    ]
    figure1_ci_layout = go.Layout({
        'xaxis': {'title': False,'showgrid': False,'visible': False},
        'yaxis': {
            'title': 'CI Level',
            'tickvals': [0,1,2,3],
            'showgrid': False

        },
        'margin': {'l': 200,'r': 200,'t': 20,'b': 20},
        'height': 130,
        'width': 1250,
    })

    figure1_ts_plot_data = [
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['percent_red'],
            mode = 'lines',
            line_color = 'orange',
            name = 'Elect. use chg',
            opacity = 1,
            line = {'dash':'dash'}
        ),
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['percent_red_lower'],
            mode = 'lines',
            line_color = 'yellow',
            opacity = 1,
            showlegend = False
        ),
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['percent_red_upper'],
            mode = 'lines',
            fill = 'tonexty',
            line_color = 'yellow',
            opacity = 1,
            showlegend = False
        ),
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['grocery_pharmacy'],
            mode = 'lines',
            name = 'Grocery/Pharmacy',
            line_color = 'lightgreen'
        ),
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['workplace'],
            mode = 'lines',
            name = 'Workplace',
            line_color = 'darkblue'
        ),
        go.Scatter(
            x = figure1_filtered['date'],
            y = figure1_filtered['residential'],
            mode = 'lines',
            name = 'Residential',
            line_color = 'mediumturquoise'
        )
    ]
    figure1_ts_layout = go.Layout({
        'xaxis': {'title': '', 'showgrid': False},
        'yaxis': {
            'title': '% change',
            'tickformat': ',.0%',
            'showgrid': False
        },
        'margin': {'l': 200,'r': 200,'t': 20,'b': 20},
        'height': 500,
        'width': 1250,
    })
    figure12_ci = {'data': figure12_ci_plot_data,'layout': figure1_ci_layout}
    figure1_ts= {'data': figure1_ts_plot_data,'layout': figure1_ts_layout}
    #================================== Figure 1 ==================================#

    #================================== Table 1 ===================================#
    table1_filtered = df_dict['table1'].loc[df_dict['table1']['country'] == geography,['variable','coefficient','p_value','standard_error']]
    colnames = ['Variable','Coefficient','P-value','Standard Error']
    table1_filtered.columns = colnames
    table1 = dash_table.DataTable(
        id = 'table1',
        columns = [{"name": i, "id": i} for i in table1_filtered.columns],
        data = table1_filtered.to_dict('records'),
        style_cell = {'textAlign': 'left', 'font_size': '16 px'},
        style_as_list_view = True,
    )
    #================================== Table 1 ===================================#

    #================================= Figure 2 ===================================#
    figure2_filtered = df_dict['figure2'].loc[df_dict['figure2'].geography == geography,:]
    figure2_breakpoints = figure2_filtered.loc[figure2_filtered.breakpoint_in_SIP == 1,:]
    # Set shapes for breakpoint lines
    breakpoint_margin = 0.05
    nbreakpoints = figure2_breakpoints.shape[0]
    fig2_shapes = [
        {
            'type':'line',
            'line':{'color':'mediumseagreen','dash':'dash'},
            'yref':'paper','y0':0,'y1':1,
            'xref':'x','x0': figure2_breakpoints.loc[i,'date'], 'x1': figure2_breakpoints.loc[i,'date']
        }\
             for i in figure2_breakpoints.index
    ]

    figure2_ts_plot_data = [
        go.Scatter(
            x = figure2_filtered['date'],
            y = figure2_filtered['percent_red'],
            mode = 'lines',
            line_color = 'cornflowerblue',
            name = 'Elect. use chg',
            opacity = 1
        ),
        go.Scatter(
            x = figure2_filtered['date'],
            y = figure2_filtered['mars_elec'],
            mode = 'lines',
            line_color = 'orange',
            name = 'MARS fit',
            opacity = 1
        ) 
    ]
    figure2_ts_layout = go.Layout({
        'xaxis': {'title': '','showgrid': False},
        'yaxis': {
            'title': '% change elect. demand',
            'tickformat': ',.0%',
            'showgrid': False
        },
        'margin': {'l': 200,'r': 200,'t': 20,'b': 20},
        'height': 500,
        'width': 1250,
        'shapes': fig2_shapes
    })
    figure2_ci_layout = go.Layout({
        'xaxis': {'title': False,'showgrid': False,'visible': False},
        'yaxis': {
            'title': 'CI Level',
            'tickvals': [0,1,2,3],
            'showgrid': False

        },
        'margin': {'l': 200,'r': 200,'t': 20},
        'height': 210,
        'width': 1250
    })


    figure2_ts = {'data': figure2_ts_plot_data,'layout': figure2_ts_layout}
    figure2_ci = {'data': figure12_ci_plot_data,'layout': figure2_ci_layout}
    #================================= Figure 2 ===================================#

    #================================= Table 2 ====================================#    
    table2_filtered = df_dict['table2'].loc[df_dict['table2']['country'] == geography,['mobility_type_desc','coefficient','standard_error','p_value','R2','N']]
    colnames = ['Variable','Coefficient','Standard Error','P-value','R-squared','N']
    table2_filtered.columns = colnames
    table2 = dash_table.DataTable(
        id = 'table2',
        columns = [{"name": i, "id": i} for i in table2_filtered.columns],
        data = table2_filtered.to_dict('records'),
        style_cell = {'textAlign': 'left', 'font_size': '16 px'},
        style_as_list_view = True,
    )
    #================================= Table 2 ====================================#    

    #================================= Figure 3 ===================================#
    figure3_filtered = df_dict['figure3'].loc[df_dict['figure3']['country'] == geography,:]
    figure3_weekend_historical = figure3_filtered.loc[figure3_filtered['Day.type'] == 'weekend - Historic (April 2016-2019)',:]
    figure3_weekday_historical = figure3_filtered.loc[figure3_filtered['Day.type'] == 'workday - Historic (April 2016-2019)',:]
    figure3_weekday_actual     = figure3_filtered.loc[figure3_filtered['Day.type'] == 'workday - April 2020',:]
    hovertemplate = 'Hour: %{x}, Demand: %{y:,.0f}<extra></extra>'
    figure3_plot_data = [
        go.Scatter(
            x = figure3_weekend_historical['hour'],
            y = figure3_weekend_historical['load_median'],
            mode = 'lines',
            line_color = 'cornflowerblue',
            name = 'weekend − Historic (April 2016−2019)',
            line = {'dash':'dash'},
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekend_historical['hour'],
            y = figure3_weekend_historical['load_Q10'],
            line_color='cornflowerblue',
            line = {'dash':'dash'},
            name = 'weekend − Historic (April 2016−2019)',
            showlegend = False,
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekend_historical['hour'],
            y = figure3_weekend_historical['load_Q90'],
            fill = 'tonexty',
            line_color='cornflowerblue',
            line = {'dash':'dash'},
            name = 'weekend − Historic (April 2016−2019)',
            showlegend = False,
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_historical['hour'],
            y = figure3_weekday_historical['load_median'],
            mode = 'lines',
            line_color = 'cornflowerblue',
            name = 'working day − Historic (April 2016−2019)',
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_historical['hour'],
            y = figure3_weekday_historical['load_Q10'],
            line_color = 'cornflowerblue',
            name = 'working day − Historic (April 2016−2019)',            
            opacity = 0.2,
            showlegend = False,
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_historical['hour'],
            y = figure3_weekday_historical['load_Q90'],
            fill = 'tonexty',
            line_color = 'cornflowerblue',
            name = 'working day − Historic (April 2016−2019)',            
            showlegend = False,
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_actual['hour'],
            y = figure3_weekday_actual['load_median'],
            mode = 'lines',
            line_color = 'red',
            name = 'working day − April 2020',
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_actual['hour'],
            y = figure3_weekday_actual['load_Q10'],
            line_color = 'red',
            name = 'working day − April 2020',
            showlegend = False,
            hovertemplate = hovertemplate
        ),
        go.Scatter(
            x = figure3_weekday_actual['hour'],
            y = figure3_weekday_actual['load_Q90'],
            fill = 'tonexty',
            line_color = 'red',
            name = 'working day − April 2020',
            showlegend = False,
            hovertemplate = hovertemplate
        )
    ]
    figure3_layout = go.Layout({
        'xaxis': {'title': 'Hour of day','showgrid': False},
        'yaxis': {
            'title': 'Load (MW)',
            'tickformat': ',d',
            'showgrid': False
        },
        'legend': {'yanchor' : 'top', 'y' : 0.99, 'xanchor' : 'left', 'x' : 0.01, 'bgcolor': 'rgba(255,255,255,0.4)'},
    })
    figure3 = {'data': figure3_plot_data,'layout': figure3_layout}
    #================================= Figure 3 ===================================#

    #================================= Table 3 ====================================# 
    table3_filtered = df_dict['table3'].loc[df_dict['table3'].country == geography, ['type_desc','historic','actual']]
    colnames = ['Load shape measure','April 2016-2019','April 2020']
    table3_filtered.columns = colnames
    table3_table = [dash_table.DataTable(
        id = 'table3',
        columns = [{"name": i, "id": i} for i in table3_filtered.columns],
        data = table3_filtered.to_dict('records'),
        style_cell = {'textAlign': 'left', 'font_size': '16 px'},
        style_as_list_view = True,
    )]
    table3_caption = [
        html.Div(
            className = 'table-title-container-2col',
            style = {'padding-top': '22%'},
            children = [
                html.P(
                    "Table 3:",
                    className ='table-title-left-2col'
                ),
                html.P(
                    "Changes in peak and baseload (MW, timing) for workdays April 2016-2019 vs, April 2020.",
                    className ='table-title-right-2col'
                )
            ]
        )
    ]
    table3 = table3_table + table3_caption
    #================================= Table 3 ====================================# 

    return figure12_ci, figure1_ts, table1, figure2_ci, figure2_ts, table2, figure3, table3


@app.callback(
    Output('download-zip', 'href'), 
    [Input('geography-dropdown','value')]
)

def load_link(value):
    return '/download_csv'

@app.server.route('/download_csv')

def download_csv():

    zip_object = ZipFile('covid-data.zip', 'w')
    for file_name in df_dict:
        data_sub = df_dict[file_name]
        data_sub.to_csv('{}.csv'.format(file_name))
        zip_object.write('{}.csv'.format(file_name))

    zip_object.close()

    return send_file(
        'covid-data.zip',
        attachment_filename = 'covid-data.zip',
        as_attachment = True
    )


if __name__ == '__main__':

    app.run_server(debug = True, host = '0.0.0.0', port = 8080)


