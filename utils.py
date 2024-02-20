

def get_euclidean_distance(coordinateA, coordinateB):
    differenceX = coordinateA[0] - coordinateB[0]
    differenceY = coordinateA[1] - coordinateB[1]
    print(differenceX,differenceY)
    return (differenceX * differenceX + differenceY * differenceY) ** 0.5

# Helper function of shortest path scheduling
def state_count(state):
    count = -1
    while state:
        count += state%2
        state //= 2
    return count



def shortest_paths_recommandation(spots, type_requirement):
    num_spots = len(spots)
    num_visiting = len(type_requirement)

    
    num_states = (2 ** num_spots)
    dp_state_single = [(1e18, -1)] * num_spots
    dp_states = []
    for _ in range(num_states):
        dp_states.append(dp_state_single.copy())
    # Enumerate all possibilities via State Compression Dynamic Programming
    for spot_id in range(num_spots):
        if spots[spot_id]['id'][0] == type_requirement[0]:
            dp_states[int(2 ** spot_id)][spot_id] = (0, 0)
    best_final_state = (1e18, 0, 0)
    
    

    for visit_order in range(1, num_visiting):
        for state in range(num_states):
            
            if state_count(state) != visit_order: continue
            for spot_id in range(num_spots):
                # disregard impossible state
                spot = spots[spot_id]
                if spot['id'][0] != type_requirement[visit_order] or int((2 ** spot_id) & state) == 0: continue
                past_state = state - int(2 ** spot_id)
                best_plan = (1e18, -1)
                for source_id in range(num_spots):
                    if (int(2 ** source_id) & past_state) == 0: continue
                    past_cost, past_endpoint = dp_states[past_state][source_id]
                    cur_cost = cost_criteria(spots[source_id], spots[spot_id])
                    if past_cost + cur_cost < best_plan[0]:
                        best_plan = (past_cost + cur_cost, source_id)
                dp_states[state][spot_id] = best_plan
                if visit_order == num_visiting - 1 and best_plan[0] < best_final_state[0]:
                    best_final_state = (best_plan[0], state, spot_id)
    # Retrieve optimal plan under criteria
    routes = []
    print(best_final_state[2])
    final_state = (best_final_state[1], best_final_state[2])
    while final_state[0]:
        spot_id = spots[final_state[1]]['id']
        routes = [spot_id] + routes
        next_state = (int(final_state[0] - (2 ** final_state[1])), dp_states[final_state[0]][final_state[1]][1])
        final_state = next_state

    return routes

