import GOES
import dash
from dash import dcc, html, page_registry, page_container
from dash.dependencies import Input, Output
import pandas as pd
from goes_data_tools import find_near_point, get_Data, get_Rad
import os
import plotly.express as px
from netCDF4 import Dataset
import dash_bootstrap_components as dbc
import numpy as np
import dash_leaflet as dl
from datetime import datetime, timedelta
import glob
import time

def download():

    isExist = os.path.exists('radiances') 
    if isExist:
        if os.listdir('radiances/'):
            lista_paths = os.listdir('radiances/')[0]
            name_date_ini = lista_paths[5:9] + '-' + lista_paths[9:11] + '-' + lista_paths[11:13] + '-' + lista_paths[13:15] + '-' + lista_paths[15:17] 
            name_date_ini = datetime.strptime(name_date_ini, '%Y-%m-%d-%H-%M')

            date_ini_next = name_date_ini + timedelta(minutes=20)
            date_ini = date_ini_next.strftime("%Y-%m-%y %H:%M")

            date_fin_next = date_ini_next + timedelta(minutes=9)
            date_fin = date_fin_next.strftime("%Y-%m-%y %H:%M")

            get_Rad(date_ini, date_fin)

        else: 
            c = datetime.now()
            current_time = c.strftime('%Y-%m-%d %H:%M:%S')
            current_time = current_time[:-5] + '00:00'

            date_ini = current_time[:-5] + '00'
            date_fin = current_time[:-5] + '09'

            get_Rad(date_ini, date_fin)

    else: 
        c = datetime.now()
        current_time = c.strftime('%Y-%m-%d %H:%M:%S')
        current_time = current_time[:-5] + '00:00'

        date_ini = current_time[:-5] + '00'
        date_fin = current_time[:-5] + '09'

        get_Rad(date_ini, date_fin)        


def App():
    # Initialize the app
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

    #read data
    data_city = pd.read_csv('Ciudades.csv')

    # Define the layout
    app.layout = html.Div([
        # Header
        html.Div([
            html.H1("Datos satelitales GOES-16 sobre Colombia", className='headerH1'),
            html.Img(src="path_to_icon.png", className='header-icon'),
        ], className='header'),

        # Sidebar and content layout
        html.Div([
            # Sidebar
            html.Div([
                html.Div([
                    html.P('Seleccione ciudad'),
                    dcc.Dropdown(id='cities',
                                value='Medellin',
                                placeholder='Ubicacion',
                                options=[{'label': c, 'value': c} for c in data_city['ciudad']]),
                    
                    html.P('Seleccione el tamano de la malla'),
                    dcc.Dropdown(id='resolution',
                                value=3,
                                placeholder='Resolucion',
                                options=[{'label': '3x3', 'value':3}, {'label': '5x5', 'value':5}, {'label': '10x10', 'value':10}]), 

                    html.P('Seleccione variable'),
                    dcc.Dropdown(id='variable',
                                value='Rad8',
                                placeholder='Variable',
                                options=[{'label': 'Radianza banda 8', 'value':'Rad8'}, 
                                        {'label': 'Radianza banda 9', 'value':'Rad9'}, 
                                        {'label': 'Radianza banda 10', 'value':'Rad10'},
                                        {'label': 'Radianza banda 13', 'value':'Rad13'},
                                        {'label': 'Radianza banda 14', 'value':'Rad14'}]),
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(id="city-name", children="City name", className="card-title"),
                            html.Hr(),
                            html.P(id="variable-name", children="Variable name", className="card-text"),
                            html.P(id="date-name", children="Date name", className="card-text"),                    
                            html.P(id="resolution-name", children="Resolution name", className="card-text")
                        ]), style={"width": "18rem", "padding": "10px", "margin-top":"50px"})
            ])
            ], className='siddebar'), 

            # Main content
            html.Div(dl.Map([dl.TileLayer(), 
                dl.Rectangle(id='rectangle', bounds=[[6.26951742, -75.60275336], [6.23276768, -75.56580692]])], 
                id='map', center=[6.25101405, -75.58414913], zoom=13, style={'height': '50vh'})),
        ])
    ])

    # Callback to update content based on URL

    @app.callback(
        Output('cities', 'value'),
        [Input('cities', 'options')]
    )
    def set_cities(cities):
        return cities[0]['value']

    @app.callback(
        Output('resolution', 'value'),
        [Input('resolution', 'options')]
    )
    def set_resolution(resolution):
        return resolution[0]['value']

    @app.callback(
        Output('variable', 'value'),
        [Input('variable', 'options')]
    )
    def set_variable(variable):
        return variable[0]['value']

    @app.callback(
        [Output('city-name', 'children'),
        Output('variable-name', 'children'),
        Output('date-name', 'children'),
        Output('resolution-name', 'children')],
        [Input('cities', 'value'),
        Input('variable', 'value'),
        Input('resolution', 'value')]
    )
    def set_card(cities, variable, resolution):
        choosed_city = cities

        if resolution == 3:
            choosed_resolution = '3x3'
        elif resolution == 5:
            choosed_resolution = '5x5'
        else:
            choosed_resolution = '10x10'        

        ciudades = pd.read_csv('Ciudades.csv')
        city = ciudades[ciudades['ciudad'] == cities]
        ciudad_lat = city['latitud'].values[0]
        ciudad_lon = city['longitud'].values[0]

        lista_paths = os.listdir('radiances/')
        date = lista_paths[0][5:9] + '-' + lista_paths[0][9:11] + '-' + lista_paths[0][11:13]
        
        list_of_files = glob.glob('radiances/*.nc') # * means all if need specific format then *.csv
        latest_file = max(list_of_files, key=os.path.getctime)

        ds1 = Dataset(latest_file)
        lat = ds1['lat'][:]
        lon = ds1['lon'][:]

        lat_near, lon_near, lat_points, lon_points = find_near_point(lat, lon, ciudad_lat, ciudad_lon, resolution)

        if variable == 'Rad8':
            choosed_var = 'Radianza banda 8'
            var = get_Data(ds1, lon_points, lat_points, variable='Rad8')

        elif variable == 'Rad9':
            choosed_var = 'Radianza banda 9'
            var = get_Data(ds1, lon_points, lat_points, variable='Rad9')    

        elif variable == 'Rad10':
            choosed_var = 'Radianza banda 10'
            var = get_Data(ds1, lon_points, lat_points, variable='Rad10')

        elif variable == 'Rad13':
            choosed_var = 'Radianza banda 13'
            var = get_Data(ds1, lon_points, lat_points, variable='Rad13')

        elif variable == 'Rad14':
            choosed_var = 'Radianza banda 14'
            var = get_Data(ds1, lon_points, lat_points, variable='Rad14')
                

        lon = []
        lat = []
        list_var = []
        for i in range(len(lon_points)):
            for j in range(len(lon_points)):
                lon.append(lon_points[i,j])
                lat.append(lat_points[i,j])
                list_var.append(var[i,j])
                    
        mean_variable = np.round(np.mean(list_var), 2)
        
        content_var = [
                html.Span(f"{choosed_var}: ", style={"fontWeight": "bold"}),
                f"{str(mean_variable)}" + " W m-2 sr-1 um-1"]
        
        content_date = [
                html.Span("Fecha: ", style={"fontWeight": "bold"}),
                f"{date}"]
        
        content_resolution = [
                html.Span("Resolucion: ", style={"fontWeight": "bold"}),
                f"{choosed_resolution}"]
        
        return choosed_city, content_var, content_date, content_resolution 

    @app.callback(
        [Output('rectangle', 'bounds'),
        Output('map', 'center'),
        Output('map', 'zoom')], 
        [Input('cities', 'value'), 
        Input('resolution', 'value')]
    )
    def heatmap_plot(cities, resolution):
        if resolution == 3:
            zoom = 13
        elif resolution == 5:
            zoom = 12
        else:
            zoom = 10

        ciudades = pd.read_csv('Ciudades.csv')
        city = ciudades[ciudades['ciudad'] == cities]
        ciudad_lat = city['latitud'].values[0]
        ciudad_lon = city['longitud'].values[0]

        lista_paths = os.listdir('radiances/')

        ds1 = Dataset('radiances/'+lista_paths[0])
        lat = ds1['lat'][:]
        lon = ds1['lon'][:]

        lat_near, lon_near, lat_points, lon_points = find_near_point(lat, lon, ciudad_lat, ciudad_lon, resolution)
        bounds = [[lat_points[0,0], lon_points[0,0]], [lat_points[-1,-1], lon_points[-1,-1]]]
        center = [lat_near, lon_near]

        return bounds, center, zoom       
    app.run_server()

def main_app():
    while True:
        download()
        App()
        time.sleep(1200)

# Run the app
if __name__ == '__main__':
    main_app()
