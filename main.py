import dash
from dash import dcc, html, Input, Output, callback
import requests
import pandas as pd
import plotly.express as px
import plotly.io as poi

poi.renderers.default = 'browser'

# Получение данных
response = requests.get('http://asterank.com/api/kepler?query={}&limit=2000')
df = pd.json_normalize(response.json())

# Добавление нового столбца для классификации размеров
def classify_size(row):
    if row['RPLANET'] > row['RSTAR']:
        return 'big'
    elif abs(row['RPLANET'] - row['RSTAR']) / row['RSTAR'] < 0.1:
        return 'same size'
    else:
        return 'small'

df['SizeCategory'] = df.apply(classify_size, axis=1)

# Инициализация приложения
app = dash.Dash(__name__, suppress_callback_exceptions=True)

app.layout = html.Div([
    html.H1('EXOPLANET DATA VISUALIZATION'),
    
    # Вкладки
    dcc.Tabs(id='tabs-example', value='tab-1', children=[
        dcc.Tab(label='Graphs', value='tab-1'),
        dcc.Tab(label='About', value='tab-2'),
    ]),
    html.Div(id='tabs-content-example')
])

# Callback для отображения содержимого вкладок
@app.callback(Output('tabs-content-example', 'children'),
              Input('tabs-example', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H2('Read about exoplanets'),

            # Выпадающее меню
            dcc.Dropdown(
                options=[
                    {'label': 'Big', 'value': 'big'},
                    {'label': 'Same Size', 'value': 'same size'},
                    {'label': 'Small', 'value': 'small'}
                ],
                value='big',  # Значение по умолчанию
                id='size-dropdown'
            ),
            # Добавление RangeSlider
            dcc.RangeSlider(
                id='rplanet-slider',
                min=df['RPLANET'].min(),
                max=df['RPLANET'].max(),
                value=[df['RPLANET'].min(), df['RPLANET'].max()],
                marks={i: str(i) for i in range(int(df['RPLANET'].min()), int(df['RPLANET'].max()) + 1, 2)},
                step=0.1,
            ),
            html.Div(id='dd-output-container'),

            # Первый график
            dcc.Graph(id='scatter-plot'),

            # Второй график
            dcc.Graph(id='radius-relationship-plot'),

             # Третий график
            dcc.Graph(id='mass-size-plot'),

            
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('About This Site'),
            html.P('This site provides visualizations of exoplanet data obtained from the Kepler mission. '
                   'Explore different characteristics of exoplanets and their host stars through interactive graphs. '
                   'Use the dropdown and slider to filter data based on planet size and radius.')
        ])

# Callback для обновления первого графика
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('rplanet-slider', 'value'),
     Input('size-dropdown', 'value')]
)
def update_graph(selected_range, selected_size):
    filtered_df = df[(df['RPLANET'] >= selected_range[0]) & 
                     (df['RPLANET'] <= selected_range[1]) & 
                     (df['SizeCategory'] == selected_size)]
    fig = px.scatter(filtered_df, x='RPLANET', y='TPLANET', title=f'Size Category: {selected_size.capitalize()}')
    return fig

# Callback для обновления второго графика
@app.callback(
    Output('radius-relationship-plot', 'figure'),
    [Input('rplanet-slider', 'value'),
     Input('size-dropdown', 'value')]
)
def update_radius_relationship(selected_range, selected_size):
    filtered_df = df[(df['RPLANET'] >= selected_range[0]) & 
                     (df['RPLANET'] <= selected_range[1]) & 
                     (df['SizeCategory'] == selected_size)]
    fig = px.scatter(filtered_df, x='RPLANET', y='RSTAR', title=f'Planet vs Star Radius: {selected_size.capitalize()}')
    return fig

# Callback для обновления третьего графика
@app.callback(
    Output('mass-size-plot', 'figure'),
    [Input('rplanet-slider', 'value'),
    Input('size-dropdown', 'value')]
)
def update_mass_relationship(selected_range, selected_size):
    filtered_df = df[(df['RPLANET'] >= selected_range[0]) &
                      (df['RPLANET'] <=selected_range[1]) &
                      (df['SizeCategory'] == selected_size)]
    fig = px.scatter(filtered_df, x='TPLANET', y='MSTAR', title=f'Mass vs Temp: {selected_size.capitalize()}')
    return fig

@callback(
    Output('dd-output-container', 'children'),
    Input('size-dropdown', 'value')
)
def update_output(value):
    return f'You have selected {value}'

if __name__ == '__main__':
    app.run_server(debug=True)
