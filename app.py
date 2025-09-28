from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = 'inventario_seguro_2024'

# Base de datos
DATABASE = 'inventario.db'


# =========================
# 🔧 Funciones de utilidad
# =========================
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Crea la tabla productos si no existe"""
    with get_db_connection() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT,
                marca TEXT,
                cantidad INTEGER NOT NULL,
                precio_compra REAL NOT NULL,
                precio_venta REAL NOT NULL,
                categoria TEXT
            )
        ''')
        conn.commit()


# =========================
# 📌 Rutas del CRUD
# =========================

# a. Crear Producto
@app.route('/crear', methods=['GET', 'POST'])
def crear_producto():
    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        marca = request.form.get('marca', '').strip()
        cantidad = request.form.get('cantidad', 0)
        precio_compra = request.form.get('precio_compra', 0)
        precio_venta = request.form.get('precio_venta', 0)
        categoria = request.form.get('categoria', '').strip()

        # Validaciones básicas
        if not nombre or float(precio_compra) < 0 or float(precio_venta) < 0:
            flash("⚠️ Todos los campos obligatorios deben estar correctamente llenos.", "danger")
            return redirect(url_for('crear_producto'))

        # Guardar producto
        with get_db_connection() as conn:
            conn.execute('''
                INSERT INTO productos (nombre, descripcion, marca, cantidad, precio_compra, precio_venta, categoria)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (nombre, descripcion, marca, cantidad, precio_compra, precio_venta, categoria))
            conn.commit()

        flash("✅ Producto registrado exitosamente.", "success")
        return redirect(url_for('listar_productos'))

    return render_template('formulario.html', titulo="Registrar Producto")


# b. Leer Productos
@app.route('/productos')
def listar_productos():
    with get_db_connection() as conn:
        productos = conn.execute("SELECT * FROM productos ORDER BY id DESC").fetchall()
    return render_template('productos.html', productos=productos)


# c. Actualizar Producto
@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_producto(id):
    with get_db_connection() as conn:
        producto = conn.execute("SELECT * FROM productos WHERE id = ?", (id,)).fetchone()

    if not producto:
        flash("❌ Producto no encontrado.", "danger")
        return redirect(url_for('listar_productos'))

    if request.method == 'POST':
        nombre = request.form['nombre'].strip()
        descripcion = request.form.get('descripcion', '').strip()
        marca = request.form.get('marca', '').strip()
        cantidad = request.form.get('cantidad', 0)
        precio_compra = request.form.get('precio_compra', 0)
        precio_venta = request.form.get('precio_venta', 0)
        categoria = request.form.get('categoria', '').strip()

        if not nombre:
            flash("⚠️ El nombre es obligatorio.", "warning")
            return redirect(url_for('editar_producto', id=id))

        with get_db_connection() as conn:
            conn.execute('''
                UPDATE productos
                SET nombre=?, descripcion=?, marca=?, cantidad=?, precio_compra=?, precio_venta=?, categoria=?
                WHERE id=?
            ''', (nombre, descripcion, marca, cantidad, precio_compra, precio_venta, categoria, id))
            conn.commit()

        flash("✅ Producto actualizado exitosamente.", "success")
        return redirect(url_for('listar_productos'))

    return render_template('formulario.html', producto=producto, titulo="Editar Producto")


# d. Eliminar Producto
@app.route('/eliminar/<int:id>', methods=['POST'])
def eliminar_producto(id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM productos WHERE id = ?", (id,))
        conn.commit()
    flash("🗑️ Producto eliminado exitosamente.", "success")
    return redirect(url_for('listar_productos'))


# Página principal
@app.route('/')
def home():
    return redirect(url_for('listar_productos'))


# =========================
# 🚀 Inicializar app
# =========================
if __name__ == '__main__':
    if not os.path.exists(DATABASE):
        init_db()
    app.run(debug=True)
