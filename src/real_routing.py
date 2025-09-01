"""
Módulo para cálculo de rutas reales usando OSRM
"""

import requests
from typing import List, Tuple
from geopy.distance import geodesic

class RealRouteCalculator:
    """
    Calcula rutas reales usando OSRM (Open Source Routing Machine)
    """
    
    def __init__(self, base_url="http://router.project-osrm.org/route/v1/driving/"):
        self.base_url = base_url
    
    def get_route_coordinates(self, coordinates: List[Tuple[float, float]]) -> List[Tuple[float, float]]:
        """Obtiene coordenadas de ruta real entre puntos"""
        if len(coordinates) < 2:
            return coordinates
        
        try:
            # Formatear coordenadas para OSRM
            coords_str = ";".join([f"{lng},{lat}" for lat, lng in coordinates])
            url = f"{self.base_url}{coords_str}?overview=full&geometries=geojson"
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                # Extraer geometría de la ruta
                route_geometry = data['routes'][0]['geometry']['coordinates']
                # Convertir de [lng, lat] a [lat, lng]
                return [[coord[1], coord[0]] for coord in route_geometry]
            
        except Exception as e:
            print(f"❌ Error obteniendo ruta real: {str(e)}")
        
        # Fallback: línea recta si OSRM falla
        return coordinates
    
    def get_route_duration_distance(self, origin: Tuple[float, float], destination: Tuple[float, float]) -> Tuple[float, float]:
        """Obtiene duración y distancia de ruta entre two puntos"""
        try:
            coords_str = f"{origin[1]},{origin[0]};{destination[1]},{destination[0]}"
            url = f"{self.base_url}{coords_str}?overview=false"
            
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            data = response.json()
            
            if data['code'] == 'Ok' and data['routes']:
                route = data['routes'][0]
                return route['duration'] / 60, route['distance'] / 1000  # minutos, km
            
        except Exception as e:
            print(f"❌ Error obteniendo duración de ruta: {str(e)}")
        
        # Fallback: calcular distancia geodésica
        distance_km = geodesic(origin, destination).kilometers
        duration_min = (distance_km / 25) * 60  # Asumiendo 25 km/h promedio
        return duration_min, distance_km