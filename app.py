from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd


# ------------------------ Данные ------------------------------

df = pd.read_csv(
    'https://raw.githubusercontent.com/plotly/datasets/master/gapminder_unfiltered.csv'
)

# Числовые меры (колонки, по которым можно строить оси и радиусы)
MEASURES = ['pop', 'lifeExp', 'gdpPercap']

# Справочник человекочитаемых названий мер
MEASURE_LABELS = {
    'pop': 'Population',
    'lifeExp': 'Life Expectancy',
    'gdpPercap': 'GDP per Capita',
}

DEFAULT_YEAR = 2007


# ----------------------- Приложение ----------------------------

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = Dash(__name__, external_stylesheets=external_stylesheets)

GRAPH_STYLE = {"height": "100%", "width": "100%"}

# ----------------------------------------------------------------------------
# Layout: 5 элементов управления + 4 диаграммы
#   Controls:
#     1) multi-country dropdown  -> линейный график (сравнение стран)
#     2) y-axis dropdown          -> линейный график
#     3) bubble x-axis dropdown   -> пузырьковая
#     4) bubble y-axis dropdown   -> пузырьковая
#     5) bubble size dropdown     -> пузырьковая
#   Charts:
#     A) line chart (multi-country)   -> источник года (clickData)
#     B) bubble chart                 -> фильтруется по году
#     C) top-15 bar chart             -> фильтруется по году
#     D) continent pie chart          -> фильтруется по году
# ----------------------------------------------------------------------------
app.layout = html.Div([
    html.H1(
        children='Gapminder Interactive Dashboard',
        style={'textAlign': 'center'}
    ),

    # -------------------- Панель управления --------------------
    html.Div([
        # 1) Мультивыбор стран для линейного графика
        html.Div([
            html.Label('Countries (compare on line chart):'),
            dcc.Dropdown(
                id='countries-dropdown',
                options=[{'label': c, 'value': c} for c in sorted(df.country.unique())],
                value=['Canada', 'United States', 'China', 'India'],
                multi=True,
            ),
        ], style={'width': '48%', 'display': 'inline-block', 'verticalAlign': 'top'}),

        # 2) Ось Y для линейного графика
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
        # 3) Ось X для пузырьковой диаграммы
        html.Div([
            html.Label('Bubble X axis:'),
            dcc.Dropdown(
                id='bubble-xaxis-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='gdpPercap',
                clearable=False,
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),

        # 4) Ось Y для пузырьковой диаграммы
        html.Div([
            html.Label('Bubble Y axis:'),
            dcc.Dropdown(
                id='bubble-yaxis-dropdown',
                options=[{'label': MEASURE_LABELS[m], 'value': m} for m in MEASURES],
                value='lifeExp',
                clearable=False,
            ),
        ], style={'width': '32%', 'display': 'inline-block'}),

        # 5) Радиус пузырьковой диаграммы
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

    # -------------------- Диаграммы --------------------
    html.Div([
        # A) Линейный график — сравнение нескольких стран.
        #    Клик по точке выбирает год (кросс-фильтр).
        dcc.Graph(id='line-chart', style=GRAPH_STYLE),
    ], style={'width': '100%', 'padding': '10px'}),

    html.Div([
        # B) Пузырьковая диаграмма
        html.Div([
            dcc.Graph(id='bubble-chart', style=GRAPH_STYLE),
        ], style={'width': '50%', 'display': 'inline-block'}),

        # C) Топ-15 стран по популяции
        html.Div([
            dcc.Graph(id='top15-chart', style=GRAPH_STYLE),
        ], style={'width': '50%', 'display': 'inline-block'}),
    ], style={'padding': '10px'}),

    html.Div([
        # D) Круговая диаграмма по континентам
        dcc.Graph(id='continent-pie', style=GRAPH_STYLE),
    ], style={'width': '100%', 'padding': '10px'}),
])



# ----------------- Колбэки ----------------------


def _year_from_click(clickData):
    if clickData and clickData.get('points'):
        try:
            return int(clickData['points'][0]['x'])
        except (KeyError, TypeError, ValueError):
            pass
    return DEFAULT_YEAR


# A) Линейный график: сравнение выбранных стран по выбранной мере
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


# B) Пузырьковая диаграмма — оси и радиус выбираются пользователем,
#    год берётся из clickData линейного графика
@callback(
    Output('bubble-chart', 'figure'),
    Input('line-chart', 'clickData'),
    Input('bubble-xaxis-dropdown', 'value'),
    Input('bubble-yaxis-dropdown', 'value'),
    Input('bubble-size-dropdown', 'value'),
    prevent_initial_call=True,
)
def update_bubble_chart(clickData, xaxis, yaxis, size):
    year = _year_from_click(clickData)
    dff = df[df.year == year]
    fig = px.scatter(
        dff, x=xaxis, y=yaxis, size=size,
        color='continent', hover_name='country',
        custom_data=['continent'],
        size_max=55, log_x=True,
        title=f'Bubble chart for {year}',
    )
    fig.update_layout(transition_duration=300)
    return fig


# C) Топ-15 стран по популяции за год, выбранный на линейном графике
@callback(
    Output('top15-chart', 'figure'),
    Input('line-chart', 'clickData'),
    prevent_initial_call=True,
)
def update_top15(clickData):
    year = _year_from_click(clickData)
    dff = df[df.year == year]
    top = dff.nlargest(15, 'pop').sort_values('pop', ascending=True)
    fig = px.bar(
        top, x='pop', y='country', orientation='h',
        title=f'Top-15 countries by population in {year}',
    )
    fig.update_layout(
        transition_duration=300,
        yaxis={'categoryorder': 'total ascending'},
    )
    return fig


# D) Круговая диаграмма по континентам за год, выбранный на линейном графике
@callback(
    Output('continent-pie', 'figure'),
    Input('line-chart', 'clickData'),
    prevent_initial_call=True,
)
def update_continent_pie(clickData):
    year = _year_from_click(clickData)
    dff = df[df.year == year]
    agg = dff.groupby('continent', as_index=False)['pop'].sum()
    fig = px.pie(
        agg, names='continent', values='pop',
        title=f'Population by continent in {year}',
    )
    fig.update_layout(transition_duration=300)
    return fig

# ----------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)