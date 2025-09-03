"""Recepción y validación de datos de pasajeros"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Tuple

class DataReceptionSystem:
    """Validación y procesamiento"""
    
    def __init__(self):
        self.required_columns = ['name', 'id', 'lat', 'lng', 'company_address']
        self.processing_start_time = None
    
    def clean_coordinates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y convierte coordenadas con formato incorrecto"""
        df_clean = df.copy()
        
        def convert_coordinate(coord):
            if isinstance(coord, str):
                # Remover puntos y convertir a float dividiendo por 1000
                clean_str = coord.replace('.', '')
                if clean_str and clean_str.replace('-', '').isdigit():
                    # Si tiene más de 2 dígitos antes del decimal, dividir
                    if len(clean_str.replace('-', '')) > 2:
                        # Preservar el signo negativo
                        sign = -1 if clean_str.startswith('-') else 1
                        clean_str = clean_str.replace('-', '')
                        # Convertir a float y dividir por 1000 para obtener decimales correctos
                        return sign * float(clean_str) / 1000
                    return float(clean_str)
            elif isinstance(coord, (int, float)):
                # Si ya es numérico pero tiene formato incorrecto
                if abs(coord) > 180:
                    return coord / 1000
            return coord
        
        # Limpieza a latitud y longitud
        if 'lat' in df_clean.columns:
            df_clean['lat'] = df_clean['lat'].apply(convert_coordinate)
        
        if 'lng' in df_clean.columns:
            df_clean['lng'] = df_clean['lng'].apply(convert_coordinate)
        
        return df_clean
    
    def validate_csv_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Valida la estructura y contenido del CSV"""
        errors = []
        
        # Verificar columnas requeridas
        missing_cols = [col for col in self.required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Columnas faltantes: {missing_cols}")
        
        # Verificar datos nulos en columnas críticas
        for col in ['lat', 'lng', 'id']:
            if col in df.columns and df[col].isnull().any():
                errors.append(f"Valores nulos encontrados en columna: {col}")
        
        # Verificar rango de coordenadas (Colombia)
        if 'lat' in df.columns and 'lng' in df.columns:
            # Convertir a numérico antes de comparar
            try:
                lat_numeric = pd.to_numeric(df['lat'], errors='coerce')
                lng_numeric = pd.to_numeric(df['lng'], errors='coerce')
                
                if not lat_numeric.between(-5, 15).all():
                    errors.append("Latitudes fuera del rango válido para Colombia")
                if not lng_numeric.between(-85, -65).all():
                    errors.append("Longitudes fuera del rango válido para Colombia")
            except Exception as e:
                errors.append(f"Error convirtiendo coordenadas: {str(e)}")
        
        return len(errors) == 0, errors
    
    def process_passenger_data(self, file_path: str) -> pd.DataFrame:
        """Procesa el archivo CSV de pasajeros"""
        self.processing_start_time = datetime.now()
        print(f"Iniciando procesamiento de datos: {self.processing_start_time}")
        
        try:
            # Leer CSV
            df = pd.read_csv(file_path)
            print(f"Archivo leído exitosamente: {len(df)} pasajeros")
            
            # Limpiar coordenadas
            print("Limpiando formato de coordenadas...")
            df = self.clean_coordinates(df)
            
            # Validar datos
            is_valid, errors = self.validate_csv_data(df)
            if not is_valid:
                raise ValueError(f"Errores en los datos: {errors}")
            
            # Limpiar y preparar datos
            df['id'] = df['id'].astype(str)
            df['lat'] = pd.to_numeric(df['lat'], errors='coerce')
            df['lng'] = pd.to_numeric(df['lng'], errors='coerce')
            df = df.dropna(subset=['lat', 'lng'])
            
            print(f"Datos validados y limpiados: {len(df)} pasajeros válidos")
            return df
            
        except Exception as e:
            print(f"Error procesando datos: {str(e)}")
            raise
    
    def calculate_processing_time(self) -> float:
        """Calcula el tiempo de procesamiento en minutos"""
        if self.processing_start_time:
            return (datetime.now() - self.processing_start_time).total_seconds() / 60
        return 0