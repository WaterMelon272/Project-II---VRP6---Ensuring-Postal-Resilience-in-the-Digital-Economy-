import math
import heapq

def haversine_heuristic(node1, node2, graph):
    lat1, lon1 = graph.nodes[node1]['y'], graph.nodes[node1]['x']
    lat2, lon2 = graph.nodes[node2]['y'], graph.nodes[node2]['x']
    
    R = 6371000 # Bán kính Trái Đất (mét)
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    distance = R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    
    return distance

def astar(G, source, target, weight='length'):

    if source not in G or target not in G:
        raise ValueError("Nút không tồn tại trong bản đồ.")

    open_set = []
    heapq.heappush(open_set, (0, source))
    came_from = {}
    
    # Khoảng cách thực tế từ điểm bắt đầu đến node hiện tại
    g_score = {node: float('inf') for node in G.nodes}
    g_score[source] = 0
    
    # Ước lượng tổng quãng đường qua node này đến đích
    f_score = {node: float('inf') for node in G.nodes}
    f_score[source] = haversine_heuristic(source, target, G)

    while open_set:
        current_f, current_node = heapq.heappop(open_set)

        # Đã đến đích -> truy vết đường đi
        if current_node == target:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(source)
            return path[::-1]

        for neighbor in G.neighbors(current_node):
            edge_data = G.get_edge_data(current_node, neighbor)
            min_weight = float('inf')
            
            # Xử lý đa đồ thị của OSMnx
            for key in edge_data:
                if weight in edge_data[key]:
                    w = edge_data[key][weight]
                    if w < min_weight:
                        min_weight = w
            
            if min_weight == float('inf'): 
                continue

            tentative_g_score = g_score[current_node] + min_weight

            if tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current_node
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + haversine_heuristic(neighbor, target, G)
                
                heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # Hàng đợi rỗng nhưng chưa tới đích -> Không có đường nối
    raise Exception("NoPathFound")