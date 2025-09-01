"""
Módulo para visualización de rutas con Folium
"""

import folium
from typing import Dict
import os

class RouteVisualizer:
    """Clase para visualizar rutas en mapas usando Folium"""
    
    def __init__(self, center_lat=4.6724261, center_lng=-74.1288623):
        self.center_lat = center_lat
        self.center_lng = center_lng
        # Colores oscuros y bien visibles
        self.colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A826', '#6A0572',
            '#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#2B4162'
        ]
    
    def ensure_img_directory(self):
        """Asegura que el directorio img existe"""
        os.makedirs('img', exist_ok=True)
    
    def create_route_map(self, routes_data: Dict, save_path: str = None) -> folium.Map:
        """Crea mapa con todas las rutas"""
        
        # Asegurar que la carpeta img existe
        self.ensure_img_directory()
        
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
                    weight=4,  # Grosor aumentado para mejor visibilidad
                    color=color,
                    opacity=0.9,
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
        """Crea leyenda HTML para el mapa con logo"""
        legend_items = []
        for idx, route in enumerate(routes_data['routes']):
            color = self.colors[idx % len(self.colors)]
            legend_items.append(f"""
                <li style="margin-bottom: 5px;">
                    <span style="color:{color}; font-size: 18px;">●</span> 
                    {route['bus_id']} - {route['passengers_count']} pasajeros (Cap: {route['capacity']})
                </li>
            """)
        
        return f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 320px; height: auto; 
                    background-color: white; border:2px solid #2c3e50; z-index:9999; 
                    font-size:12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        
        <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
            <img src="img/logo.svg" alt="Night Shift Logo" style="width: 40px; height: 40px; margin-right: 10px;">
            <div>
                <h4 style="margin: 0; color: #2c3e50; font-size: 16px; font-weight: bold;">🌙 Night Shift</h4>
                <p style="margin: 0; color: #7f8c8d; font-size: 12px;">Turno Nocturno</p>
            </div>
        </div>
        
        <div style="max-height: 300px; overflow-y: auto; margin-bottom: 10px;">
            <ul style="list-style-type: none; padding: 0; margin: 0;">
                {''.join(legend_items)}
            </ul>
        </div>
        
        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 10px 0;">
        
        <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
            <p style="margin: 2px 0; font-weight: bold;">
                <span style="color: #2c3e50;">Total:</span> 
                <span style="color: #e74c3c;">{routes_data['summary']['total_buses']} buses</span>
            </p>
            <p style="margin: 2px 0; font-weight: bold;">
                <span style="color: #2c3e50;">Ocupación:</span> 
                <span style="color: #27ae60;">{routes_data['summary']['utilization_rate']:.1%}</span>
            </p>
            <p style="margin: 2px 0; font-size: 11px; color: #7f8c8d;">
                🚌 {routes_data['summary']['total_passengers']} pasajeros
            </p>
        </div>
        
        </div>
        """