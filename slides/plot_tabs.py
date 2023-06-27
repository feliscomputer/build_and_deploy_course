from math import pi

import numpy as np
import pandas as pd
import panel as pn

from bokeh.palettes import Category20c, Category20
from bokeh.plotting import figure
from bokeh.transform import cumsum

pn.extension('deckgl', 'echarts', 'plotly', 'vega', 'vizzu', defer_load=True)

###############
# Altair/Vega #
###############

def altair_pane():
    import altair as alt
    from vega_datasets import data

    cars = data.cars()

    chart = alt.Chart(cars).mark_circle(size=60).encode(
        x='Horsepower',
        y='Miles_per_Gallon',
        color='Origin',
        tooltip=['Name', 'Origin', 'Horsepower', 'Miles_per_Gallon']
    ).properties(width='container', height='container').interactive()

    return pn.pane.Vega(chart)

#########
# Bokeh #
#########

x = {
    'United States': 157,
    'United Kingdom': 93,
    'Japan': 89,
    'China': 63,
    'Germany': 44,
    'India': 42,
    'Italy': 40,
    'Australia': 35,
    'Brazil': 32,
    'France': 31,
    'Taiwan': 31,
    'Spain': 29
}

data = pd.Series(x).reset_index(name='value').rename(columns={'index':'country'})
data['angle'] = data['value']/data['value'].sum() * 2*pi
data['color'] = Category20c[len(x)]

def bokeh_pane():
    p = figure(sizing_mode='stretch_both', title="Pie Chart", toolbar_location=None,
               tools="hover", tooltips="@country: @value", x_range=(-0.5, 1.0), min_height=400)

    r = p.wedge(x=0, y=1, radius=0.4,
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend_field='country', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    return pn.pane.Bokeh(p, sizing_mode="stretch_both", max_width=1300)


###########
# Deck.GL #
###########

MAPBOX_KEY = (
    "pk.eyJ1IjoibWFyY3Nrb3ZtYWRzZW4iLCJhIjoiY2s1anMzcG5rMDYzazNvcm10NTFybTE4cSJ9."
    "TV1XBgaMfR-iTLvAXM_Iew"
)

json_spec = {
    "initialViewState": {
        "bearing": -27.36,
        "latitude": 52.2323,
        "longitude": -1.415,
        "maxZoom": 15,
        "minZoom": 5,
        "pitch": 40.5,
        "zoom": 6
    },
    "layers": [{
        "@@type": "HexagonLayer",
        "autoHighlight": True,
        "coverage": 1,
        "data": "https://raw.githubusercontent.com/uber-common/deck.gl-data/master/examples/3d-heatmap/heatmap-data.csv",
        "elevationRange": [0, 3000],
        "elevationScale": 50,
        "extruded": True,
        "getPosition": "@@=[lng, lat]",
        "id": "8a553b25-ef3a-489c-bbe2-e102d18a3211", "pickable": True
    }],
    "mapStyle": "mapbox://styles/mapbox/dark-v9",
    "views": [{"@@type": "MapView", "controller": True}]
}

def deck_gl():
    return pn.pane.DeckGL(json_spec, mapbox_api_key=MAPBOX_KEY, sizing_mode='stretch_both')

echart = {
        'title': {
            'text': 'ECharts entry example'
        },
        'tooltip': {},
        'legend': {
            'data':['Sales']
        },
        'xAxis': {
            'data': ["shirt","cardign","chiffon shirt","pants","heels","socks"]
        },
        'yAxis': {},
        'series': [{
            'name': 'Sales',
            'type': 'bar',
            'data': [5, 20, 36, 10, 10, 20]
        }],
    }

def echarts_pane():
    return pn.pane.ECharts(echart, sizing_mode='stretch_both')


import holoviews as hv
import hvplot.pandas
import holoviews.plotting.bokeh

def sine(frequency=1.0, amplitude=1.0, function='sin'):
    xs = np.arange(200)/200*20.0
    ys = amplitude*getattr(np, function)(frequency*xs)
    return pd.DataFrame(dict(y=ys), index=xs).hvplot(responsive=True)

def hv_panel():
    dmap = hv.DynamicMap(sine, kdims=['frequency', 'amplitude', 'function']).redim.range(
        frequency=(0.1, 10), amplitude=(1, 10)).redim.values(function=['sin', 'cos', 'tan']).opts(responsive=True, line_width=4)

    return pn.pane.HoloViews(dmap, widgets={
        'amplitude': pn.widgets.LiteralInput(value=1., type=(float, int)),
        'function': pn.widgets.RadioButtonGroup,
        'frequency': {'value': 5},
    }, center=True, sizing_mode='stretch_both').layout


def mpl_pane():
    import matplotlib

    matplotlib.use('agg')

    import matplotlib.pyplot as plt

    Y, X = np.mgrid[-3:3:100j, -3:3:100j]
    U = -1 - X**2 + Y
    V = 1 + X - Y**2
    speed = np.sqrt(U*U + V*V)

    fig0, ax0 = plt.subplots()
    strm = ax0.streamplot(X, Y, U, V, color=U, linewidth=2, cmap=plt.cm.autumn)
    fig0.colorbar(strm.lines)

    return pn.pane.Matplotlib(fig0, format='svg', sizing_mode='stretch_both')

def plotly_pane():
    import plotly.graph_objs as go

    xx = np.linspace(-3.5, 3.5, 100)
    yy = np.linspace(-3.5, 3.5, 100)
    x, y = np.meshgrid(xx, yy)
    z = np.exp(-(x-1)**2-y**2)-(x**3+y**4-x/5)*np.exp(-(x**2+y**2))

    surface = go.Surface(z=z)
    layout = go.Layout(
        title='Plotly 3D Plot',
        autosize=True,
        margin=dict(t=50, b=50, r=50, l=50)
    )
    fig = dict(data=[surface], layout=layout)
    return pn.pane.Plotly(fig)


def vizzu_pane():
    data = {
        'Name': ['Alice', 'Bob', 'Ted', 'Patrick', 'Jason', 'Teresa', 'John'],
        'Weight': 50+np.random.randint(0, 10, 7)*10
    }

    geom = pn.widgets.RadioButtonGroup(value='rectangle', options=['rectangle', 'circle', 'area'])

    vizzu = pn.pane.Vizzu(
        data, config=pn.bind(lambda geom: {'geometry': geom, 'x': 'Name', 'y': 'Weight', 'title': 'Weight by person'}, geom),
        duration=400, height=400, sizing_mode='stretch_width'
    )

    return pn.Column(geom, vizzu)

def get_plot_tabs():
    return pn.Tabs(
        ('Altair', altair_pane),
        ('Bokeh', bokeh_pane),
        ('deck.GL', deck_gl),
        ('Echarts', echarts_pane),
        ('HoloViews', hv_panel),
        ('Matplotlib', mpl_pane),
        ('Plotly', plotly_pane),
        ('Vizzu', vizzu_pane),
        dynamic=True, height=600, width=800
    )