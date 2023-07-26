from dash import Dash, html, dcc, Input, Output, callback
import pandas as pd
import plotly.express as px
import scipy.stats as stats
import plotly.io as po
import plotly.graph_objs as go

# data load
mydataset ='https://raw.githubusercontent.com/lhshs/mydataset/main/genia/2307_dashboard/Indicator18_22.csv'
boxstrip_df = 'https://raw.githubusercontent.com/lhshs/mydataset/main/genia/2307_dashboard/boxsstrip.csv'
df = pd.read_csv(mydataset)
df_boxsstrip = pd.read_csv(boxstrip_df)#.set_index('지역')

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# Dropdown options setup
dropdown_options = [{'label': col, 'value': col} for col in df_boxsstrip.columns]

app.layout = html.Div([
                html.Div([
                    # Dropdown1
                    html.Div([
                        dcc.Dropdown(
                            df['Indicator Name'].unique(),
                            '사교육비',
                            id='crossfilter-xaxis-column',),
                        dcc.RadioItems(
                            ['Linear', 'Log'],
                            'Linear',
                            id='crossfilter-xaxis-type',
                            labelStyle={'display': 'inline-block', 'marginTop': '5px'})
                            ],
                    style={'width': '49%', 'display': 'inline-block'}),
                    # Dropdown2
                    html.Div([
                        dcc.Dropdown(
                            df['Indicator Name'].unique(),
                            '특목고진학률',
                            id='crossfilter-yaxis-column'),
                        dcc.RadioItems(
                            ['Linear', 'Log'],
                            'Linear',
                            id='crossfilter-yaxis-type',
                            labelStyle={'display': 'inline-block', 'marginTop': '5px'})
                            ], 
                        style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
                        ], 
                    style={'padding': '5px 5px'}
                ),
                    # graph 1
                    html.Div([
                        dcc.Graph(
                            id='crossfilter-indicator-scatter',
                            hoverData={'points': [{'customdata': '서울'}]})
                            ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),

                    # graph 2
                    html.Div([
                        dcc.Graph(id='x-time-series'),
                        dcc.Graph(id='y-time-series'),
                    ], style={'display': 'inline-block', 'width': '49%'}),

                    # slider
                    html.Div(dcc.Slider(
                        df['year'].min(),
                        df['year'].max(),
                        step=None,
                        id='crossfilter-year--slider',
                        value=df['year'].max(),
                        marks={str(year): str(year) for year in df['year'].unique()}
                                        ), 
                        style={'width': '49%', 'padding': '0px 20px 20px 20px'}),
                    # korea map
                    html.Iframe(
                                src="assets/map_year.html",
                                style={"height": "500px", "width": "100%"}),
                    # box plot
                    html.Div([
                        dcc.Dropdown(
                            id='column-dropdown',
                            options=dropdown_options,
                            value=df_boxsstrip.columns[11],  # Set the default value
                            style={'width': '50%'}
                        ),
                        dcc.Graph(id='box-plot')]),
])


@callback(
    Output('crossfilter-indicator-scatter', 'figure'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'),
    Input('crossfilter-yaxis-type', 'value'),
    Input('crossfilter-year--slider', 'value'))

def update_graph(xaxis_column_name, yaxis_column_name,
                 xaxis_type, yaxis_type,
                 year_value):
    dff = df[df['year'] == year_value]

    fig = px.scatter(x=dff[dff['Indicator Name'] == xaxis_column_name]['value'],
                     y=dff[dff['Indicator Name'] == yaxis_column_name]['value'],
                     hover_name=dff[dff['Indicator Name'] == yaxis_column_name]['지역'],
                     trendline = 'ols'
            )
    
    title1 = "statistic : " + str(stats.spearmanr(dff[dff['Indicator Name'] == xaxis_column_name]['value'],
                           dff[dff['Indicator Name'] == yaxis_column_name]['value'])[0])
    
    title2 = "pvalue : " + str(stats.spearmanr(dff[dff['Indicator Name'] == xaxis_column_name]['value'],
                       dff[dff['Indicator Name'] == yaxis_column_name]['value'])[1])
    
    fig.add_annotation(x=0, y=0.95, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       font=dict(family="Malgun Gothic", size=14, color="#000000"),
                       bordercolor="#c7c7c7", borderwidth=2,
                       borderpad=4, bgcolor="#F78181",
                       opacity=0.7,
                       text=title1)
    
    fig.add_annotation(x=0, y=0.875, xanchor='left', yanchor='bottom',
                   xref='paper', yref='paper', showarrow=False, align='right',
                   font=dict(family="Malgun Gothic", size=14, color="#000000"),
                   bordercolor="#c7c7c7", borderwidth=2,
                   borderpad=4, bgcolor="#F78181",
                   opacity=0.7,
                   text=title2)

    fig.update_traces(customdata=dff[dff['Indicator Name'] == yaxis_column_name]['지역'])
    fig.update_xaxes(title=xaxis_column_name, type='linear' if xaxis_type == 'Linear' else 'log')
    fig.update_yaxes(title=yaxis_column_name, type='linear' if yaxis_type == 'Linear' else 'log')
    fig.update_layout(margin={'l': 40, 'b': 40, 't': 10, 'r': 0}, hovermode='closest')

    return fig

def create_time_series(dff, axis_type, title):
    
    fig = px.scatter(dff, x='year', y='value')
    fig.update_traces(mode='lines+markers')
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(type='linear' if axis_type == 'Linear' else 'log')
    fig.add_annotation(x=0, y=0.85, xanchor='left', yanchor='bottom',
                       xref='paper', yref='paper', showarrow=False, align='left',
                       text=title)
    fig.update_layout(height=225, margin={'l': 20, 'b': 30, 'r': 10, 't': 10})
    return fig

@callback(
    Output('x-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'),
    Input('crossfilter-xaxis-column', 'value'),
    Input('crossfilter-xaxis-type', 'value'))

def update_y_timeseries(hoverData, xaxis_column_name, axis_type):
    country_name = hoverData['points'][0]['customdata']
    dff = df[df['지역'] == country_name]
    dff = dff[dff['Indicator Name'] == xaxis_column_name]
    title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
    return create_time_series(dff, axis_type, title)

@callback(
    Output('y-time-series', 'figure'),
    Input('crossfilter-indicator-scatter', 'hoverData'),
    Input('crossfilter-yaxis-column', 'value'),
    Input('crossfilter-yaxis-type', 'value'))

def update_x_timeseries(hoverData, yaxis_column_name, axis_type):
    dff = df[df['지역'] == hoverData['points'][0]['customdata']]
    dff = dff[dff['Indicator Name'] == yaxis_column_name]
    return create_time_series(dff, axis_type, yaxis_column_name)

# box plot
# Callback function definition
@callback(
    Output('box-plot', 'figure'),
    Input('column-dropdown', 'value')
)
def update_plots(selected_column):
    # Create the Box Plot
    box_fig = go.Figure()
    box_fig.add_trace(go.Box(x=df_boxsstrip['지역'], y=df_boxsstrip[selected_column], name='Box Plot', 
                             boxpoints='all', marker_color='#FF851B', marker_size=2, line_width=1
                            ))
    box_fig.update_layout(height=700, width=1300, title = 'Data Distribution')
    return box_fig
    
if __name__ == '__main__':
    app.run(debug=True)
