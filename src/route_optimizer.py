"""Módulo de optimización de rutas usando clustering y TSP"""

import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN, KMeans
from geopy.distance import geodesic
from typing import List, Dict
from datetime import datetime

def get_route_calculator():
    """Helper function para obtener el route calculator"""
    from src.real_routing import RealRouteCalculator
    return RealRouteCalculator()

class RouteOptimizer:
    """Optimización de rutas usando clustering y TSP"""
    
    def __init__(self, bus_capacities=[8, 15, 19, 20, 40]):
        self.bus_capacities = sorted(bus_capacities, reverse=True)
        self.routes = []
        self.buses_needed = []
    
    def calculate_distance_matrix(self, passengers: pd.DataFrame) -> np.ndarray:
        """Calcula matriz de distancias entre todos los puntos"""
        coords = passengers[['lat', 'lng']].values
        n = len(coords)
        distance_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                dist = geodesic(coords[i], coords[j]).kilometers
                distance_matrix[i][j] = dist
                distance_matrix[j][i] = dist
        
        return distance_matrix
    
    def calculate_real_distance_matrix(self, passengers: pd.DataFrame) -> np.ndarray:
        """Calcula matriz de tiempos de viaje reales entre puntos"""
        route_calculator = get_route_calculator()
        
        coords = passengers[['lat', 'lng']].values
        n = len(coords)
        time_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                origin = (coords[i][0], coords[i][1])
                destination = (coords[j][0], coords[j][1])
                duration_min, _ = route_calculator.get_route_duration_distance(origin, destination)
                time_matrix[i][j] = duration_min
                time_matrix[j][i] = duration_min
        
        return time_matrix
    
    def get_real_route_coordinates(self, passengers: pd.DataFrame) -> List[List[float]]:
        """Obtiene coordenadas de ruta real incluyendo la oficina"""
        route_calculator = get_route_calculator()
        
        office_coords = (4.6724261, -74.1288623)
        
        # Crear lista de coordenadas: oficina + pasajeros en orden
        all_coords = [office_coords]
        for _, passenger in passengers.iterrows():
            all_coords.append((passenger['lat'], passenger['lng']))
        
        # Obtener ruta real
        return route_calculator.get_route_coordinates(all_coords)
    
    def cluster_passengers(self, passengers: pd.DataFrame, method='kmeans') -> pd.DataFrame:
        """Agrupa pasajeros por proximidad geográfica"""
        
        # Estimar número de clusters basado en capacidad de buses
        total_passengers = len(passengers)
        estimated_clusters = max(1, total_passengers // 20)
        
        coords = passengers[['lat', 'lng']].values
        
        if method == 'kmeans':
            clustering = KMeans(n_clusters=min(estimated_clusters, total_passengers), 
                              random_state=42, n_init=10)
        else:
            clustering = DBSCAN(eps=0.01, min_samples=2)
        
        passengers['cluster'] = clustering.fit_predict(coords)
        
        # Si DBSCAN genera clusters con -1 (ruido), asignarlos a clusters individuales
        if method == 'dbscan':
            noise_mask = passengers['cluster'] == -1
            if noise_mask.any():
                max_cluster = passengers['cluster'].max()
                passengers.loc[noise_mask, 'cluster'] = range(max_cluster + 1, 
                                                            max_cluster + 1 + noise_mask.sum())
        
        return passengers
    
    def optimize_vehicle_assignment(self, passengers_by_cluster: Dict) -> List[Dict]:
        """Optimiza la asignación de vehículos por cluster"""
        assignments = []
        
        for cluster_id, cluster_passengers in passengers_by_cluster.items():
            cluster_size = len(cluster_passengers)
            
            # Algoritmo greedy para asignar vehículos
            buses_for_cluster = []
            remaining_passengers = cluster_size
            
            for capacity in self.bus_capacities:
                while remaining_passengers >= capacity:
                    buses_for_cluster.append({
                        'capacity': capacity,
                        'passengers_count': capacity,
                        'passengers': cluster_passengers.iloc[:capacity].to_dict('records')
                    })
                    cluster_passengers = cluster_passengers.iloc[capacity:]
                    remaining_passengers -= capacity
            
            # Asignar pasajeros restantes al bus más pequeño disponible
            if remaining_passengers > 0:
                suitable_capacity = min([cap for cap in self.bus_capacities if cap >= remaining_passengers])
                buses_for_cluster.append({
                    'capacity': suitable_capacity,
                    'passengers_count': remaining_passengers,
                    'passengers': cluster_passengers.to_dict('records')
                })
            
            assignments.extend(buses_for_cluster)
        
        return assignments
    
    def solve_tsp_greedy(self, distance_matrix: np.ndarray, start_idx: int = 0) -> List[int]:
        """Resuelve TSP usando algoritmo greedy (nearest neighbor)"""
        n = len(distance_matrix)
        unvisited = set(range(n))
        current = start_idx
        route = [current]
        unvisited.remove(current)
        
        while unvisited:
            nearest = min(unvisited, key=lambda x: distance_matrix[current][x])
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        return route
    
    def generate_routes(self, passengers: pd.DataFrame) -> Dict:
        """Genera rutas optimizadas para todos los pasajeros"""
        
        try:
            # 1. Clustering de pasajeros
            passengers_clustered = self.cluster_passengers(passengers)
            
            # 2. Agrupar por cluster
            clusters = {}
            for cluster_id in passengers_clustered['cluster'].unique():
                clusters[cluster_id] = passengers_clustered[
                    passengers_clustered['cluster'] == cluster_id
                ].reset_index(drop=True)
            
            # 3. Asignar vehículos
            vehicle_assignments = self.optimize_vehicle_assignment(clusters)
            
            # 4. Generar rutas TSP para cada bus
            routes_data = []
            bus_counter = 1
            
            for assignment in vehicle_assignments:
                if len(assignment['passengers']) > 1:
                    # Crear dataframe temporal para este bus
                    bus_passengers = pd.DataFrame(assignment['passengers'])
                    
                    # Calcular matriz de distancias con tiempos reales
                    distance_matrix = self.calculate_real_distance_matrix(bus_passengers)
                    
                    # Resolver TSP
                    optimal_route = self.solve_tsp_greedy(distance_matrix)
                    
                    # Reordenar pasajeros según ruta óptima
                    ordered_passengers = bus_passengers.iloc[optimal_route]
                    
                    # Obtener ruta real con OSRM
                    route_coords = self.get_real_route_coordinates(ordered_passengers)
                    
                else:
                    ordered_passengers = pd.DataFrame(assignment['passengers'])
                    # Para un solo pasajero, ruta directa desde oficina
                    office_coords = (4.6724261, -74.1288623)
                    passenger_coords = (ordered_passengers.iloc[0]['lat'], ordered_passengers.iloc[0]['lng'])
                    route_coords = get_route_calculator().get_route_coordinates([office_coords, passenger_coords])
                
                route_info = {
                    'bus_id': f"BUS-{bus_counter:03d}",
                    'bus_plate': f"ABC-{bus_counter:03d}",
                    'capacity': assignment['capacity'],
                    'passengers_count': assignment['passengers_count'],
                    'passengers': ordered_passengers.to_dict('records'),
                    'route_coordinates': route_coords,
                    'real_route_geometry': route_coords
                }
                
                routes_data.append(route_info)
                bus_counter += 1
            
            # Calcular estadísticas
            total_buses = len(routes_data)
            total_capacity = sum([route['capacity'] for route in routes_data])
            utilization = len(passengers) / total_capacity if total_capacity > 0 else 0
            
            return {
                'routes': routes_data,
                'summary': {
                    'total_passengers': len(passengers),
                    'total_buses': total_buses,
                    'total_capacity': total_capacity,
                    'utilization_rate': utilization,
                    'processing_time': datetime.now().isoformat()
                }
            }
        
        except Exception as e:
            print(f"Error en generate_routes: {str(e)}")
            return {
                'routes': [],
                'summary': {
                    'total_passengers': 0,
                    'total_buses': 0,
                    'total_capacity': 0,
                    'utilization_rate': 0,
                    'processing_time': datetime.now().isoformat()
                }
            }