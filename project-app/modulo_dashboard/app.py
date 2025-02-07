import dash
from dash import dcc, html, page_registry, page_container
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import os
import numpy as np
from netCDF4 import Dataset
import glob
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

def find_near_point(lat, lon, ciudad_lat, ciudad_lon, malla):
    lat, lon = np.meshgrid(lat, lon) 

    cercanos  = []
    indices_cercanos=[]
    for i in range(len(lat)):
        for j in range(len(lat)):
            if abs(lat[i,j] - ciudad_lat) <= 0.1: 
                cercanos.append([lat[i,j], lon[i,j]])
                indices_cercanos.append([i,j])

    mas_cercanos=[]
    indice_mas_cercano=[]
    distancia=[]
    for i,cerca in enumerate(cercanos):
        if abs(cerca[1] - ciudad_lon) <= 0.1:
            mas_cercanos.append(cerca)
            indice_mas_cercano.append(indices_cercanos[i])
            distancia.append(((cerca[0]-ciudad_lat)**2+(cerca[1]-ciudad_lon)**2)**(1/2))

    min_dist = np.min(distancia)      
    indice_min = distancia.index(min_dist)

    near = indice_mas_cercano[indice_min]
    lat_near = lat[near[0], near[1]] 
    lon_near = lon[near[0], near[1]]

    if malla == 3:
        lat_points = lat[near[0]-1:near[0]+2, near[1]-1:near[1]+2]
        lon_points = lon[near[0]-1:near[0]+2, near[1]-1:near[1]+2]

    elif malla == 5:
        lat_points = lat[near[0]-2:near[0]+3, near[1]-2:near[1]+3]
        lon_points = lon[near[0]-2:near[0]+3, near[1]-2:near[1]+3]

    else:
        lat_points = lat[near[0]-5:near[0]+6, near[1]-5:near[1]+6]
        lon_points = lon[near[0]-5:near[0]+6, near[1]-5:near[1]+6]        


    return lat_near, lon_near, lat_points, lon_points

def get_Data(ds, lon, lat, variable='LST'):

    lat_rad_1d = ds.variables['lat'][:]
    lon_rad_1d = ds.variables['lon'][:]

    xmin = np.min(lon)
    ymin = np.min(lat)

    xmax = np.max(lon)
    ymax = np.max(lat)

    sel_y = np.where((lat_rad_1d>=ymin) & (lat_rad_1d<=ymax))
    sel_x = np.where((lon_rad_1d>=xmin) & (lon_rad_1d<=xmax))

    Data = ds.variables[variable][sel_y[0].min():sel_y[0].max()+1,sel_x[0].min():sel_x[0].max()+1]

    datos = Data.data

    for i in range(len(datos)):
        for j in range(len(datos)):
            if datos[i][j] == 65535.:
                datos[i][j] = np.nan
            else:
                pass     

    return datos


# Initialize the app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

#read data
data_city = {'Medellin': [6.25204,-75.582588], 'Bogota': [4.653074,-74.106448], 'Cucuta': [7.906564,-72.5097], 
                'Ibague': [4.431797,-75.198797], 'Valledupar': [10.469062,-73.255675], 'Pereira': [4.803405,-75.716337], 
                'Manizales': [5.057924,-75.500295], 'Buenaventura': [3.879256,-77.008785], 'Inirida': [3.865814,-67.924432], 
                'Leticia': [-4.208594,-69.943431], 'Mocoa': [1.151397,-76.648995], 'Neiva': [2.941732,-75.286125], 
                'Palmira': [3.865814,-67.924432], 'Pamplona': [7.372149,-72.650551], 'Quibdo': [5.692077,-76.653716],
                'Rionegro': [6.148405,-75.378508], 'Sogamoso': [5.729765,-72.927993], 'Tumaco': [1.775423,-78.78793],
                'Zipaquira': [5.021561,-73.995758]}

coordinates_path = os.path.join(SCRIPT_DIR, 'coordinates.json')
with open(coordinates_path, "r", encoding="utf-8") as file:
    coordinates = json.load(file)


# Define the layout
app.layout = html.Div(className="app-layout", children=[
    # Header
    html.Div(className='header', children=[
        html.H1("COLOMBIA GOES-16")
    ]),

    # Sidebar and content layout
    html.Div(className="content-container", children=[
        # Sidebar
        html.Div(className="sidebar", children=[
            html.H4("Datos satelitales sobre Colombia", className="text-center"),
            html.P("Seleccione los parametros para mostrar variables climaticas tomadas por el satelite GOES-16 sobre el territorio colombiano", className="text-center"),
            html.Hr(),
            html.P('Seleccione ciudad'),
            dcc.Dropdown(id='cities',
                        value='Medellin',
                        placeholder='Ubicacion',
                        options=[{'label': c, 'value': c} for c in data_city.keys()]),
            
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
                                {'label': 'Radianza banda 14', 'value':'Rad14'}
                        ]),
            dbc.Card(
                dbc.CardBody([
                    html.H4(id="city-name", children="City name", className="card-title"),
                    html.Hr(),
                    html.P(id="variable-name", children="Variable name", className="card-text"),
                    html.P(id="date-name", children="Date name", className="card-text"),
                    html.P(id="resolution-name", children="Resolution name", className="card-text")
                ]), 
            ),
            html.P("Proyecto académico. No nos responsabilizamos del uso de los datos. La información se obtuvo de Datos Abiertos. Última actualización: Enero de 2023. Conctactanos al facomestaciones@gmail.com", className="text-center"),
    ]), 

        # Main content
        html.Div(className="main-content", children=[
            dl.Map([
                dl.TileLayer(),
                dl.Rectangle(id='rectangle', bounds=[[6.26951742, -75.60275336], [6.23276768, -75.56580692]])
            ], id='map', center=[6.25101405, -75.58414913], zoom=13)
        ])
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

    city = data_city[cities]
    ciudad_lat = city[0]
    ciudad_lon = city[1]

    project_root = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
    radiances_path = os.path.join(project_root, 'radiances')
    #radiances_path_fix = '/mnt/c/Users/aguju/Documents/joven-investigador/repository/GOES_Colombia/project-app/radiances'

    lista_paths = os.listdir(radiances_path)
    date = lista_paths[0][5:9] + '-' + lista_paths[0][9:11] + '-' + lista_paths[0][11:13] + ' ' + lista_paths[0][13:17]
    
    files_path = os.path.join(radiances_path, '*.nc')
    list_of_files = glob.glob(files_path) 
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

    city = data_city[cities]
    ciudad_lat = city[0]
    ciudad_lon = city[1]

    lat = coordinates['lat']
    lon = coordinates['lon']

    lat_near, lon_near, lat_points, lon_points = find_near_point(lat, lon, ciudad_lat, ciudad_lon, resolution)
    bounds = [[lat_points[0,0], lon_points[0,0]], [lat_points[-1,-1], lon_points[-1,-1]]]
    center = [lat_near, lon_near]

    return bounds, center, zoom       
    
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)  