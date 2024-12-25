import numpy as np 
import heapq
import random 

test_graph = {
    'A': (('B', 5),('C', 1)),
    'B': (('A', 5), ('C', 2),('D', 1)),
    'C': (('A', 1), ('B', 2), ('D', 4), ('E', 8)),
    'D': (('B', 1), ('C', 4), ('E', 3)),
    'E': (('C', 8), ('D', 3))
}

def choose_random_points(multi_network: dict): 
    p1 = random.choice(list(multi_network.keys()))
    p2 = random.choice(list(multi_network.keys()))

    if len(list(multi_network[p1])) == 0 or len(list(multi_network[p2])) == 0: 
        print('None returned - pruning required')
        return None, None
    else: 
        return p1, p2

def euclidean_dist(p1, p2): 

    if p1 is None or p2 is None: 
        return None
    (x1, y1) = p1 
    (x2, y2) = p2

    d = np.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return d 
def djikstra_alg(multi_network: dict, source, dest, max_iterations = 1_000_000): 

    # need source target rejection if they are on min-max border
    count = 0
    
    distances = {node : float('inf') for node in multi_network}
    last_hop = {node: None for node in multi_network}
    
    last_hop[source] = source
    distances[source] = 0

    current_node = None

    pq = [(0, source)]

    if dest is None: 
        while pq and count < max_iterations: 
            current_dist, current_node = heapq.heappop(pq)  
            count += 1
            if current_dist > distances[current_node]: 
                continue 
            try: 
                for (next_node, weight) in multi_network[current_node]:
                    dist = current_dist + weight
                    if dist < distances[next_node]: 
                        distances[next_node] = dist
                        last_hop[next_node] = current_node
                        heapq.heappush(pq, (dist, next_node))
            except: pass 

    else: 
        while current_node != dest and count < max_iterations: 
            current_dist, current_node = heapq.heappop(pq)  
            count += 1
            if current_dist > distances[current_node]: 
                continue 
            for (next_node, weight) in multi_network[current_node]:
                dist = current_dist + weight
                if dist < distances[next_node]: 
                    distances[next_node] = dist
                    last_hop[next_node] = current_node
                    heapq.heappush(pq, (dist, next_node))

    return distances, last_hop

def return_path(last_hop, source, dest): 
        
    call_stack = []
    current_node = dest

    while current_node != source: 
        
        call_stack.append((current_node))
        current_node = last_hop[current_node]
    
    call_stack.append(source)
    
    return call_stack

if __name__ == '__main__': 
    d,l = djikstra_alg(test_graph, 'A', 'D')
    print(d)
    c = return_path(l, 'A', 'D')
    print(c)

