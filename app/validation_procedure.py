import numpy as np 
import random 
import time

check1_bool = False 
check2_bool = False
check3_bool = False
check4_bool = False
check5_bool = False

f_prec = 8


def all_checks(single_network: dict, num_rows, num_cols, padding, draw_width, draw_height, print_out = False): 
    
    global check1_bool
    global check2_bool
    global check3_bool
    global check4_bool
    global check5_bool
    
    temp_network = {}

    for key in single_network: 
        new_key = (np.round(key[0], f_prec), np.round(key[1], f_prec))
        item_list = []
        for item in single_network[key]: 
            item_list.append(((np.round(item[0][0], f_prec), np.round(item[0][1], f_prec)),item[1]))
        
        temp_network[new_key] = item_list
    
    check1_bool = False 
    check2_bool = False
    check3_bool = False
    check4_bool = False
    check5_bool = False

    check2345(temp_network, num_rows, num_cols, padding, draw_width, draw_height)
    check1(temp_network, 0)

    if (print_out): 
        check_list = [check1_bool, check2_bool, check3_bool, check4_bool, check5_bool]
        print('CHECK LIST')
        for num, bool in enumerate(check_list): 
            print("Check ", num + 1, " : ", bool)
        print('\n')

    return (check1_bool and check2_bool and check3_bool and check4_bool and check5_bool)

    
def segment_node_type(num_rows, num_cols, padding, draw_width, draw_height): 

    points_list = []

    face_points = []
    
    tl_corner, tr_corner, bl_corner, br_corner = None, None, None, None

    left_face_points = []
    right_face_points = []

    top_face_points = []
    bot_face_points = []

    corner_points = []
    inner_points = []


    p_dist = (draw_height - 2*padding)/(num_rows-1)   

    for j in range(num_cols): 
        for i in range(num_rows): 
            x_c = j*p_dist
            y_c = i*p_dist

            points_list.append((np.round(x_c, f_prec), np.round(y_c, f_prec)))
    

    min_x = 0
    max_x = (num_cols - 1)*p_dist

    min_y = 0
    max_y = (num_rows - 1)*p_dist

    for point in points_list: 
        (tx, ty) = point

        if tx in (min_x, max_x) and ty in (min_y, max_y): 
            corner_points.append(point)
        elif tx in (min_x, max_x): 
            face_points.append(point)
        elif ty in (min_y, max_y): 
            face_points.append(point)
        else: 
            inner_points.append(point)
    
    for point in face_points: 
        (tx, ty) = point

        if tx == min_x: 
            left_face_points.append(point)
        elif tx == max_x: 
            right_face_points.append(point)
        elif ty == min_y: 
            top_face_points.append(point)
        else: 
            bot_face_points.append(point)
    
    
    #corner_points = [tl_corner, bl_corner, tr_corner, br_corner]
    return corner_points, left_face_points, right_face_points, top_face_points, bot_face_points, inner_points

def prune_network(single_network:dict):

    new_network = single_network 

    for key in list(new_network):
        l1 = new_network[key]
        if len(l1) == 0: 
            del new_network[key]
        else: 
            pass

    return new_network

def check1(single_network: dict, f_count): 

    global check1_bool

    anchor_history = []

    if len(list(single_network)) < 1: 
        return
    
    anchor = None 

    # Prune the single_network (remove empty lists)
    # Checks if network has any C0 discontinuities
    for key in list(single_network):
        l1 = single_network[key]
        if len(l1) == 0: 
            del single_network[key]
        elif len(l1) >= 2: 
            anchor = key
            break
        else: 
            pass
    
    # How to handle when tree is reduced to two connected nodes in true and false case
    if anchor == None : 
        count = 0
        for key in single_network.keys(): 
            l1 = single_network[key]
            if len(l1) > 0: 
                count += 1
        if count > 2: 
            return 
        else: 
            check1_bool = True
            return 
   
    prev_node = anchor
    curr_node = single_network[anchor][1][0]
    anchor_history.append(anchor)

    def forwards(anchor, prev_node, curr_node, f_count = 0): 
        
        if  f_count > 800: 
            print(anchor_history)
            print('overrun')
            return None 
        # if anchor we want to repeat and set a new anchor point
        (bool_anchor, ind_anchor) = check_if_anchor(single_network, curr_node, prev_node, anchor_history)
        (bool_path, next_node) = check_if_path(single_network, curr_node, prev_node, anchor_history)

        if bool_anchor: 
            new_anchor = curr_node
            anchor_history.append(new_anchor)
            next_node = single_network[new_anchor][ind_anchor][0]

            new_prev = curr_node
            new_curr = next_node

            forwards(new_anchor, new_prev, new_curr, f_count + 1)

        # if path node we just want to move
        elif bool_path:

            anchor = anchor
            new_prev = curr_node
            new_curr = next_node

            forwards(anchor, new_prev, new_curr, f_count + 1)

        else:  
            backwards(single_network, curr_node)
    
    def backwards(single_network: dict, leaf): 
        try: 
            del single_network[leaf]

            # remove child pointer from every key's value
            for key in single_network.keys(): 
                l = single_network[key]
                l = [x for x in l if x[0] != leaf]
                single_network[key] = l
            
        except: 
            pass
        check1(single_network, f_count + 1)
        

    def check_if_anchor(single_network, key, prev_key, anchor_history): 
        
        key_list = list(single_network[key])
        path_index = None

        count = 0
        for i, element in enumerate(key_list):  
            if element[0] not in anchor_history and element[0] != prev_key: 
                path_index = i
                count += 1
        
        if count > 1: 
            return (True, path_index)
        else: 
            return (False, None)
    
    def check_if_path(single_network, key, prev_key, anchor_history): 
        
        key_list = list(single_network[key])
        forward_path = None

        count = 0
        for element in key_list:  
            if element[0] != prev_key: 
                if element[0] not in anchor_history: 
                    count += 1
                    forward_path = element[0]
        
        if count == 1: 
            return (True, forward_path)
        else: 
            return (False, None)

    forwards(anchor, prev_node, curr_node, f_count + 1)

def check2345(single_network: dict, num_rows, num_cols, padding, draw_width, draw_height): 

    global check2_bool
    global check3_bool
    global check4_bool
    global check5_bool

    check_network = prune_network(single_network)

    corner_points, left_face_points, right_face_points, top_face_points, bot_face_points, inner_points = segment_node_type(num_rows, num_cols, padding, draw_width, draw_height)
    tl_corner, bl_corner, tr_corner, br_corner = corner_points[0], corner_points[1], corner_points[2], corner_points[3]

    # Check all inner points are connected
    for point in inner_points: 
        if point in check_network: 
            check2_bool = True
        else: 
            check2_bool = False
            break
    
    # Check at least one corner point is connected
    for point in corner_points: 
        if point in check_network: 
            check3_bool = True
            break 
        else:
            pass 
    
    # horizontal traversal check 
        
    # OR condition: 
    
    for l_point, r_point in zip(left_face_points, right_face_points): 
        if (l_point in check_network) or (r_point in check_network): 
            check4_bool = True
        else: 
            check4_bool = False
            break
    
    # AND condition: 
    
    if check4_bool: 
        check4_bool = False
        for l_point, r_point in zip(left_face_points, right_face_points): 
            if l_point in check_network and r_point in check_network: 
                check4_bool = True
                break
    
        if not check4_bool:         
            if (tl_corner in check_network and tr_corner in check_network) or (bl_corner in check_network and br_corner in check_network): 
                check4_bool = True
   
    
    # vertical traversal check
    # OR condition: 
                    
    for t_point, b_point in zip(top_face_points, bot_face_points): 
        if (t_point in check_network) or (b_point in check_network):
            check5_bool = True
        else: 
            check5_bool = False
            break
    
    # AND condition: 
    
    if check5_bool: 
        check5_bool = False
        for t_point, b_point in zip(top_face_points, bot_face_points): 
            if (t_point in check_network) & (b_point in check_network): 
                check5_bool = True
                break
    
        if not check5_bool: 
            if (tl_corner in check_network and bl_corner in check_network) or (tr_corner in check_network and br_corner in check_network): 
                check5_bool = True

if __name__ == "__main__": 
    
   pass