#!/usr/bin/env python3
"""
Punto de entrada principal del sistema Night Shift
Ejecutar: python src/main.py
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.data_reception import DataReceptionSystem
from src.route_optimizer import RouteOptimizer
from src.visualization import RouteVisualizer
from src.app_generator import AppDataGenerator
import time
from datetime import datetime
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def ensure_data_directory():
    """Asegura que el directorio data existe"""
    os.makedirs('data', exist_ok=True)

def execute_night_shift_system():
    """Función principal que ejecuta todo el sistema"""
    
    ensure_data_directory()
    
    # Inicializar sistema
    data_processor = DataReceptionSystem()
    route_optimizer = RouteOptimizer()
    visualizer = RouteVisualizer()
    app_generator = AppDataGenerator()
    
    CSV_FILE_PATH = 'data/passengers.csv'
    
    print("="*60)
    print("🌙 NIGHT SHIFT - SISTEMA DE TRANSPORTE NOCTURNO")
    print("="*60)
    
    # Paso 1: Recepción y validación de datos
    print("\n1️⃣ RECEPCIÓN DE DATOS")
    try:
        passengers_df = data_processor.process_passenger_data(CSV_FILE_PATH)
        processing_time = data_processor.calculate_processing_time()
    except Exception as e:
        print(f"❌ Error en recepción de datos: {str(e)}")
        return None, None, None
    
    # Paso 2: Optimización de rutas
    print("\n2️⃣ OPTIMIZACIÓN DE RUTAS")
    start_optimization = time.time()
    routes_data = route_optimizer.generate_routes(passengers_df)
    optimization_time = (time.time() - start_optimization) / 60
    
    print(f"✅ Rutas generadas en {optimization_time:.2f} minutos")
    print(f"📊 Resumen: {routes_data['summary']['total_buses']} buses para {routes_data['summary']['total_passengers']} pasajeros")
    print(f"🎯 Utilización de flota: {routes_data['summary']['utilization_rate']:.1%}")
    
    # Paso 3: Crear visualización
    print("\n3️⃣ VISUALIZACIÓN DE RUTAS")
    try:
        route_map = visualizer.create_route_map(routes_data, 'bas_routes_map.html')
    except Exception as e:
        print(f"❌ Error creando mapa: {str(e)}")
    
    # Paso 4: Generar outputs para apps
    print("\n4️⃣ GENERACIÓN DE OUTPUTS PARA APPS")
    
    try:
        first_passenger_id = passengers_df.iloc[0]['id']
        passenger_app_data = app_generator.generate_passenger_app_data(
            routes_data, first_passenger_id
        )
        
        if routes_data['routes']:
            driver_app_data = app_generator.generate_driver_app_data(
                routes_data['routes'][0]
            )
        else:
            driver_app_data = {"error": "No routes available"}
            
        # Guardar outputs
        with open('passenger_app_output.json', 'w', encoding='utf-8') as f:
            json.dump(passenger_app_data, f, indent=2, ensure_ascii=False)
        
        with open('driver_app_output.json', 'w', encoding='utf-8') as f:
            json.dump(driver_app_data, f, indent=2, ensure_ascii=False)
        
        with open('complete_routes_data.json', 'w', encoding='utf-8') as f:
            json.dump(routes_data, f, indent=2, ensure_ascii=False)
        
        # Mostrar tiempo total de procesamiento
        total_time = processing_time + optimization_time
        print(f"\n⏱️ TIEMPO TOTAL DE PROCESAMIENTO: {total_time:.2f} minutos")
        
        safety_margin = 15 - total_time
        print(f"🛡️ MARGEN DE SEGURIDAD: {safety_margin:.2f} minutos")
        
        if safety_margin > 0:
            print("✅ Tiempo suficiente para la operación")
        else:
            print("⚠️ Necesitamos optimizar el proceso o recibir datos más temprano")
        
        return routes_data, passenger_app_data, driver_app_data
        
    except Exception as e:
        print(f"❌ Error generando outputs: {str(e)}")
        return routes_data, None, None

if __name__ == "__main__":
    print("🚀 INICIANDO SISTEMA NIGHT SHIFT")
    print("="*60)
    
    routes_result, passenger_output, driver_output = execute_night_shift_system()
    
    if routes_result:
        print("\n✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("📁 Archivos generados:")
        print("• bas_routes_map.html - Mapa interactivo de rutas")
        print("• passenger_app_output.json - Datos para app de pasajeros")
        print("• driver_app_output.json - Datos para app de conductores")
        print("• complete_routes_data.json - Datos completos de rutas")