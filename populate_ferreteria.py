#!/usr/bin/env python3
"""
Script para poblar la base de datos con productos específicos de ferretería
Ejecutar: python populate_ferreteria.py
"""

import sqlite3
import os
from datetime import datetime

# Configuración de la base de datos
DATABASE = 'ferreteria_inventario.db'

def init_db():
    """Inicializa la base de datos si no existe"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT UNIQUE,
                nombre TEXT NOT NULL UNIQUE,
                descripcion TEXT,
                marca TEXT,
                cantidad INTEGER NOT NULL DEFAULT 0,
                precio_compra REAL NOT NULL DEFAULT 0,
                precio_venta REAL NOT NULL DEFAULT 0,
                categoria TEXT NOT NULL DEFAULT 'General',
                subcategoria TEXT,
                ubicacion TEXT,
                proveedor TEXT,
                stock_minimo INTEGER DEFAULT 5,
                unidad_medida TEXT DEFAULT 'unidad',
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

def clear_products():
    """Limpia todos los productos existentes"""
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('DELETE FROM productos')
        conn.commit()
        print("🗑️  Base de datos limpiada")

def add_ferreteria_products():
    """Agrega productos específicos de ferretería"""
    productos_ferreteria = [
        # Herramientas Manuales
        ("HER-001", "Martillo de Garra 16oz", "Martillo con mango de fibra de vidrio, cabeza forjada", "Stanley", 25, 12.50, 18.99, "Herramientas Manuales", "Martillos", "Pasillo 1A", "Distribuidora Central", 5, "unidad"),
        ("HER-002", "Destornillador Phillips #2", "Destornillador con mango ergonómico y punta magnética", "Klein Tools", 40, 3.25, 6.99, "Herramientas Manuales", "Destornilladores", "Pasillo 1A", "Distribuidora Central", 10, "unidad"),
        ("HER-003", "Alicate Universal 8\"", "Alicate con mandíbulas dentadas y corte lateral", "Irwin", 18, 8.75, 15.50, "Herramientas Manuales", "Alicates", "Pasillo 1A", "Herramientas Pro", 5, "unidad"),
        ("HER-004", "Sierra de Mano 20\"", "Sierra para madera con dientes templados", "Bahco", 12, 15.00, 24.99, "Herramientas Manuales", "Sierras", "Pasillo 1B", "Herramientas Pro", 3, "unidad"),
        ("HER-005", "Llave Inglesa 10\"", "Llave ajustable con apertura hasta 30mm", "Crescent", 15, 11.25, 19.99, "Herramientas Manuales", "Llaves", "Pasillo 1A", "Distribuidora Central", 5, "unidad"),
        ("HER-006", "Nivel de Burbuja 24\"", "Nivel de aluminio con 3 burbujas", "Empire", 8, 18.50, 32.99, "Herramientas Manuales", "Niveles", "Pasillo 1B", "Construcción Total", 3, "unidad"),
        ("HER-007", "Cinta Métrica 7.5m", "Cinta métrica con carcasa resistente a impactos", "Stanley", 30, 6.50, 12.99, "Herramientas Manuales", "Medición", "Pasillo 1A", "Distribuidora Central", 8, "unidad"),
        ("HER-008", "Juego de Llaves Mixtas", "Set de 12 llaves combinadas de 8mm a 19mm", "Truper", 6, 28.00, 45.99, "Herramientas Manuales", "Llaves", "Pasillo 1A", "Herramientas Pro", 2, "unidad"),
        
        # Herramientas Eléctricas
        ("HEL-001", "Taladro Percutor 1/2\"", "Taladro con percutor 800W, velocidad variable", "Black & Decker", 8, 45.00, 79.99, "Herramientas Eléctricas", "Taladros", "Vitrina", "ElectroTools", 2, "unidad"),
        ("HEL-002", "Sierra Circular 7 1/4\"", "Sierra circular 1400W con guía láser", "Skil", 5, 65.00, 119.99, "Herramientas Eléctricas", "Sierras", "Vitrina", "ElectroTools", 2, "unidad"),
        ("HEL-003", "Amoladora Angular 4.5\"", "Amoladora 750W con protector y mango lateral", "Bosch", 10, 38.00, 68.99, "Herramientas Eléctricas", "Amoladoras", "Vitrina", "ElectroTools", 3, "unidad"),
        ("HEL-004", "Lijadora Orbital", "Lijadora con almohadilla cuadrada y aspiración", "Makita", 6, 52.00, 89.99, "Herramientas Eléctricas", "Lijadoras", "Vitrina", "ElectroTools", 2, "unidad"),
        
        # Electricidad
        ("ELE-001", "Cable THW #12", "Cable de cobre sólido para instalaciones residenciales", "Condumex", 500, 1.20, 2.15, "Electricidad", "Cables", "Bodega A", "Eléctricos del Norte", 50, "metro"),
        ("ELE-002", "Interruptor Sencillo", "Interruptor de 15A, 127V para uso residencial", "Leviton", 50, 2.50, 4.99, "Electricidad", "Apagadores", "Pasillo 2A", "Eléctricos del Norte", 15, "unidad"),
        ("ELE-003", "Contacto Doble Polarizado", "Contacto con tierra física para seguridad", "Leviton", 35, 3.75, 7.25, "Electricidad", "Contactos", "Pasillo 2A", "Eléctricos del Norte", 10, "unidad"),
        ("ELE-004", "Pastilla Termomagnética 20A", "Pastilla para centro de carga, 1 polo", "Square D", 20, 8.50, 16.99, "Electricidad", "Protecciones", "Pasillo 2B", "Eléctricos del Norte", 5, "unidad"),
        ("ELE-005", "Tubo Conduit PVC 1/2\"", "Tubo conduit flexible de 3 metros", "Plycem", 80, 2.80, 5.50, "Electricidad", "Conduit", "Bodega B", "Materiales Eléctricos", 20, "unidad"),
        ("ELE-006", "Foco LED 9W", "Foco LED equivalente a 60W, luz blanca", "Philips", 60, 4.25, 8.99, "Electricidad", "Iluminación", "Pasillo 2C", "Eléctricos del Norte", 15, "unidad"),
        
        # Plomería
        ("PLO-001", "Tubo PVC Sanitario 4\"", "Tubo de 6 metros para drenaje sanitario", "Pavco", 25, 12.50, 22.99, "Plomería", "Tubería", "Bodega C", "Hidráulicos SA", 8, "unidad"),
        ("PLO-002", "Codo PVC 90° 1/2\"", "Codo de conexión roscado", "Pavco", 100, 0.85, 1.75, "Plomería", "Conexiones", "Pasillo 3A", "Hidráulicos SA", 30, "unidad"),
        ("PLO-003", "Válvula de Paso 1/2\"", "Válvula de bronce con manija", "Foset", 18, 6.50, 12.99, "Plomería", "Válvulas", "Pasillo 3A", "Hidráulicos SA", 5, "unidad"),
        ("PLO-004", "Llave para Lavabo", "Llave monomando con cartucho cerámico", "Helvex", 12, 28.00, 52.99, "Plomería", "Llaves", "Vitrina",