import math
import random

class GeneticAlgorithmVRP:
    def __init__(
        self,
        vehicle_coords,
        order_coords,
        vehicle_capacities,
        order_demands,
        pop_size=80,
        generations=120,
        mutation_rate=0.1,
        penalty_factor=10000,
    ):
        self.vehicle_coords = vehicle_coords
        self.order_coords = order_coords
        self.vehicle_capacities = vehicle_capacities
        self.order_demands = order_demands
        self.num_vehicles = len(vehicle_coords)
        self.num_orders = len(order_coords)
        self.pop_size = pop_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.penalty_factor = penalty_factor
        self.bird_dist_matrix = self._build_bird_distance_matrix()
        self.bird_dist_matrix_order_order = self._build_bird_order_distance_matrix()

    def _haversine(self, lat1, lon1, lat2, lon2):
        R = 6371000
        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)
        a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
        return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    def _build_bird_distance_matrix(self):
        matrix = [[0.0] * self.num_orders for _ in range(self.num_vehicles)]
        for v_idx, (v_lat, v_lng) in enumerate(self.vehicle_coords):
            for o_idx, (o_lat, o_lng) in enumerate(self.order_coords):
                matrix[v_idx][o_idx] = self._haversine(v_lat, v_lng, o_lat, o_lng)
        return matrix

    def _build_bird_order_distance_matrix(self):
        matrix = [[0.0] * self.num_orders for _ in range(self.num_orders)]
        for i, (lat_i, lng_i) in enumerate(self.order_coords):
            for j, (lat_j, lng_j) in enumerate(self.order_coords):
                matrix[i][j] = self._haversine(lat_i, lng_i, lat_j, lng_j)
        return matrix

    def _create_feasible_individual(self):
        individual = [-1] * self.num_orders
        remaining_capacity = list(self.vehicle_capacities)
        order_indices = sorted(range(self.num_orders), key=lambda i: self.order_demands[i], reverse=True)
        loads = [0.0] * self.num_vehicles

        for order_idx in order_indices:
            feasible_vehicles = [v for v in range(self.num_vehicles) if remaining_capacity[v] >= self.order_demands[order_idx]]
            if feasible_vehicles:
                feasible_vehicles.sort(
                    key=lambda v: self.bird_dist_matrix[v][order_idx] + 0.12 * (loads[v] / max(1.0, self.vehicle_capacities[v]))
                )
                chosen = feasible_vehicles[0]
                if len(feasible_vehicles) > 1 and random.random() < 0.3:
                    chosen = random.choice(feasible_vehicles[:2])
                individual[order_idx] = chosen
            else:
                individual[order_idx] = random.randrange(self.num_vehicles)

            remaining_capacity[individual[order_idx]] -= self.order_demands[order_idx]
            loads[individual[order_idx]] += self.order_demands[order_idx]

        return individual

    def _estimate_route_stats(self, vehicle_idx, assigned_orders):
        if not assigned_orders:
            return 0.0, 0.0

        remaining = set(assigned_orders)
        current_order = None
        route_distance = 0.0
        total_delivery_distance = 0.0
        current_distance = 0.0

        # Start from warehouse to first order
        first_order = min(
            remaining,
            key=lambda o: self.bird_dist_matrix[vehicle_idx][o]
        )
        distance_to_first = self.bird_dist_matrix[vehicle_idx][first_order]
        route_distance += distance_to_first
        current_distance += distance_to_first
        total_delivery_distance += current_distance
        current_order = first_order
        remaining.remove(first_order)

        while remaining:
            next_order = min(
                remaining,
                key=lambda o: self.bird_dist_matrix_order_order[current_order][o]
            )
            segment = self.bird_dist_matrix_order_order[current_order][next_order]
            route_distance += segment
            current_distance += segment
            total_delivery_distance += current_distance
            current_order = next_order
            remaining.remove(next_order)

        # Return to warehouse
        route_distance += self.bird_dist_matrix[vehicle_idx][current_order]
        return route_distance, total_delivery_distance

    def _vehicle_stats(self, individual):
        loads = [0.0] * self.num_vehicles
        distances = [0.0] * self.num_vehicles
        total_delivery_distance = [0.0] * self.num_vehicles

        assignments = [[] for _ in range(self.num_vehicles)]
        for order_idx, vehicle_idx in enumerate(individual):
            loads[vehicle_idx] += self.order_demands[order_idx]
            assignments[vehicle_idx].append(order_idx)

        for v_idx in range(self.num_vehicles):
            distances[v_idx], total_delivery_distance[v_idx] = self._estimate_route_stats(v_idx, assignments[v_idx])

        return loads, distances, total_delivery_distance

    def fitness(self, individual):
        loads, distances, total_delivery_distance = self._vehicle_stats(individual)
        total_distance_km = sum(distances) / 1000.0
        total_delivery_hours = sum(total_delivery_distance) / 1000.0 / 40.0

        mean_distance = total_distance_km / self.num_vehicles
        variance = sum((d/1000.0 - mean_distance) ** 2 for d in distances) / self.num_vehicles
        std_distance = math.sqrt(variance)

        penalty = 0.0
        for v_idx in range(self.num_vehicles):
            overload = max(0.0, loads[v_idx] - self.vehicle_capacities[v_idx])
            penalty += overload * self.penalty_factor

        balance_penalty = std_distance * 15.0
        cost = total_distance_km + total_delivery_hours + balance_penalty + penalty + 1.0
        return 1.0 / cost

    def _repair(self, individual):
        loads = [0.0] * self.num_vehicles
        for order_idx, vehicle_idx in enumerate(individual):
            loads[vehicle_idx] += self.order_demands[order_idx]

        for order_idx in range(self.num_orders):
            current_v = individual[order_idx]
            if loads[current_v] > self.vehicle_capacities[current_v]:
                feasible_vehicles = [
                    v for v in range(self.num_vehicles)
                    if v != current_v and loads[v] + self.order_demands[order_idx] <= self.vehicle_capacities[v]
                ]
                if feasible_vehicles:
                    best_v = min(
                        feasible_vehicles,
                        key=lambda v: self.bird_dist_matrix[v][order_idx] + 0.2 * abs(loads[v] + self.order_demands[order_idx] - self.vehicle_capacities[v])
                    )
                    loads[current_v] -= self.order_demands[order_idx]
                    loads[best_v] += self.order_demands[order_idx]
                    individual[order_idx] = best_v
        return individual

    def crossover(self, parent1, parent2):
        child = [None] * self.num_orders
        for idx in range(self.num_orders):
            child[idx] = parent1[idx] if random.random() < 0.5 else parent2[idx]
        return self._repair(child)

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            order_idx = random.randrange(self.num_orders)
            feasible_vehicles = [
                v for v in range(self.num_vehicles)
                if sum(self.order_demands[i] for i, assignment in enumerate(individual) if assignment == v and i != order_idx) + self.order_demands[order_idx] <= self.vehicle_capacities[v]
            ]
            if feasible_vehicles:
                individual[order_idx] = min(
                    feasible_vehicles,
                    key=lambda v: self.bird_dist_matrix[v][order_idx] + 0.15 * abs((sum(self.order_demands[i] for i, assignment in enumerate(individual) if assignment == v and i != order_idx) + self.order_demands[order_idx]) - self.vehicle_capacities[v])
                )
            else:
                individual[order_idx] = random.randrange(self.num_vehicles)
        return self._repair(individual)

    def run(self):
        population = [self._create_feasible_individual() for _ in range(self.pop_size)]

        for _ in range(self.generations):
            population.sort(key=self.fitness, reverse=True)
            new_gen = population[:6]

            while len(new_gen) < self.pop_size:
                parents = random.sample(population[:24], 2)
                child = self.crossover(parents[0], parents[1])
                child = self.mutate(child)
                new_gen.append(child)

            population = new_gen

        population.sort(key=self.fitness, reverse=True)
        return population[0]
