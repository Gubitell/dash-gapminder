from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv'
)

# Числовые меры
MEASURES = ['pop', 'lifeExp', 'gdpPercap']

# Справочник названий мер
MEASURE_LABELS = {
    'pop': 'Population',
    'lifeExp': 'Life Expectancy',
    'gdpPercap': 'GDP per Capita',
}

app = Dash(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

# Общий стиль для графиков
GRAPH_STYLE = {"height": "100%", "width": "100%"}

app.layout = html.Div([
    html.H1(
        children='Gapminder Interactive Dashboard',
        style={'textAlign': 'center'}
    ),

    # Панель управления
    html.Div([
        # Мультивыбор стран для линейного графика
        html.Div([
            html.Label('Countries (compare on line chart):'),
            dcc.Dropdown(
                id='countries-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df.country.unique())],
                value=['Canada', 'United States', 'China', 'India'],
                multi=True,
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # Ось Y для линейного графика
        html.Div([
            html.Label('Y axis (line chart):'),
            dcc.Dropdown(
                id='line-yaxis-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='pop',
                clearable=False,
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),
    ], style={'padding': '10px'}),

    html.Div([
        # Ось X для пузырьковой диаграммы
        html.Div([
            html.Label('Bubble X axis:'),
            dcc.Dropdown(
                id='bubble-xaxis-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='gdpPercap',
                clearable=False,
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),

        # Ось Y для пузырьковой диаграммы
        html.Div([
            html.Label('Bubble Y axis:'),
            dcc.Dropdown(
                id='bubble-yaxis-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='lifeExp',
                clearable=False,
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),

        # Радиус пузырьковой диаграммы
        html.Div([
            html.Label('Bubble size (radius):'),
            dcc.Dropdown(
                id='bubble-size-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='pop',
                clearable=False,
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),
    ], style={'padding': '10px'}),

    # Год — кросс-фильтр для топ-15, пирога и пузырьковой
    html.Div([
        html.Label('Year (cross-filter for top-15, pie, bubble):'),
        dcc.Slider(
            id='year-slider',
            min=int(df['year'].min()),
            max=int(df['year'].max()),
            step=5,
            value=2007,
            marks={str(y): str(y) for y in range(int(df['year'].min()), int(df['year'].max()) + 1, 5)},
            tooltip={"placement": "bottom", "always_visible": False},
        ),
    ], style={'padding': '10px 30px'}),

    # Диаграммы
    html.Div([
        # Линейный график — сравнение нескольких стран
        dcc.Graph(id='line-chart', style=GRAPH_STYLE),
    ], style={'width': '100%', 'padding': '10px'}),

    html.Div([
        # Пузырьковая диаграмма
        html.Div([
            dcc.Graph(id='bubble-chart', style=GRAPH_STYLE),
        ], style={'width': '50%', 'display': 'inline-block'}),

        # Топ-15 стран по популяции
        html.Div([
            dcc.Graph(id='top15-chart', style=GRAPH_STYLE),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'padding': '10px'}),

    html.Div([
        # Круговая диаграмма по континентам
        dcc.Graph(id='continent-pie', style=GRAPH_STYLE),
    ], style={'width': '100%', 'padding': '10px'}),
])



# Колбэки

# Линейный график: сравнение выбранных стран по выбранной мере
@callback(
    Output('line-chart', 'figure'),
    Input('countries-dropdown', 'value'),
    Input('line-yaxis-dropdown', 'value'),
)
def update_line_chart(countries, yaxis):
    if not countries:
        countries = ['Canada']
    dff = df[df.country.isin(countries)].sort_values('year')
    fig = px.line(
        dff, x='year', y=yaxis, color='country',
        title=f'{MEASURE_LABELS[yaxis]} over time (selected countries)',
        markers=True,
    )
    fig.update_layout(transition_duration=300)
    return fig


# Пузырьковая диаграмма — оси и радиус выбираются пользователем, год берётся из слайдера (кросс-фильтр)
@callback(
    Output('bubble-chart', 'figure'),
    Input('year-slider', 'value'),
    Input('bubble-xaxis-dropdown', 'value'),
    Input('bubble-yaxis-dropdown', 'value'),
    Input('bubble-size-dropdown', 'value'),
)
def update_bubble_chart(year, xaxis, yaxis, size):
    dff = df[df.year == year]
    fig = px.scatter(
        dff, x=xaxis, y=yaxis, size=size,
        color='continent', hover_name='country',
        size_max=55, log_x=True,
        title=f'Bubble chart for {year}',
    )
    fig.update_layout(transition_duration=300)
    return fig


# Топ-15 стран по популяции за выбранный год
@callback(
    Output('top15-chart', 'figure'),
    Input('year-slider', 'value'),
)
def update_top15(year):
    dff = df[df.year == year].nlargest(15, 'pop')
    fig = px.bar(
        dff.sort_values('pop', ascending=True),
        x='pop', y='country', orientation='h',
        color='continent',
        title=f'Top-15 countries by population in {year}',
    )
    fig.update_layout(transition_duration=300)
    return fig


# Круговая диаграмма по континентам за выбранный год
@callback(
    Output('continent-pie', 'figure'),
    Input('year-slider', 'value'),
)
def update_continent_pie(year):
    dff = df[df.year == year]
    agg = dff.groupby('continent', as_index=False)['pop'].sum()
    fig = px.pie(
        agg, names='continent', values='pop',
        title=f'Population by continent in {year}',
    )
    fig.update_layout(transition_duration=300)
    return fig

server = app.server
if __name__ == '__main__':
    app.run(debug=True)