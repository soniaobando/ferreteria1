from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'ferreteria_inventario_2024_seguro'

# Configuración de la base de datos
DATABASE = 'ferreteria_inventario.db'

def init_db():
    """Inicializa la base de datos con las tablas necesarias para ferretería"""
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

def get_db_connection():
    """Obtiene una conexión a la base de datos"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_all_products():
    """Obtiene todos los productos de la base de datos"""
    with get_db_connection() as conn:
        products = conn.execute('''
            SELECT * FROM productos ORDER BY categoria, nombre
        ''').fetchall()
    return products

def get_product_by_id(product_id):
    """Obtiene un producto por su ID"""
    with get_db_connection() as conn:
        product = conn.execute('''
            SELECT * FROM productos WHERE id = ?
        ''', (product_id,)).fetchone()
    return product

def product_exists_by_name(name, exclude_id=None):
    """Verifica si existe un producto con el mismo nombre"""
    with get_db_connection() as conn:
        if exclude_id:
            result = conn.execute('''
                SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?) AND id != ?
            ''', (name, exclude_id)).fetchone()
        else:
            result = conn.execute('''
                SELECT id FROM productos WHERE LOWER(nombre) = LOWER(?)
            ''', (name,)).fetchone()
    return result is not None

def search_products(term, search_type='nombre'):
    """Busca productos por nombre, código, marca o categoría"""
    with get_db_connection() as conn:
        if search_type == 'nombre':
            products = conn.execute('''
                SELECT * FROM productos 
                WHERE LOWER(nombre) LIKE LOWER(?) OR LOWER(descripcion) LIKE LOWER(?)
                   OR LOWER(codigo) LIKE LOWER(?) OR LOWER(marca) LIKE LOWER(?)
                ORDER BY nombre
            ''', (f'%{term}%', f'%{term}%', f'%{term}%', f'%{term}%')).fetchall()
        elif search_type == 'categoria':
            products = conn.execute('''
                SELECT * FROM productos 
                WHERE LOWER(categoria) LIKE LOWER(?) OR LOWER(subcategoria) LIKE LOWER(?)
                ORDER BY nombre
            ''', (f'%{term}%', f'%{term}%')).fetchall()
        elif search_type == 'codigo':
            products = conn.execute('''
                SELECT * FROM productos 
                WHERE LOWER(codigo) LIKE LOWER(?)
                ORDER BY nombre
            ''', (f'%{term}%',)).fetchall()
        else:
            products = []
    return products

def get_categories():
    """Obtiene todas las categorías únicas"""
    with get_db_connection() as conn:
        categories = conn.execute('''
            SELECT DISTINCT categoria FROM productos 
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria
        ''').fetchall()
    return [cat['categoria'] for cat in categories]

def get_brands():
    """Obtiene todas las marcas únicas"""
    with get_db_connection() as conn:
        brands = conn.execute('''
            SELECT DISTINCT marca FROM productos 
            WHERE marca IS NOT NULL AND marca != ''
            ORDER BY marca
        ''').fetchall()
    return [brand['marca'] for brand in brands]

def get_low_stock_products():
    """Obtiene productos con stock bajo"""
    with get_db_connection() as conn:
        products = conn.execute('''
            SELECT * FROM productos 
            WHERE cantidad <= stock_minimo
            ORDER BY cantidad ASC
        ''').fetchall()
    return products

def get_stats():
    """Obtiene estadísticas del inventario"""
    with get_db_connection() as conn:
        total_products = conn.execute('SELECT COUNT(*) as count FROM productos').fetchone()['count']
        total_investment = conn.execute('SELECT SUM(cantidad * precio_compra) as total FROM productos').fetchone()['total']
        total_value = conn.execute('SELECT SUM(cantidad * precio_venta) as total FROM productos').fetchone()['total']
        low_stock = conn.execute('SELECT COUNT(*) as count FROM productos WHERE cantidad <= stock_minimo').fetchone()['count']
        categories_count = conn.execute('SELECT COUNT(DISTINCT categoria) as count FROM productos').fetchone()['count']
        total_units = conn.execute('SELECT SUM(cantidad) as total FROM productos').fetchone()['total']
    
    return {
        'total_products': total_products,
        'total_investment': total_investment if total_investment else 0,
        'total_value': total_value if total_value else 0,
        'potential_profit': (total_value - total_investment) if total_value and total_investment else 0,
        'low_stock': low_stock,
        'categories': categories_count,
        'total_units': total_units if total_units else 0
    }

# Rutas de la aplicación
@app.route('/')
def index():
    """Página principal con estadísticas de la ferretería"""
    stats = get_stats()
    recent_products = get_all_products()[:6]  # Últimos 6 productos
    low_stock_products = get_low_stock_products()[:5]  # Top 5 con stock bajo
    return render_template('ferreteria_index.html', 
                         stats=stats, 
                         recent_products=recent_products,
                         low_stock_products=low_stock_products)

@app.route('/inventario')
def inventario():
    """Página del inventario completo"""
    products = get_all_products()
    categories = get_categories()
    brands = get_brands()
    return render_template('ferreteria_inventario.html', 
                         products=products, 
                         categories=categories,
                         brands=brands)

@app.route('/producto/nuevo', methods=['GET', 'POST'])
def nuevo_producto():
    """Crear un nuevo producto"""
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip()
            nombre = request.form['nombre'].strip()
            descripcion = request.form.get('descripcion', '').strip()
            marca = request.form.get('marca', '').strip()
            cantidad = int(request.form['cantidad'])
            precio_compra = float(request.form['precio_compra'])
            precio_venta = float(request.form['precio_venta'])
            categoria = request.form['categoria'].strip() or 'General'
            subcategoria = request.form.get('subcategoria', '').strip()
            ubicacion = request.form.get('ubicacion', '').strip()
            proveedor = request.form.get('proveedor', '').strip()
            stock_minimo = int(request.form.get('stock_minimo', 5))
            unidad_medida = request.form.get('unidad_medida', 'unidad').strip()
            
            # Validaciones
            if not nombre:
                flash('El nombre del producto es obligatorio', 'error')
                return render_template('ferreteria_form.html', 
                                     categories=get_categories(), 
                                     brands=get_brands())
            
            if product_exists_by_name(nombre):
                flash('Ya existe un producto con ese nombre', 'error')
                return render_template('ferreteria_form.html', 
                                     categories=get_categories(), 
                                     brands=get_brands())
            
            if cantidad < 0:
                flash('La cantidad no puede ser negativa', 'error')
                return render_template('ferreteria_form.html', 
                                     categories=get_categories(), 
                                     brands=get_brands())
            
            if precio_compra < 0 or precio_venta < 0:
                flash('Los precios no pueden ser negativos', 'error')
                return render_template('ferreteria_form.html', 
                                     categories=get_categories(), 
                                     brands=get_brands())
                                     
            if precio_venta <= precio_compra:
                flash('El precio de venta debe ser mayor al precio de compra', 'warning')
            
            # Guardar en base de datos
            with get_db_connection() as conn:
                conn.execute('''
                    INSERT INTO productos (codigo, nombre, descripcion, marca, cantidad, 
                                         precio_compra, precio_venta, categoria, subcategoria, 
                                         ubicacion, proveedor, stock_minimo, unidad_medida)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (codigo, nombre, descripcion, marca, cantidad, precio_compra, 
                     precio_venta, categoria, subcategoria, ubicacion, proveedor, 
                     stock_minimo, unidad_medida))
                conn.commit()
            
            flash('Producto creado exitosamente', 'success')
            return redirect(url_for('inventario'))
            
        except ValueError:
            flash('Por favor ingrese valores numéricos válidos', 'error')
        except Exception as e:
            flash(f'Error al crear el producto: {str(e)}', 'error')
    
    categories = get_categories()
    brands = get_brands()
    return render_template('ferreteria_form.html', categories=categories, brands=brands)

@app.route('/producto/<int:product_id>/editar', methods=['GET', 'POST'])
def editar_producto(product_id):
    """Editar un producto existente"""
    product = get_product_by_id(product_id)
    
    if not product:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inventario'))
    
    if request.method == 'POST':
        try:
            codigo = request.form.get('codigo', '').strip()
            nombre = request.form['nombre'].strip()
            descripcion = request.form.get('descripcion', '').strip()
            marca = request.form.get('marca', '').strip()
            cantidad = int(request.form['cantidad'])
            precio_compra = float(request.form['precio_compra'])
            precio_venta = float(request.form['precio_venta'])
            categoria = request.form['categoria'].strip() or 'General'
            subcategoria = request.form.get('subcategoria', '').strip()
            ubicacion = request.form.get('ubicacion', '').strip()
            proveedor = request.form.get('proveedor', '').strip()
            stock_minimo = int(request.form.get('stock_minimo', 5))
            unidad_medida = request.form.get('unidad_medida', 'unidad').strip()
            
            # Validaciones similares al crear producto
            if not nombre:
                flash('El nombre del producto es obligatorio', 'error')
                return render_template('ferreteria_form.html', product=product, 
                                     categories=get_categories(), brands=get_brands())
            
            if product_exists_by_name(nombre, product_id):
                flash('Ya existe otro producto con ese nombre', 'error')
                return render_template('ferreteria_form.html', product=product, 
                                     categories=get_categories(), brands=get_brands())
            
            if precio_venta <= precio_compra:
                flash('El precio de venta debe ser mayor al precio de compra', 'warning')
            
            # Actualizar en base de datos
            with get_db_connection() as conn:
                conn.execute('''
                    UPDATE productos 
                    SET codigo=?, nombre=?, descripcion=?, marca=?, cantidad=?, 
                        precio_compra=?, precio_venta=?, categoria=?, subcategoria=?, 
                        ubicacion=?, proveedor=?, stock_minimo=?, unidad_medida=?,
                        fecha_actualizacion=CURRENT_TIMESTAMP
                    WHERE id=?
                ''', (codigo, nombre, descripcion, marca, cantidad, precio_compra, 
                     precio_venta, categoria, subcategoria, ubicacion, proveedor, 
                     stock_minimo, unidad_medida, product_id))
                conn.commit()
            
            flash('Producto actualizado exitosamente', 'success')
            return redirect(url_for('inventario'))
            
        except ValueError:
            flash('Por favor ingrese valores numéricos válidos', 'error')
        except Exception as e:
            flash(f'Error al actualizar el producto: {str(e)}', 'error')
    
    categories = get_categories()
    brands = get_brands()
    return render_template('ferreteria_form.html', product=product, 
                         categories=categories, brands=brands)

@app.route('/producto/<int:product_id>/eliminar', methods=['POST'])
def eliminar_producto(product_id):
    """Eliminar un producto"""
    try:
        product = get_product_by_id(product_id)
        
        if not product:
            flash('Producto no encontrado', 'error')
            return redirect(url_for('inventario'))
        
        with get_db_connection() as conn:
            conn.execute('DELETE FROM productos WHERE id = ?', (product_id,))
            conn.commit()
        
        flash('Producto eliminado exitosamente', 'success')
        
    except Exception as e:
        flash(f'Error al eliminar el producto: {str(e)}', 'error')
    
    return redirect(url_for('inventario'))

@app.route('/buscar')
def buscar():
    """Página de búsqueda"""
    term = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'nombre')
    results = []
    
    if term:
        results = search_products(term, search_type)
    
    categories = get_categories()
    brands = get_brands()
    return render_template('ferreteria_buscar.html', 
                         results=results, 
                         term=term, 
                         search_type=search_type,
                         categories=categories,
                         brands=brands)

@app.route('/producto/<int:product_id>')
def ver_producto(product_id):
    """Ver detalles de un producto"""
    product = get_product_by_id(product_id)
    
    if not product:
        flash('Producto no encontrado', 'error')
        return redirect(url_for('inventario'))
    
    return render_template('ferreteria_detalle.html', product=product)

@app.route('/stock-bajo')
def stock_bajo():
    """Página de productos con stock bajo"""
    products = get_low_stock_products()
    return render_template('ferreteria_stock_bajo.html', products=products)

@app.route('/api/stats')
def api_stats():
    """API para obtener estadísticas en formato JSON"""
    return jsonify(get_stats())

# Filtros personalizados para Jinja2
@app.template_filter('currency')
def currency_filter(amount):
    """Filtro para formatear moneda"""
    return f"${amount:,.2f}"

@app.template_filter('percentage')
def percentage_filter(cost, sale):
    """Filtro para calcular porcentaje de ganancia"""
    if cost and cost > 0:
        return f"{((sale - cost) / cost * 100):.1f}%"
    return "0%"

@app.template_filter('datetime')
def datetime_filter(date_string):
    """Filtro para formatear fecha"""
    if date_string:
        try:
            dt = datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return dt.strftime('%d/%m/%Y %H:%M')
        except:
            return date_string
    return ''

# Manejo de errores
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Crear directorio para la base de datos si no existe
    os.makedirs(os.path.dirname(os.path.abspath(DATABASE)) if os.path.dirname(DATABASE) else '.', exist_ok=True)
    
    # Inicializar base de datos
    init_db()
    
    # Ejecutar aplicación
    app.run(debug=True, host='0.0.0.0', port=5000)
    