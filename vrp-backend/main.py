from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import osmnx as ox
import networkx as nx
import math
import numpy as np
import random
from typing import List

from routing_astar import astar
from routing_ga import GeneticAlgorithmVRP 

app = FastAPI(title="VRP Routing AI Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

center_point = (21.0285, 105.8542) # Tọa độ Hồ Gươm 
radius_meters = 2500 # Tải tất cả con đường trong bán kính 2.5km quanh Hồ Gươm

graph = ox.graph_from_point(
    center_point, 
    dist=radius_meters, 
    network_type='drive'
)

class Location(BaseModel):
    id: str
    lat: float
    lng: float

class Vehicle(Location):
    type: str
    max_load: float

class Order(Location):
    demand: float

class DispatchRequest(BaseModel):
    vehicles: List[Vehicle]
    orders: List[Order]


class RouteRequest(BaseModel):
    start_lat: float
    start_lng: float
    end_lat: float
    end_lng: float

def get_dist_matrix(nodes_coords, graph):
    """Tính ma trận khoảng cách giữa tất cả các điểm bằng Dijkstra"""
    size = len(nodes_coords)
    matrix = np.zeros((size, size))
    
    # Map tọa độ sang node trong graph
    graph_nodes = []
    for lat, lng in nodes_coords:
        graph_nodes.append(ox.distance.nearest_nodes(graph, X=lng, Y=lat))
    
    for i in range(size):
        for j in range(size):
            if i == j:
                matrix[i][j] = 0
            else:
                try:
                    matrix[i][j] = nx.shortest_path_length(graph, graph_nodes[i], graph_nodes[j], weight='length')
                except nx.NetworkXNoPath:
                    matrix[i][j] = 1e9 # Khoảng cách vô hạn nếu không có đường
    return matrix


def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def get_nodes_within_radius(center_lat, center_lng, radius_m):
    nodes = []
    for node, data in graph.nodes(data=True):
        dist = haversine_distance(center_lat, center_lng, data['y'], data['x'])
        if dist <= radius_m:
            nodes.append(node)
    return nodes


def generate_route_data(num_warehouses=3, order_count=50):
    available_nodes = get_nodes_within_radius(center_point[0], center_point[1], radius_meters)
    if len(available_nodes) < num_warehouses + order_count:
        available_nodes = list(graph.nodes)

    warehouse_nodes = random.sample(available_nodes, min(num_warehouses, len(available_nodes)))
    warehouses = []
    vehicles = []
    used_nodes = set(warehouse_nodes)

    for idx, w_node in enumerate(warehouse_nodes):
        warehouses.append({
            'id': f'KH-{idx + 1}',
            'lat': graph.nodes[w_node]['y'],
            'lng': graph.nodes[w_node]['x'],
        })

    remaining_nodes = [node for node in available_nodes if node not in used_nodes]
    if len(remaining_nodes) < order_count:
        remaining_nodes = [node for node in graph.nodes if node not in used_nodes]

    order_nodes = random.sample(remaining_nodes, min(order_count, len(remaining_nodes)))
    orders = []
    total_demand = 0
    for idx, node in enumerate(order_nodes):
        demand = random.randint(2, 6)
        orders.append({
            'id': f'DH-{idx + 1}',
            'lat': graph.nodes[node]['y'],
            'lng': graph.nodes[node]['x'],
            'demand': demand,
        })
        total_demand += demand

    required_capacity = math.ceil(total_demand * 1.5)
    small_count = random.randint(3, 7)
    medium_count = random.randint(3, 6)
    large_count = random.randint(2, 5)
    total_capacity = small_count * 6 + medium_count * 12 + large_count * 20

    while total_capacity < required_capacity:
        if total_capacity + 20 <= required_capacity or random.random() < 0.6:
            large_count += 1
            total_capacity += 20
        elif total_capacity + 12 <= required_capacity:
            medium_count += 1
            total_capacity += 12
        else:
            small_count += 1
            total_capacity += 6

    total_vehicles = small_count + medium_count + large_count
    warehouse_cycle = [warehouse_nodes[i % len(warehouse_nodes)] for i in range(total_vehicles)]

    vehicle_id = 1
    for count, vehicle_type, max_load in [
        (small_count, 'Xe nhỏ', 6),
        (medium_count, 'Xe vừa', 12),
        (large_count, 'Xe lớn', 20),
    ]:
        for _ in range(count):
            warehouse_node = warehouse_cycle[vehicle_id - 1]
            warehouse_idx = warehouse_nodes.index(warehouse_node)
            vehicles.append({
                'id': f'XE-{vehicle_id:02d}',
                'lat': graph.nodes[warehouse_node]['y'],
                'lng': graph.nodes[warehouse_node]['x'],
                'type': vehicle_type,
                'max_load': max_load,
                'warehouse_id': f'KH-{warehouse_idx + 1}',
            })
            vehicle_id += 1

    return {
        'warehouses': warehouses,
        'vehicles': vehicles,
        'orders': orders,
    }

@app.get('/api/seed-data')
def seed_data():
    return generate_route_data()


def assign_orders_to_vehicles_via_ga(vehicles, orders, dist_matrix):
    num_vehicles = len(vehicles)
    num_orders = len(orders)

    vehicle_coords = [(vehicle.lat, vehicle.lng) for vehicle in vehicles]
    order_coords = [(order.lat, order.lng) for order in orders]
    vehicle_capacities = [vehicle.max_load for vehicle in vehicles]
    order_demands = [order.demand for order in orders]

    ga = GeneticAlgorithmVRP(
        vehicle_coords=vehicle_coords,
        order_coords=order_coords,
        vehicle_capacities=vehicle_capacities,
        order_demands=order_demands,
        pop_size=80,
        generations=120,
        mutation_rate=0.12,
        penalty_factor=10000,
    )

    assignment = ga.run()
    assignments = [[] for _ in vehicles]
    route_sequences = [[] for _ in vehicles]
    for order_idx, vehicle_idx in enumerate(assignment):
        assignments[vehicle_idx].append(order_idx)

    for v_idx in range(num_vehicles):
        route_sequences[v_idx] = build_order_sequence_for_vehicle(v_idx, assignments[v_idx], num_vehicles, dist_matrix)

    return assignments, route_sequences


def exact_assign_orders_to_vehicles(vehicles, orders, dist_matrix):
    num_vehicles = len(vehicles)
    num_orders = len(orders)

    if num_orders == 0:
        return [[] for _ in vehicles], [[] for _ in vehicles]

    order_demands = [order.demand for order in orders]

    if num_orders > 14:
        assignments, _ = assign_orders_to_vehicles_via_ga(vehicles, orders, dist_matrix)
        route_sequences = []
        for v_idx, assigned_orders in enumerate(assignments):
            if len(assigned_orders) <= 14:
                route_sequences.append(
                    solve_exact_vehicle_sequence(v_idx, assigned_orders, num_vehicles, dist_matrix)
                )
            else:
                route_sequences.append(
                    build_order_sequence_for_vehicle(v_idx, assigned_orders, num_vehicles, dist_matrix)
                )
        return assignments, route_sequences

    N = 1 << num_orders
    load = [0] * N
    for mask in range(1, N):
        b = (mask & -mask).bit_length() - 1
        load[mask] = load[mask ^ (1 << b)] + order_demands[b]

    INF = float('inf')
    subset_costs = [[INF] * N for _ in range(num_vehicles)]
    subset_sequences = [[None] * N for _ in range(num_vehicles)]

    def bit_iter(x):
        while x:
            lsb = x & -x
            yield lsb.bit_length() - 1
            x ^= lsb

    for v_idx, vehicle in enumerate(vehicles):
        capacity = vehicle.max_load
        dp = [[INF] * num_orders for _ in range(N)]
        parent = [[-1] * num_orders for _ in range(N)]

        for i in range(num_orders):
            mask = 1 << i
            dp[mask][i] = dist_matrix[v_idx][num_vehicles + i]

        for mask in range(1, N):
            for last in bit_iter(mask):
                if mask == (1 << last):
                    continue
                prev_mask = mask ^ (1 << last)
                for prev in bit_iter(prev_mask):
                    candidate = dp[prev_mask][prev] + dist_matrix[num_vehicles + prev][num_vehicles + last]
                    if candidate < dp[mask][last]:
                        dp[mask][last] = candidate
                        parent[mask][last] = prev

        for mask in range(1, N):
            if load[mask] > capacity:
                continue

            best_cost = INF
            best_last = -1
            for last in bit_iter(mask):
                total_cost = dp[mask][last] + dist_matrix[num_vehicles + last][v_idx]
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_last = last

            if best_cost < INF:
                subset_costs[v_idx][mask] = best_cost
                sequence = []
                current_mask = mask
                current_last = best_last
                while current_mask:
                    sequence.append(current_last)
                    prev = parent[current_mask][current_last]
                    current_mask ^= (1 << current_last)
                    current_last = prev
                subset_sequences[v_idx][mask] = list(reversed(sequence))

    full_mask = N - 1
    dp_assign = [[INF] * N for _ in range(num_vehicles + 1)]
    parent_choice = [[None] * N for _ in range(num_vehicles + 1)]
    dp_assign[0][0] = 0.0

    for v_idx in range(1, num_vehicles + 1):
        for mask in range(N):
            if dp_assign[v_idx - 1][mask] >= INF:
                continue
            rem = full_mask ^ mask
            s = rem
            while s:
                cost = subset_costs[v_idx - 1][s]
                if cost < INF:
                    new_mask = mask | s
                    candidate = dp_assign[v_idx - 1][mask] + cost
                    if candidate < dp_assign[v_idx][new_mask]:
                        dp_assign[v_idx][new_mask] = candidate
                        parent_choice[v_idx][new_mask] = (mask, s)
                s = (s - 1) & rem
            if dp_assign[v_idx - 1][mask] < dp_assign[v_idx][mask]:
                dp_assign[v_idx][mask] = dp_assign[v_idx - 1][mask]
                parent_choice[v_idx][mask] = (mask, 0)

    if dp_assign[num_vehicles][full_mask] >= INF:
        raise HTTPException(status_code=400, detail='Không tìm thấy lời giải CVRP chính xác với dữ liệu hiện tại.')

    assignments = [[] for _ in vehicles]
    route_sequences = [[] for _ in vehicles]
    current_mask = full_mask
    for v_idx in range(num_vehicles, 0, -1):
        choice = parent_choice[v_idx][current_mask]
        if choice is None:
            continue
        prev_mask, subset_mask = choice
        if subset_mask:
            assignments[v_idx - 1] = subset_sequences[v_idx - 1][subset_mask] or []
            route_sequences[v_idx - 1] = subset_sequences[v_idx - 1][subset_mask] or []
        current_mask = prev_mask

    return assignments, route_sequences


def solve_exact_vehicle_sequence(vehicle_idx, assigned_order_indices, num_vehicles, dist_matrix):
    if not assigned_order_indices:
        return []

    order_count = len(assigned_order_indices)
    if order_count == 1:
        return assigned_order_indices

    INF = float('inf')
    N = 1 << order_count
    dp = [[INF] * order_count for _ in range(N)]
    parent = [[-1] * order_count for _ in range(N)]

    def bit_iter(x):
        while x:
            lsb = x & -x
            yield lsb.bit_length() - 1
            x ^= lsb

    for idx, order_idx in enumerate(assigned_order_indices):
        mask = 1 << idx
        dp[mask][idx] = dist_matrix[vehicle_idx][num_vehicles + order_idx]

    for mask in range(1, N):
        for last in bit_iter(mask):
            if mask == (1 << last):
                continue
            prev_mask = mask ^ (1 << last)
            for prev in bit_iter(prev_mask):
                candidate = dp[prev_mask][prev] + dist_matrix[num_vehicles + assigned_order_indices[prev]][num_vehicles + assigned_order_indices[last]]
                if candidate < dp[mask][last]:
                    dp[mask][last] = candidate
                    parent[mask][last] = prev

    best_cost = INF
    best_last = -1
    full_mask = (1 << order_count) - 1
    for last in range(order_count):
        total_cost = dp[full_mask][last] + dist_matrix[num_vehicles + assigned_order_indices[last]][vehicle_idx]
        if total_cost < best_cost:
            best_cost = total_cost
            best_last = last

    sequence = []
    current_mask = full_mask
    current_last = best_last
    while current_mask and current_last != -1:
        sequence.append(assigned_order_indices[current_last])
        prev_last = parent[current_mask][current_last]
        current_mask ^= (1 << current_last)
        current_last = prev_last

    return list(reversed(sequence))


def assign_orders_to_vehicles(vehicles, orders, dist_matrix):
    return assign_orders_to_vehicles_via_ga(vehicles, orders, dist_matrix)


def build_order_sequence_for_vehicle(vehicle_idx, assigned_order_indices, num_vehicles, dist_matrix):
    if not assigned_order_indices:
        return []

    sequence = []
    remaining = set(assigned_order_indices)
    current_node = vehicle_idx

    while remaining:
        next_order = min(
            remaining,
            key=lambda order_idx: dist_matrix[current_node][num_vehicles + order_idx]
        )
        sequence.append(next_order)
        remaining.remove(next_order)
        current_node = num_vehicles + next_order

    return sequence


def build_dispatch_response(request: DispatchRequest, assignments, route_sequences, num_vehicles, all_coords, dist_matrix):
    assignments_payload = []
    order_eta_hours = {}

    for v_idx, vehicle in enumerate(request.vehicles):
        route_order_sequence = route_sequences[v_idx] if route_sequences[v_idx] else assignments[v_idx]
        route_points_indices = [v_idx] + [num_vehicles + idx for idx in route_order_sequence] + [v_idx]
        full_route_coords = []

        cumulative_distance = 0.0
        current_node_idx = v_idx
        for order_idx in route_order_sequence:
            cumulative_distance += dist_matrix[current_node_idx][num_vehicles + order_idx]
            order_eta_hours[request.orders[order_idx].id] = round(cumulative_distance / 1000.0 / 40.0, 2)
            current_node_idx = num_vehicles + order_idx

        for i in range(len(route_points_indices) - 1):
            start_node_idx = route_points_indices[i]
            end_node_idx = route_points_indices[i + 1]

            start_lat, start_lng = all_coords[start_node_idx]
            end_lat, end_lng = all_coords[end_node_idx]

            orig_node = ox.distance.nearest_nodes(graph, X=start_lng, Y=start_lat)
            dest_node = ox.distance.nearest_nodes(graph, X=end_lng, Y=end_lat)

            try:
                path_nodes = astar(graph, orig_node, dest_node, weight='length')
                path_coords = [[graph.nodes[n]['y'], graph.nodes[n]['x']] for n in path_nodes]

                if i > 0:
                    full_route_coords.extend(path_coords[1:])
                else:
                    full_route_coords.extend(path_coords)
            except Exception as e:
                print(f"Lỗi tìm đường: {e}")
                continue

        assigned_order_ids = [request.orders[idx].id for idx in route_order_sequence]
        assignments_payload.append({
            "vehicle_id": vehicle.id,
            "vehicle_type": vehicle.type,
            "max_load": vehicle.max_load,
            "orders": assigned_order_ids,
            "route": full_route_coords or [[vehicle.lat, vehicle.lng]]
        })

    return {
        "status": "success",
        "assignments": assignments_payload,
        "order_eta_hours": order_eta_hours
    }


@app.post("/api/dispatch/ga")
def dispatch_vehicles_ga(request: DispatchRequest):
    try:
        num_vehicles = len(request.vehicles)
        all_coords = [(v.lat, v.lng) for v in request.vehicles] + [(o.lat, o.lng) for o in request.orders]
        dist_matrix = get_dist_matrix(all_coords, graph)

        assignments, route_sequences = assign_orders_to_vehicles_via_ga(request.vehicles, request.orders, dist_matrix)
        return build_dispatch_response(request, assignments, route_sequences, num_vehicles, all_coords, dist_matrix)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/dispatch/exact")
def dispatch_vehicles_exact(request: DispatchRequest):
    try:
        num_vehicles = len(request.vehicles)
        all_coords = [(v.lat, v.lng) for v in request.vehicles] + [(o.lat, o.lng) for o in request.orders]
        dist_matrix = get_dist_matrix(all_coords, graph)

        assignments, route_sequences = exact_assign_orders_to_vehicles(request.vehicles, request.orders, dist_matrix)
        return build_dispatch_response(request, assignments, route_sequences, num_vehicles, all_coords, dist_matrix)
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/routing")
def get_optimal_route(request: RouteRequest):
    try:
        orig_node = ox.distance.nearest_nodes(graph, X=request.start_lng, Y=request.start_lat)
        dest_node = ox.distance.nearest_nodes(graph, X=request.end_lng, Y=request.end_lat)

        # Chạy thuật toán A*
        route_nodes = astar(
            G=graph, 
            source=orig_node, 
            target=dest_node, 
            weight='length'
        )

        # route_nodes = nx.astar_path(
        #     G=graph, 
        #     source=orig_node, 
        #     target=dest_node, 
        #     heuristic=haversine_heuristic, 
        #     weight='length'
        # )

        route_coords = [[graph.nodes[n]['y'], graph.nodes[n]['x']] for n in route_nodes]
        
        return {
            "status": "success",
            "message": "Tìm đường thành công",
            "total_nodes": len(route_coords),
            "route": route_coords
        }
        
    except nx.NetworkXNoPath:
        raise HTTPException(status_code=404, detail="Không tìm thấy đường đi bộ/xe máy giữa 2 điểm này.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/dispatch")
def dispatch_vehicles(request: DispatchRequest):
    return dispatch_vehicles_ga(request)
