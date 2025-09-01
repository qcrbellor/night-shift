"""
Módulo para visualización de rutas con Folium
"""

import folium
from typing import Dict

class RouteVisualizer:
    """
    Clase para visualizar rutas en mapas usando Folium
    """
    
    def __init__(self, center_lat=4.6724261, center_lng=-74.1288623):  # Bogotá (oficina central)
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                      'lightred', 'beige', 'darkblue', 'darkgreen', 'cadetblue', 
                      'darkpurple', 'black', 'pink', 'lightblue', 'lightgreen', 'gray']
    
    def create_route_map(self, routes_data: Dict, save_path: str = None) -> folium.Map:
        """Crea mapa con todas las rutas"""
        
        # Crear mapa centrado en Bogotá
        m = folium.Map(
            location=[self.center_lat, self.center_lng],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Agregar punto de origen (oficina)
        folium.Marker(
            [self.center_lat, self.center_lng],
            popup=f"🏢 Oficina Central<br>Ac. 24 #86-49, Bogotá",
            tooltip="Punto de Partida",
            icon=folium.Icon(color='black', icon='building')
        ).add_to(m)
        
        # Agregar rutas
        for idx, route in enumerate(routes_data['routes']):
            color = self.colors[idx % len(self.colors)]
            
            # Agregar marcadores para cada pasajero
            for passenger_idx, passenger in enumerate(route['passengers']):
                folium.Marker(
                    [passenger['lat'], passenger['lng']],
                    popup=f"🚌 {route['bus_id']}<br>"
                          f"👤 {passenger['name']}<br>"
                          f"📍 Parada #{passenger_idx + 1}",
                    tooltip=f"{passenger['name']} - {route['bus_id']}",
                    icon=folium.Icon(color=color, icon='user')
                ).add_to(m)
            
            # Agregar línea de ruta - usar real_route_geometry si existe, sino route_coordinates
            route_coords = route.get('real_route_geometry', route.get('route_coordinates', []))
            if len(route_coords) > 1:
                folium.PolyLine(
                    locations=route_coords,
                    weight=3,
                    color=color,
                    opacity=0.8,
                    popup=f"Ruta {route['bus_id']} - {route['passengers_count']} pasajeros"
                ).add_to(m)
        
        # Agregar leyenda
        legend_html = self._create_legend(routes_data)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        if save_path:
            m.save(save_path)
            print(f"🗺️ Mapa guardado en: {save_path}")
        
        return m
    
    def _create_legend(self, routes_data: Dict) -> str:
        """Crea leyenda HTML para el mapa"""
        legend_items = []
        for idx, route in enumerate(routes_data['routes']):
            color = self.colors[idx % len(self.colors)]
            legend_items.append(f"""
                <li><span style="color:{color};">●</span> 
                {route['bus_id']} - {route['passengers_count']} pasajeros (Cap: {route['capacity']})</li>
            """)
        
        return f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 300px; height: auto; 
                    background-color: white; border:2px solid grey; z-index:9999; 
                    font-size:14px; padding: 10px">
        <h4>🚌 Rutas Bas - Turno Nocturno</h4>
        <ul style="list-style-type: none; padding: 0;">
            {''.join(legend_items)}
        </ul>
        <hr>
        <p><strong>Total:</strong> {routes_data['summary']['total_buses']} buses<br>
        <strong>Ocupación:</strong> {routes_data['summary']['utilization_rate']:.1%}</p>
        </div>
        """