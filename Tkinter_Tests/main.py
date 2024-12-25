import tkinter as tk 
from tkinter import Canvas, Button
import random
import time
import djikstra as dj
import tqdm 
import tkintermapview
import matplotlib.pyplot as plt 
import numpy as np 
from validation_procedure import all_checks, segment_node_type, prune_network


# Geometry stuff
WIDTH, HEIGHT= 1000, 600
draw_width, draw_height = WIDTH/2, HEIGHT/2
padding = 50

num_rows = 3
num_cols = 3

# Clicknum keeps track of whether you are creating or deleting a line
click_num = 0

root_tk = tk.Tk()
root_tk.geometry(f"{WIDTH}x{HEIGHT}")
root_tk.title("Canvas")

single_network = {}
temperorary_network = {}
multi_network = {}

lines_dict = {}
markers_dict = {}

# Create circle method (to make it easier later)
def _create_circle(self, x, y, r, **kwargs):
    return self.create_oval(x-r, y-r, x+r, y+r, **kwargs)

tk.Canvas.create_circle = _create_circle

# takes num of rows and cols and creates a grid on the draw frame (rxc)
def change_row_col(custom_row, custom_col): 

    global click_num
    global single_network
    global num_rows
    global num_cols
    global points_dict 

    click_num = 0 

    if custom_col > 2 and custom_row > 2: 
        num_rows = custom_row
        num_cols = custom_col

        draw_canvas.delete('all')
        single_network = {}
        points_dict = set_grid()
        return 
    else: 
        print('Invalid Dimensions!')
        return 


# clears the draw canvas (removes all lines and markers)
def clear_draw_canvas(): 
    global single_network
    global lines_dict
    global markers_dict
    global click_num 

    click_num = 0 

    single_network = {}

    for line in lines_dict.values(): 
        draw_canvas.delete(line)

    for (c1, c2) in markers_dict.values(): 
        draw_canvas.delete(c1)
        draw_canvas.delete(c2) 

# sets the grid initially
# points dict keeps track of the coords of these points
def set_grid(): 
    
    global num_rows
    global num_cols

    global padding

    points_dict = {}
    count = 0

    p_dist = (draw_height - 2*padding)/(num_rows-1)
    v_offset = padding
    h_offset = (draw_width - (p_dist *(num_cols - 1)))/2

    for j in range(num_cols): 
        for i in range(num_rows): 
            x_c = h_offset + j*p_dist
            y_c = v_offset + i*p_dist

            points_dict[count] = (x_c, y_c)
            count += 1
            draw_canvas.create_circle(x_c, y_c, 5, fill = 'black')
    
    return points_dict

def closest_coord(x1: float, y1:float, points_dict:dict): 
    
    p_dist = (draw_height - 2*padding)/(num_rows-1)

    v_offset = padding
    h_offset = (draw_width - (p_dist *(num_cols - 1)))/2


    _, res_coord = min(points_dict.items(), key=lambda x: ((x1 - x[1][0])**2 + (y1 - x[1][1])**2))

    res_key = tuple((res_coord[0] - h_offset, res_coord[1]- v_offset))

    return res_key, res_coord

def add_path_to_network(id1, id2, dist, **kwargs): 
    global single_network

    if id1 in single_network: 
        l1 = single_network[id1]
        l1.append((id2, dist))
        single_network[id1] = l1
    else: 
        single_network[id1] = [(id2, dist)]

    if id2 in single_network: 
        l2 = single_network[id2]
        l2.append((id1, dist))
        single_network[id2] = l2
    else: 
        single_network[id2] = [(id1, dist)]

def del_path_from_network(id1, id2, dist): 
    global single_network

    l1 = single_network[id1]
    l1.remove((id2, dist))

    l2 = single_network[id2]
    l2.remove((id1, dist))

    if l1 == None: 
        l1 = []
    if l2 == None: 
        l2 = []

    single_network[id1] = l1
    single_network[id2] = l2
    
    
    pass
def draw_line(event): 

    global click_num 
    global x1, y1 
    global id1
    global is_draw 
    global single_network
    global lines_dict
    global markers_dict 
        
    if click_num == 0:

        x1=event.x
        y1=event.y

        id1, (x1, y1) = closest_coord(x1, y1, points_dict)

        start_circle = draw_canvas.create_circle(x1, y1, 8, fill = 'green')
        draw_canvas.after(150, lambda x=start_circle: draw_canvas.delete(x))

        click_num += 1

    elif click_num == 1:
        x2=event.x
        y2=event.y
        id2, (x2, y2) = closest_coord(x2, y2, points_dict)
        
        if x2 == x1 and y2 == y1: 
            return
        
        start_circle = draw_canvas.create_circle(x2, y2, 8, fill = 'green')
        draw_canvas.after(150, lambda x=start_circle: draw_canvas.delete(x))
        
        dist = ((x1-x2)**2 + (y1 - y2)**2)**0.5

        add_path_to_network(id1, id2, dist)
        
        new_line = draw_canvas.create_line(x1,y1,x2,y2, fill="orange", width=3)
        p1_circle = draw_canvas.create_circle(x1, y1, 3, fill = 'orange')
        p2_circle = draw_canvas.create_circle(x2, y2, 3, fill = 'orange')
        

        lines_dict[f'{id1} + {id2}'] = new_line
        markers_dict[f'{id1} + {id2}'] = (p1_circle, p2_circle)

        click_num = 0 
    else: 
        click_num = 0 

    
def delete_line(event): 

    global click_num 
    global x1, y1 
    global id1
    global is_draw 
    global single_network
    global lines_dict
    global markers_dict


    try:
        if click_num == 0:
            x1=event.x
            y1=event.y

            id1, (x1, y1) = closest_coord(x1, y1, points_dict)

            start_circle = draw_canvas.create_circle(x1, y1, 8, fill = 'red')
            draw_canvas.after(150, lambda x=start_circle: draw_canvas.delete(x))

            click_num -= 1

        elif click_num == -1:
            x2=event.x
            y2=event.y
            id2, (x2, y2) = closest_coord(x2, y2, points_dict)
            
            start_circle = draw_canvas.create_circle(x2, y2, 8, fill = 'red')
            draw_canvas.after(150, lambda x=start_circle: draw_canvas.delete(x))
            
            dist = ((x1-x2)**2 + (y1 - y2)**2)**0.5
            
            try: 
                del_line = lines_dict[f'{id1} + {id2}']
                (dp1_circle, dp2_circle) = markers_dict[f'{id1} + {id2}']
            except: 
                del_line = lines_dict[f'{id2} + {id1}']
                (dp1_circle, dp2_circle) = markers_dict[f'{id2} + {id1}']
            
            draw_canvas.delete(del_line)
            draw_canvas.delete(dp1_circle)
            draw_canvas.delete(dp2_circle)

            del_path_from_network(id1, id2, dist)
            click_num = 0
        else: 
            click_num = 0
    except Exception as ex: 
        print(ex)

def re_weight_network(w_param = 1): 

    # We want to incorporate intersection weighting. Nodes with lots of intersections will be penalised 

    # The weights will be node specific and directional, travelling from a node with a high intersection weight will change the overall weight 
    # but travelling towards a high intersection node wont (e.g if the destination is a high intersection node - route is not penalised)
    
    # We assign intersection weight depending on number of intersections of that node 
    #       Node with 1 or 2 intersections will not be rescaled (represents a path or a leaf - like a straight road)
    #       Node with 4 intersections will be scaled by 2
    #       Node with 8 intersections will be scaled by 4

    # We take num_intersections and divide by 2 to get the rescale val. If the value is less than 1 - we round up to 1 (only when num == 1) 
    # We now take this weight and multiply by w_param to 'rescale' the effects of intersections. Any final weight less than 1 is automatically set to 1. 

    # Setting w_param = 0 will essentially nullify the effect of intersections on capacity - this will mean no reweighting is done
    # Setting w_param < 1 will prioritise low path distances
    # Setting w_param = 1 (default) will mean the rule described above (4 intersections halves capacity - doubles weights). 
    # Setting w_param > 1 will prioritise low intersection number networks 

    global multi_network
    w_param = W_PARAM.get()

    for node in multi_network: 
        # node list is a list of tuples: [] -> where each element in the list is in the form: ((next_node_x, next_node_y), weight) 
        node_list = list(multi_network[node]) 
        hist_list = []

        for i in node_list: 
            if i in hist_list: pass 
            else: hist_list.append(i)
       
        weight_coeff = len(hist_list)/2
        weight_coeff *= w_param

        if weight_coeff < 1 : weight_coeff  = 1

        temp_list = []
        
        for element in node_list: 
            temp_list.append((element[0], abs(element[1]*weight_coeff)))
        
        multi_network[node] = temp_list



def horizontal_tessellate(d, i, seed_network, set_h, do_plot = True):
    global multi_network
    global num_cols
    global num_rows

    temp_network = {}

    for key in seed_network.keys(): 
        t_list = seed_network[key]

        x1, y1 = key[0] + d*i*(num_cols-1), key[1]

        modified_key = (x1, y1)
        modified_list = []

        for l_tuple in t_list: 
            x2, y2 = l_tuple[0][0] + d*i*(num_cols-1), l_tuple[0][1]
            modified_tuple = ((x2, y2), l_tuple[1]) 
            modified_list.append(modified_tuple)
            if do_plot: 
                tesselate_canvas.create_line(x1, y1, x2, y2, fill='light grey', width = 0.5)
                tesselate_canvas.create_circle(x1, y1, 1, fill = 'black')
                tesselate_canvas.create_circle(x2, y2, 1, fill = 'black')
        
        temp_network[modified_key] = modified_list

    for key in temp_network.keys(): 
        if key in multi_network: 
            l1 = multi_network[key]
            l2 = temp_network[key]

            l3 = l1 + l2
            temp_network[key] = l3
    
    multi_network = multi_network|temp_network
    
    if (i < set_h - 1): 
        horizontal_tessellate(d, i + 1, seed_network, set_h)
    else: 
        return
    
def vertical_tessellate(d, i, seed_network, set_v, do_plot = True): 
    global multi_network
    global num_rows
    global num_cols
    
    temp_network = {}

    for key in seed_network.keys(): 
        t_list = seed_network[key]

        x1, y1 = key[0], key[1] + d*i*(num_rows-1)

        modified_key = (x1, y1)
        modified_list = []

        for l_tuple in t_list: 
            x2, y2 = l_tuple[0][0], l_tuple[0][1]+ d*i*(num_rows-1)
            modified_tuple = ((x2, y2), l_tuple[1]) 
            modified_list.append(modified_tuple)
            
            if do_plot: 
                tesselate_canvas.create_line(x1, y1, x2, y2, fill='light grey', width = 1)
                tesselate_canvas.create_circle(x1, y1, 1, fill = 'black')
                tesselate_canvas.create_circle(x2, y2, 1, fill = 'black')

        
        temp_network[modified_key] = modified_list

    for key in temp_network.keys(): 
        if key in multi_network: 
            l1 = multi_network[key]
            l2 = temp_network[key]

            l3 = l1 + l2
            temp_network[key] = l3
    
    multi_network = multi_network|temp_network
    if (i < set_v - 1): 
        vertical_tessellate(d, i + 1, seed_network, set_v)
    else: 
        return

def generate_seed_network(h_offset, v_offset, rescale_val): 
    global single_network
    global multi_network

    seed_network = {}

    for key in single_network.keys(): 

        t_list = single_network[key]
        x1, y1 = key[0] * rescale_val + h_offset, key[1]*rescale_val + v_offset

        modified_key = (x1, y1)
        modified_list = []

        for l_tuple in t_list: 
            x2, y2 = l_tuple[0][0]*rescale_val + h_offset, l_tuple[0][1]*rescale_val + v_offset
            modified_tuple = ((x2, y2), rescale_val*l_tuple[1]) 
            modified_list.append(modified_tuple)
            tesselate_canvas.create_line(x1, y1, x2, y2, fill='black', width = 1)
        
        seed_network[modified_key] = modified_list
    
    return seed_network


def tessellate_graph(canvas_width, canvas_height, w_param = 1): 
    global single_network   
    global multi_network
    global num_rows
    global num_cols
    global padding 

    tesselate_canvas.delete('all')

    p_dist = (canvas_height - 2*padding)/(num_rows-1)
    
    seed_network = {}    
    
    try: 
        set_h, set_v = int(H.get()), int(V.get())
        if set_h > 0 and set_v > 0: 
            pass
        else: 
            print("Values Cannot be < 1 !!")
            return
    except Exception as ex: 
        print(ex)
        return 
    
    h_d = ((canvas_width - 2*padding)/set_h)/(num_cols - 1)
    v_d = ((canvas_height - 2*padding)/set_v)/(num_rows - 1)

    d = min(h_d, v_d)

    rescale_val = d/p_dist
    h_offset = (canvas_width - d*set_h*(num_cols-1))/2
    v_offset = (canvas_height - d*set_v*(num_rows-1))/2

    seed_network = generate_seed_network(h_offset, v_offset, rescale_val)
    # Begin tesselation
    multi_network = seed_network
    # Horizontal tesselation

    horizontal_tessellate(d, 0, seed_network, set_h)
    seed_network = multi_network
    vertical_tessellate(d, 0, seed_network, set_v)

    re_weight_network(w_param)

def validate(print_out = False): 
    global temperorary_network
    global num_rows
    global num_cols
    global padding
    global single_network
    global draw_width
    global draw_height
 
    temperorary_network = {}


    temperorary_network = single_network.copy()
    bool = all_checks(temperorary_network, num_rows, num_cols, padding, draw_width, draw_height, print_out)

    return bool

def use_multinetwrok(): 
    # Just for debugging
    
    global multi_network

    for node in multi_network: 
        l_node = multi_network[node]
        for (dest, weight) in l_node: 

            (node_x, node_y) = node
            (dest_x, dest_y) = dest

            tesselate_canvas.create_line(node_x, node_y, dest_x, dest_y, fill = 'red', width= 2)


def random_route_finder(show_route = True, mc_simulation = False, monte_carlo_iters = 100, monte_carlo_plot_show = True): 
    global multi_network

    if validate(): 
        if not mc_simulation: 
            colors = ['red', 'green', 'blue', 'orange', 'light blue', 'pink', 'purple']

            p1 , p2 = dj.choose_random_points(multi_network)

            dist_dict, last_hop_dict = dj.djikstra_alg(multi_network, p1, p2)
            path_stack = dj.return_path(last_hop_dict, p1, p2)
            euclid_dist = dj.euclidean_dist(p1, p2)


            prev_point = path_stack.pop()
            rand_color = random.choice(colors)
            while len(path_stack) > 0: 

                curr_point = path_stack.pop()

                if (show_route): 
                    (xp, yp) = prev_point
                    (xc, yc) = curr_point
                    tesselate_canvas.create_line(xp,yp, xc, yc, fill=rand_color, width=1.5)

                prev_point = curr_point

            try:
                eta = euclid_dist/dist_dict[p2]
            except: pass

            return eta
        else: 
            
            eta_list = []
            with tqdm.trange(monte_carlo_iters) as bar: 
                bar.set_description("Computing...")
                for i in bar: 
                    p1, _ = dj.choose_random_points(multi_network)
                    dist_dict, _ = dj.djikstra_alg(multi_network, p1, None)

                    for key in dist_dict: 
                        try: 
                            d = dj.euclidean_dist(p1, key)
                            if d is None: 
                                continue
                            path_d = dist_dict[key]
                            eta_list.append(d/path_d)
                        except OverflowError: 
                            pass
            
            eta_list = [x for x in eta_list if x != 0]

            if monte_carlo_plot_show:
                plt.figure(figsize=(5,5))
                plt.hist(eta_list, bins=np.linspace(0, 1, 21, endpoint=True))
                plt.title("Route Efficiency Histogram")
                plt.show()

                print(np.nanmean(eta_list))
            return eta_list

    else: 
        print('Invalid Tessellation')
        return None

def alpha_sweep(bounds: tuple = (1, 10), w_param = 0, sweep_iters = 10): 

    # Alpha is H/V value
    global single_network
    global multi_network

    set_h = 50

    min_alpha = bounds[0]
    max_alpha = bounds[1]
    alpha_step = (max_alpha - min_alpha)/sweep_iters

    p_dist = (draw_height - 2*padding)/(num_rows-1)

    avg_eta = []

    for i in range(sweep_iters): 
        
        print(f'Iteration {i+1}/{sweep_iters}'.center(100))
        print('\n')
        curr_alpha = min_alpha + i * alpha_step
        set_v = int(set_h/curr_alpha)

        multi_network = single_network
        horizontal_tessellate(p_dist, 0, single_network, set_h, False)
        vertical_tessellate(p_dist, 0, multi_network, set_v, False)

        re_weight_network(w_param)
        
        eta_list = random_route_finder(mc_simulation=True, monte_carlo_plot_show=False, monte_carlo_iters=100)
        eta = np.nanmean(eta_list)

        print(f'Eta Value = {eta}'.center(100))
        avg_eta.append(eta)
        print('\n')

    
    plt.plot(list(np.linspace(min_alpha, max_alpha, sweep_iters)), avg_eta)
    plt.show()



draw_frame = tk.Frame(root_tk, width=draw_width, height=draw_height, bg='grey')
tesselate_frame = tk.Frame(root_tk, width=WIDTH, height=draw_height, bg = 'blue')
controls_frame = tk.Frame(root_tk, width=draw_width, height=draw_height, bg='light grey')
draw_canvas=Canvas(draw_frame, width=draw_width, height=draw_height, background="white")
tesselate_canvas = Canvas(tesselate_frame, width=WIDTH, height=draw_height, background='white')

tesselate_frame.pack(side='bottom')
draw_frame.pack(side = 'right')
controls_frame.pack(side='left')
draw_canvas.pack()
tesselate_canvas.pack()

title = tk.Label(controls_frame, text="Controls Panel", font=('Helvetica', 12, 'bold'), padx = 1, pady = 1, bg='light grey', borderwidth=2)
title.place(relx=0.05, rely=0.1, anchor='nw')

H = tk.IntVar()
H.set(15)
V = tk.IntVar()
V.set(5)
W_PARAM = tk.DoubleVar()
W_PARAM.set(1.0)


custom_row = tk.IntVar()
custom_row.set(num_rows)
custom_col = tk.IntVar()
custom_col.set(num_cols)

tk.Entry(controls_frame, width = 10, textvariable=H).place(relx=0.05, rely=0.25)
H_label = tk.Label(controls_frame, text='H-Value', padx = 1, pady = 1, bg = 'light grey', ).place(relx=0.25, rely=0.25)

tk.Entry(controls_frame, width = 10, textvariable=custom_row).place(relx=0.5, rely=0.25)
row_Label = tk.Label(controls_frame, text='Set Num Rows', padx = 1, pady = 1, bg = 'light grey').place(relx=0.7, rely=0.25)

tk.Entry(controls_frame, width = 10, textvariable=V).place(relx=0.05, rely=0.35)
V_label = tk.Label(controls_frame, text='V-Value', padx = 1, pady = 1, bg = 'light grey').place(relx=0.25, rely=0.35)

tk.Entry(controls_frame, width = 10, textvariable=custom_col).place(relx=0.5, rely=0.35)
row_Label = tk.Label(controls_frame, text='Set Num Cols', padx = 1, pady = 1, bg = 'light grey').place(relx=0.7, rely=0.35)

Tesselate_Bttn = tk.Button(controls_frame, text = 'Tesselate', command=lambda: tessellate_graph(WIDTH, draw_height, W_PARAM), padx=1, pady=1).place(relx=0.05, rely=0.5)
Clear_Bttn = tk.Button(controls_frame, text = 'Clear', command = lambda: clear_draw_canvas(), padx=1, pady=1).place(relx=0.2, rely=0.5)
CustomDim_Bttn = tk.Button(controls_frame, text = 'Set Custom Dim', command=lambda: change_row_col(custom_row.get(), custom_col.get())).place(relx=0.3, rely=0.5)
Alpha_sweep_Bttn = tk.Button(controls_frame, text = 'Alpha Sweep', command=lambda: alpha_sweep()).place(relx=0.55, rely=0.5)

Validate_Bttn = tk.Button(controls_frame, text='Validate Net', command = lambda: validate(print_out = True), padx=1, pady=1).place(relx=0.05, rely=0.6)
Mnet_Bttn = tk.Button(controls_frame, text='Use Multi Net', command = lambda: use_multinetwrok(), padx=1, pady=1).place(relx=0.225, rely=0.6)
RndRoute_Bttn = tk.Button(controls_frame, text='Rand Route', command = lambda: random_route_finder(), padx=1, pady=1).place(relx=0.425, rely=0.6)
R_ansys_Bttn = tk.Button(controls_frame, text='Run MC simulation', command = lambda: random_route_finder(mc_simulation = True), padx=1, pady=1).place(relx=0.6, rely=0.6)
W_param_slider = tk.Scale(controls_frame, from_=0, to = 2, resolution=0.1, length=draw_width/2, label='W Param', orient='horizontal', bg='light grey', variable=W_PARAM).place(relx=0.05, rely=0.75)

is_draw = True


points_dict = set_grid()

draw_canvas.bind('<Button-1>', draw_line)
draw_canvas.bind('<Button-3>', delete_line)

root_tk.mainloop()
