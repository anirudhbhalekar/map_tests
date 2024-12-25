import osmnx as ox 
import random
import tqdm 
import matplotlib.pyplot as plt 
import matplotlib.patches as patch
import geopandas as gpd
import numpy as np 
import networkx

from matplotlib.widgets import TextBox
from matplotlib.widgets import Button 
from matplotlib.widgets import Slider 


# Define place name - can be made a field inside pyplot later

# Initial tags for mapping
building_tags = {'building' : True}  
highway_tags = {'highway' : True}

# Route efficiency array 
route_efficiency_arr = []

custom_filter_arr = ['["highway"~"motorway"]', '["highway"~"motorway|trunk"]','["highway"~"motorway|trunk|primary"]', 
                      '["highway"~"motorway|trunk|primary|secondary"]', '["highway"]']

def get_g2(place_name): 

    try: 
        # Geocode to GDF object (to get bbox)
        area = ox.geocode_to_gdf(place_name)
        bounds = area.total_bounds
        x_min, y_min, x_max, y_max = bounds[0], bounds[1], bounds[2], bounds[3]
        area = (x_max - x_min) * (y_max - y_min)
        print(area)
        if area > 0.03: 
            calc_area = area


        # Geocode to graph (graphing)

        G2 = ox.graph_from_place(place_name, simplify=True, custom_filter=custom_filter_arr[-1])
        #G2 = ox.simplify_graph(G2)
        print("Loaded GeoDataFrame")
    except Exception as ex: 
        
        print("Could not resolve")
        fig_err, ax_err = plt.subplots(figsize = (2, 2))
        ax_err.grid('off')
        ax_err.set_title("Could not Resolve!")
        plt.show()
        raise ValueError(ex)
    
   
    return G2, bounds
 

# Function to generate a random x/y coordinates based on boundaries of the GDF 

def gen_random_points(bounds): 

    x_min, y_min, x_max, y_max = bounds[0], bounds[1], bounds[2], bounds[3]
    rx, ry = random.random(), random.random()

    # Simple RNG from 0 to 1 scaled to the boundary intervals 

    p_x = x_min + (x_max - x_min) * rx
    p_y = y_min + (y_max - y_min) * ry

    return (p_x, p_y) 


def get_coords(G2, bounds): 

    (sx, sy) = gen_random_points(bounds)
    (dx, dy) = gen_random_points(bounds)

    nn_s = ox.nearest_nodes(G2, sx, sy, return_dist = False)
    nn_d = ox.nearest_nodes(G2, dx, dy, return_dist = False)

    nn_sx, nn_sy = G2.nodes[nn_s]['x'], G2.nodes[nn_s]['y']
    nn_dx, nn_dy = G2.nodes[nn_d]['x'], G2.nodes[nn_d]['y']

    s_dist = ((nn_sx - sx)**2 + (nn_sy - sy)**2)**0.5
    d_dist = ((nn_dx - dx)**2 + (nn_dy - dy)**2)**0.5

    s_path = ox.shortest_path(G2, orig = nn_s, dest = nn_d)

    try: 
        if len(s_path) <= 1: 
            get_coords(G2, bounds)
    except: 
        get_coords(G2, bounds)

    s_tup, d_tup = [(sx,sy), nn_s, s_dist], [(dx,dy), nn_d, d_dist]

    return s_path, s_tup, d_tup


# Routine

def get_agg_route_efficiency(G2, s_path, s_tup:tuple, d_tup:tuple): 

    (sx,sy) = s_tup[0]
    (dx,dy) = d_tup[0]

    nn_s, nn_d = s_tup[1], d_tup[1]
    s_dist, d_dist = s_tup[2], d_tup[2]

    x_diff = sx - dx 
    y_diff = sy - dy

    dir_dist = np.sqrt(x_diff **2 + y_diff**2)
    path_dist = 0


    for i in range(len(s_path) - 1): 
        curr_node = s_path[i]
        next_node = s_path[i+1]

        curr_x, curr_y = G2.nodes[curr_node]['x'], G2.nodes[curr_node]['y']
        next_x, next_y = G2.nodes[next_node]['x'], G2.nodes[next_node]['y']

        del_x, del_y = next_x - curr_x, next_y - curr_y 

        path_dist += (del_x**2 + del_y**2)**0.5

    path_dist += s_dist + d_dist
    
    return dir_dist, path_dist

def run_routine(place_name): 
    G2, bounds = get_g2(place_name)
    s_path, s_tup, d_tup = get_coords(G2, bounds) 
    return G2, bounds, s_path, s_tup, d_tup 

# Plotting things

def plot_map(place_name): 

    

    G2, bounds, s_path, s_tup, d_tup = run_routine(place_name)
    fig, main_ax = plt.subplots(figsize = (9,5))

    plt.axis('off')
    ox.plot_graph(G2, ax=main_ax, show = False, close = False, bgcolor = 'white', node_color= 'grey', edge_linewidth= 1, node_size = 3)

    main_ax.set_title(f"Map of {place_name}")

    axbox = plt.axes([0.3, 0.05, 0.3, 0.075])
    text_box = TextBox(axbox, 'Place Name', initial=place_name)

    ax_route = plt.axes([0.7, 0.05, 0.1, 0.075])
    route_button = Button(ax_route, 'New Route')

    ax_auto = plt.axes([0.8, 0.05, 0.1, 0.075])
    auto_button = Button(ax_auto, 'Auto-Run')

    def plot_route(G2, ax, route, s_tup, d_tup, print_statement = True, show_route = True): 

        try:
            if (show_route):
                colors_arr = ['green', 'red', 'blue', 'yellow', 'purple']

                ox.plot_graph_route(G2, ax=ax, route = route, route_linewidth = 2, node_size = 15, show = False, close = False, 
                                    bgcolor = 'white', node_color= 'black', orig_dest_size=15, route_color=random.choice(colors_arr))
                ax.plot(s_tup[0][0], s_tup[0][1], marker = 'o')
                ax.plot(d_tup[0][0], d_tup[0][1], marker = 'x')
            try:

                dir_dist, path_dist = get_agg_route_efficiency(G2, route, s_tup, d_tup)
                
                if path_dist != 0:  
                    re = dir_dist/path_dist
                    route_efficiency_arr.append(re)
                    if (print_statement):
                        print(f"Aggregate Route Efficiency Metric: {np.round(np.average(route_efficiency_arr), 2)}")
                else: 
                    pass
            except: 
                pass
        except: 
            pass 
             
    def route_button_press(val): 
            sn_path, s_tup, d_tup = get_coords(G2, bounds) 
            plot_route(G2, main_ax, sn_path, s_tup, d_tup)
             

    def auto_run(val): 

        with tqdm.trange(500) as bar: 
            bar.set_description("Computing...")
            for i in bar: 
                sn_path, s_tup, d_tup = get_coords(G2, bounds) 
                plot_route(G2, main_ax, sn_path, s_tup, d_tup, print_statement=False, show_route=False)
        print("Done")
         
        
    route_button.on_clicked(route_button_press)
    auto_button.on_clicked(auto_run)
    
    plt.show()


def histogram_plot(route_arr:list): 
    plt.hist(route_arr, bins=np.linspace(0,1,21,endpoint=True))
    plt.title("Route Efficiency Histogram")
    plt.show()

if __name__ == '__main__': 

    plot_map(place_name='City of London, UK')
    histogram_plot(route_efficiency_arr)