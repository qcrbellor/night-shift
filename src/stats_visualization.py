"""
Módulo para generación de gráficas estadísticas
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from typing import Dict
import os

class StatsVisualizer:
    """Clase para generar visualizaciones estadísticas del sistema"""
    
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A826', '#6A0572']
    
    def ensure_img_directory(self):
        """Asegura que el directorio img existe"""
        os.makedirs('img', exist_ok=True)
    
    def create_utilization_analysis(self, routes_data: Dict, save_path: str = 'img/bus_utilization_analysis.png'):
        """Crea gráfico de análisis de utilización"""
        self.ensure_img_directory()
        
        try:
            plt.figure(figsize=(15, 10))
            
            routes = routes_data['routes']
            
            # Subplot 1: Utilización por bus
            plt.subplot(2, 2, 1)
            bus_capacities = [route['capacity'] for route in routes]
            bus_usage = [route['passengers_count'] for route in routes]
            bus_ids = [route['bus_id'] for route in routes]
            
            x = range(len(bus_capacities))
            plt.bar(x, bus_capacities, alpha=0.6, label='Capacidad', color='lightblue')
            plt.bar(x, bus_usage, alpha=0.9, label='Pasajeros', color='darkblue')
            plt.xlabel('Bus')
            plt.ylabel('Número de Pasajeros')
            plt.title('Utilización por Bus')
            plt.legend()
            plt.xticks(x, [f"Bus {i+1}" for i in range(len(bus_capacities))], rotation=45)
            
            # Subplot 2: Distribución de tipos de bus
            plt.subplot(2, 2, 2)
            capacity_counts = pd.Series(bus_capacities).value_counts().sort_index()
            plt.pie(capacity_counts.values, labels=[f'{cap}p' for cap in capacity_counts.index], 
                    autopct='%1.1f%%', startangle=90, colors=self.colors)
            plt.title('Distribución de Tipos de Bus')
            
            # Subplot 3: Eficiencia por ruta
            plt.subplot(2, 2, 3)
            efficiency = [usage/capacity*100 for usage, capacity in zip(bus_usage, bus_capacities)]
            plt.bar(x, efficiency, color='green', alpha=0.7)
            plt.axhline(y=85, color='red', linestyle='--', label='Meta 85%')
            plt.xlabel('Bus')
            plt.ylabel('Eficiencia (%)')
            plt.title('Eficiencia por Bus')
            plt.legend()
            plt.xticks(x, [f"Bus {i+1}" for i in range(len(bus_capacities))], rotation=45)
            
            # Subplot 4: Resumen estadístico
            plt.subplot(2, 2, 4)
            plt.axis('off')
            summary_text = f"""
            RESUMEN ESTADÍSTICO
            
            📊 Total Pasajeros: {routes_data['summary']['total_passengers']}
            🚌 Total Buses: {routes_data['summary']['total_buses']}
            🎯 Utilización: {routes_data['summary']['utilization_rate']:.1%}
            📈 Eficiencia Promedio: {np.mean(efficiency):.1f}%
            🪑 Asientos Vacíos: {sum(bus_capacities) - sum(bus_usage)}
            
            🏆 Bus Más Eficiente: {max(efficiency):.1f}%
            📉 Bus Menos Eficiente: {min(efficiency):.1f}%
            """
            
            plt.text(0.1, 0.5, summary_text, fontsize=12, verticalalignment='center',
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            
            plt.suptitle('📊 Análisis de Utilización - Night Shift System', fontsize=16, fontweight='bold')
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📈 Gráfico de análisis guardado: {save_path}")
            
        except Exception as e:
            print(f"❌ Error creando gráfico de análisis: {str(e)}")
    
    def create_geographic_distribution(self, routes_data: Dict, save_path: str = 'img/geographic_distribution.png'):
        """Crea gráfico de distribución geográfica"""
        self.ensure_img_directory()
        
        try:
            plt.figure(figsize=(12, 8))
            
            # Extraer todas las coordenadas de pasajeros
            all_passengers = []
            for route in routes_data['routes']:
                all_passengers.extend(route['passengers'])
            
            lats = [p['lat'] for p in all_passengers]
            lngs = [p['lng'] for p in all_passengers]
            
            # Crear scatter plot
            plt.scatter(lngs, lats, alpha=0.6, s=50, c='blue', edgecolors='black', linewidth=0.5)
            
            # Marcar la oficina central
            plt.scatter(-74.1288623, 4.6724261, s=200, c='red', marker='*', edgecolors='black', 
                       linewidth=1, label='Oficina Central')
            
            plt.xlabel('Longitud')
            plt.ylabel('Latitud')
            plt.title('Distribución Geográfica de Pasajeros')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Añadir anotaciones
            plt.annotate('Oficina Central', xy=(-74.1288623, 4.6724261), xytext=(-74.14, 4.66),
                        arrowprops=dict(arrowstyle='->', color='red'),
                        bbox=dict(boxstyle="round,pad=0.3", facecolor="yellow"))
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"🗺️ Gráfico de distribución geográfica guardado: {save_path}")
            
        except Exception as e:
            print(f"❌ Error creando gráfico de distribución: {str(e)}")
    
    def create_performance_timeline(self, processing_time: float, optimization_time: float, 
                                  save_path: str = 'img/performance_timeline.png'):
        """Crea timeline de performance del sistema"""
        self.ensure_img_directory()
        
        try:
            plt.figure(figsize=(10, 6))
            
            process_steps = ['Recepción\nDatos', 'Validación', 'Clustering', 
                           'Optimización\nRutas', 'Generación\nOutputs']
            process_times = [
                processing_time * 0.3,  # 30% del tiempo total de procesamiento
                processing_time * 0.2,  # 20%
                optimization_time * 0.4,  # 40% del tiempo de optimización
                optimization_time * 0.4,  # 40%
                (processing_time + optimization_time) * 0.1  # 10% total
            ]
            
            cumulative_times = np.cumsum([0] + process_times)
            
            colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A826', '#6A0572']
            
            for i in range(len(process_steps)):
                plt.barh(process_steps[i], process_times[i], left=cumulative_times[i], 
                        color=colors[i], alpha=0.8, edgecolor='black')
                
                # Añadir etiquetas de tiempo
                plt.text(cumulative_times[i] + process_times[i]/2, i, 
                        f'{process_times[i]:.1f}m', ha='center', va='center', 
                        fontweight='bold', color='white')
            
            plt.xlabel('Tiempo (minutos)')
            plt.title('Timeline de Procesamiento del Sistema')
            plt.grid(True, alpha=0.3, axis='x')
            
            # Añadir tiempo total
            total_time = processing_time + optimization_time
            plt.axvline(x=total_time, color='red', linestyle='--', alpha=0.7)
            plt.text(total_time + 0.1, len(process_steps)-1, 
                    f'Total: {total_time:.1f}m', color='red', va='center')
            
            plt.tight_layout()
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"⏱️ Timeline de performance guardado: {save_path}")
            
        except Exception as e:
            print(f"❌ Error creando timeline de performance: {str(e)}")
    
    def create_all_charts(self, routes_data: Dict, processing_time: float, optimization_time: float):
        """Crea todas las gráficas estadísticas"""
        print("\n📊 GENERANDO GRÁFICAS ESTADÍSTICAS")
        
        self.create_utilization_analysis(routes_data)
        self.create_geographic_distribution(routes_data)
        self.create_performance_timeline(processing_time, optimization_time)
        
        print("✅ Todas las gráficas generadas en la carpeta img/")