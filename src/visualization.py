"""Módulo para visualización de rutas con Folium"""

import folium
from typing import Dict
import os
from datetime import datetime

class RouteVisualizer:
    """Visualizar las rutas usando Folium"""
    
    def __init__(self, center_lat=4.6724261, center_lng=-74.1288623):
        self.center_lat = center_lat
        self.center_lng = center_lng
        self.colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 
                      'darkorange', 'darkgray', 'darkblue', 'darkgreen', 'cadetblue', 
                      'darkpurple', 'black', 'pink', 'lightblue', 'lightgreen', 'gray'
        ]
    
    def ensure_img_directory(self):
        os.makedirs('img', exist_ok=True)
    
    def create_route_map(self, routes_data: Dict, save_path: str = None) -> folium.Map:
        
        # img existe
        self.ensure_img_directory()
        
        # Mapa centrado en Bogotá
        m = folium.Map(
            location=[self.center_lat, self.center_lng],
            zoom_start=12,
            tiles='OpenStreetMap'
        )
        
        # Punto de origen
        folium.Marker(
            [self.center_lat, self.center_lng],
            popup=f"Oficina<br>Ac. 24 #86-49, Bogotá",
            tooltip="Punto de Partida",
            icon=folium.Icon(color='black', icon='building')
        ).add_to(m)
        
        # Rutas
        for idx, route in enumerate(routes_data['routes']):
            color = self.colors[idx % len(self.colors)]
            
            # Marcadores para cada pasajero
            for passenger_idx, passenger in enumerate(route['passengers']):
                folium.Marker(
                    [passenger['lat'], passenger['lng']],
                    popup=f"🚌 {route['bus_id']}<br>"
                        f"👤 {passenger['name']}<br>"
                        f"📍 Parada #{passenger_idx + 1}",
                    tooltip=f"{passenger['name']} - {route['bus_id']}",
                    icon=folium.Icon(
                        color=color,
                        icon_color='white',
                        icon='user',
                        prefix='fa')
                ).add_to(m)
            
            route_coords = []
            
            # Recorrido si existe, sino route_coordinates
            route_coords = route.get('real_route_geometry', route.get('route_coordinates', []))
            if len(route_coords) > 1:
                folium.PolyLine(
                    locations=route_coords,
                    weight=3,
                    color=color,
                    opacity=0.9,
                    popup=f"Ruta {route['bus_id']} - {route['passengers_count']} pasajeros"
                ).add_to(m)
            
        # Agregar leyenda
        legend_html = self._create_legend(routes_data)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        if save_path:
            m.save(save_path)
            print(f"Mapa guardado en: {save_path}")
        
        return m
    
    def _create_legend(self, routes_data: Dict) -> str:
        """Leyenda o convenciones"""
        legend_items = []
        for idx, route in enumerate(routes_data['routes']):
            color = self.colors[idx % len(self.colors)]
            efficiency = (route['passengers_count'] / route['capacity']) * 100
            legend_items.append(f"""
                <tr>
                    <td><span style="color:{color}; font-size: 16px;">●</span></td>
                    <td>{route['bus_id']}</td>
                    <td>{route['passengers_count']}/{route['capacity']}</td>
                    <td>{efficiency:.1f}%</td>
                </tr>
            """)
        
        # Métricas dashboard
        total_buses = routes_data['summary']['total_buses']
        total_passengers = routes_data['summary']['total_passengers']
        utilization = routes_data['summary']['utilization_rate'] * 100
        total_capacity = sum(route['capacity'] for route in routes_data['routes'])
        empty_seats = total_capacity - total_passengers
        
        return f"""
        <div style="position: fixed; 
                    top: 10px; right: 10px; width: 380px; height: auto; 
                    background-color: white; border:2px solid #2c3e50; z-index:9999; 
                    font-size:12px; padding: 15px; border-radius: 10px;
                    box-shadow: 0 4px 8px rgba(0,0,0,0.2);">
        
        <!-- Header -->
        <div style="display: flex; align-items: center; margin-bottom: 15px; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px;">
            <img src="img/logo.svg" alt="Bas Logo" style="width: 40px; height: 40px; margin-right: 10px;">
            <div>
                <h4 style="margin: 0; color: #2c3e50; font-size: 16px; font-weight: bold;">Turno nocturno: Dashboard</h4>
                <p style="margin: 0; color: #7f8c8d; font-size: 12px;">Monitoreo en Tiempo Real</p>
            </div>
        </div>

        <!-- Dashboard -->
        <div style="margin-bottom: 15px;">
            <button onclick="showTab('tab-routes')" style="padding: 5px 10px; margin-right: 5px; border: 1px solid #ddd; border-radius: 3px; background: #f8f9fa;">🚌 Rutas</button>
            <button onclick="showTab('tab-stats')" style="padding: 5px 10px; border: 1px solid #ddd; border-radius: 3px; background: #f8f9fa;">📊 Estadísticas</button>
        </div>

        <!-- Rutas -->
        <div id="tab-routes" style="display: block; max-height: 250px; overflow-y: auto; margin-bottom: 10px;">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: #f8f9fa;">
                        <th style="text-align: left; padding: 5px; border-bottom: 1px solid #ddd;">Ruta</th>
                        <th style="text-align: left; padding: 5px; border-bottom: 1px solid #ddd;">Bus</th>
                        <th style="text-align: left; padding: 5px; border-bottom: 1px solid #ddd;">Ocupación</th>
                        <th style="text-align: left; padding: 5px; border-bottom: 1px solid #ddd;">Eficiencia</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(legend_items)}
                </tbody>
            </table>
        </div>

        <!-- Estadísticas -->
        <div id="tab-stats" style="display: none; margin-bottom: 10px;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; border-radius: 5px; margin-bottom: 10px;">
                <h4 style="margin: 0 0 10px 0;">Resumen General</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{total_buses}</div>
                        <div style="font-size: 11px;">Buses</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{total_passengers}</div>
                        <div style="font-size: 11px;">Pasajeros</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{utilization:.1f}%</div>
                        <div style="font-size: 11px;">Utilización</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 24px; font-weight: bold;">{empty_seats}</div>
                        <div style="font-size: 11px;">Asientos Vacíos</div>
                    </div>
                </div>
            </div>

            <div style="background: #f8f9fa; padding: 10px; border-radius: 5px;">
                <h5 style="margin: 0 0 10px 0;">Métricas de Performance</h5>
                <div style="font-size: 11px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Capacidad Total:</span>
                        <span style="font-weight: bold;">{total_capacity} asientos</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                        <span>Eficiencia Promedio:</span>
                        <span style="font-weight: bold;">{utilization:.1f}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span>Promedio Pasajeros/Bus:</span>
                        <span style="font-weight: bold;">{(total_passengers/total_buses):.1f}</span>
                    </div>
                </div>
            </div>
        </div>

        <hr style="border: none; border-top: 1px solid #ecf0f1; margin: 10px 0;">

        <!-- Footer -->
        <div style="font-size: 11px; color: #7f8c8d; text-align: center;">
            <div>Última actualización - {datetime.now().strftime('%H:%M')}</div>
        </div>

        <!-- JavaScript -->
        <script>
            function showTab(tabId) {{
                document.getElementById('tab-routes').style.display = 'none';
                document.getElementById('tab-stats').style.display = 'none';
                document.getElementById(tabId).style.display = 'block';
            }}
        </script>

        </div>
        """