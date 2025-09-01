"""
Módulo para generación de outputs JSON para aplicaciones móviles
"""

from datetime import datetime, timedelta
from typing import Dict

class AppDataGenerator:
    """
    Genera los outputs JSON para las aplicaciones de pasajeros y conductores
    """
    
    def __init__(self):
        self.route_calculator = RealRouteCalculator()
    
    def generate_passenger_app_data(self, routes_data: Dict, passenger_id: str) -> Dict:
        """Genera datos para la app del pasajero con tiempos reales"""
        
        # Buscar el pasajero en las rutas
        for route in routes_data['routes']:
            for idx, passenger in enumerate(route['passengers']):
                if str(passenger['id']) == str(passenger_id):
                    # Calcular tiempo estimado real
                    office_coords = (4.6724261, -74.1288623)
                    passenger_coords = (passenger['lat'], passenger['lng'])
                    
                    # Obtener duración real
                    duration_min, distance_km = self.route_calculator.get_route_duration_distance(
                        office_coords, passenger_coords
                    )
                    
                    # Calcular tiempos estimados
                    departure_time = datetime.strptime("22:30", "%H:%M")
                    estimated_arrival = departure_time + timedelta(minutes=duration_min)
                    
                    # Usar real_route_geometry si existe, sino route_coordinates
                    route_geometry = route.get('real_route_geometry', route.get('route_coordinates', []))
                    
                    return {
                        'passenger_info': {
                            'id': passenger['id'],
                            'name': passenger['name'],
                            'pickup_location': f"Oficina: {passenger['company_address']}",
                            'destination': f"Lat: {passenger['lat']}, Lng: {passenger['lng']}",
                            'distance_km': round(distance_km, 1),
                            'estimated_duration_min': round(duration_min, 1)
                        },
                        'trip_details': {
                            'bus_id': route['bus_id'],
                            'bus_plate': route['bus_plate'],
                            'estimated_pickup_time': "22:30",
                            'estimated_arrival_time': estimated_arrival.strftime("%H:%M"),
                            'status': "confirmed",
                            'position_in_route': idx + 1
                        },
                        'real_time_tracking': {
                            'bus_location': None,
                            'estimated_arrival_in_minutes': round(duration_min, 1),
                            'next_stop': None,
                            'route_geometry': route_geometry
                        }
                    }
        
        return {"error": "Passenger not found"}
    
    def generate_driver_app_data(self, route_info: Dict) -> Dict:
        """Genera datos para la app del conductor con información real"""
        
        passengers_list = []
        stops = []
        total_duration = 0
        total_distance = 0
        
        office_coords = (4.6724261, -74.1288623)
        previous_coords = office_coords
        
        for idx, passenger in enumerate(route_info['passengers']):
            current_coords = (passenger['lat'], passenger['lng'])
            
            # Calcular tiempo y distancia hasta esta parada
            duration_min, distance_km = self.route_calculator.get_route_duration_distance(
                previous_coords, current_coords
            )
            
            total_duration += duration_min
            total_distance += distance_km
            
            # Calcular hora estimada
            departure_time = datetime.strptime("22:30", "%H:%M")
            estimated_time = departure_time + timedelta(minutes=total_duration)
            
            passengers_list.append({
                'order': idx + 1,
                'passenger_id': passenger['id'],
                'name': passenger['name'],
                'phone': f"+57 300 {passenger['id'][-7:]}",
                'pickup_status': 'pending',
                'drop_off_status': 'pending',
                'estimated_arrival': estimated_time.strftime("%H:%M")
            })
            
            stops.append({
                'stop_number': idx + 1,
                'passenger_name': passenger['name'],
                'address': f"Destino - Lat: {passenger['lat']}, Lng: {passenger['lng']}",
                'coordinates': [passenger['lat'], passenger['lng']],
                'estimated_time': estimated_time.strftime("%H:%M"),
                'status': 'pending',
                'duration_from_previous': round(duration_min, 1),
                'distance_from_previous': round(distance_km, 1)
            })
            
            previous_coords = current_coords
        
        # Usar real_route_geometry si existe, sino route_coordinates
        route_geometry = route_info.get('real_route_geometry', route_info.get('route_coordinates', []))
        
        return {
            'bus_info': {
                'bus_id': route_info['bus_id'],
                'bus_plate': route_info['bus_plate'],
                'capacity': route_info['capacity'],
                'current_passengers': route_info['passengers_count']
            },
            'route_summary': {
                'total_stops': len(stops),
                'estimated_duration_minutes': round(total_duration, 1),
                'total_distance_km': round(total_distance, 1),
                'start_time': "22:30",
                'pickup_location': "Oficina Central - Ac. 24 #86-49",
                'average_speed_kmh': round((total_distance / total_duration * 60) if total_duration > 0 else 0, 1)
            },
            'passengers': passengers_list,
            'route_stops': stops,
            'navigation': {
                'current_stop': 0,
                'next_destination': stops[0] if stops else None,
                'route_polyline': route_geometry,
                'total_route_geometry': route_geometry
            }
        }