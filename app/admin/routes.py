from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import db, Usuario
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def solo_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.es_admin():
            flash('No tienes permisos para acceder a esta sección.', 'danger')
            return redirect(url_for('reportes.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@solo_admin
def index():
    usuarios = Usuario.query.order_by(Usuario.nombre).all()
    return render_template('admin/index.html', usuarios=usuarios)

@admin_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
@solo_admin
def nuevo():
    if request.method == 'POST':
        if Usuario.query.filter_by(username=request.form.get('username')).first():
            flash('Ese nombre de usuario ya existe.', 'danger')
            return redirect(url_for('admin.nuevo'))
        usuario = Usuario(
            nombre=request.form.get('nombre'),
            username=request.form.get('username'),
            rol=request.form.get('rol'),
        )
        usuario.set_password(request.form.get('password'))
        db.session.add(usuario)
        db.session.commit()
        flash(f'Usuario {usuario.username} creado correctamente.', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/nuevo.html')

@admin_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
@solo_admin
def editar(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == 'POST':
        usuario.nombre = request.form.get('nombre')
        usuario.rol = request.form.get('rol')
        usuario.activo = request.form.get('activo') == 'true'
        nueva_password = request.form.get('password')
        if nueva_password:
            usuario.set_password(nueva_password)
        db.session.commit()
        flash(f'Usuario {usuario.username} actualizado correctamente.', 'success')
        return redirect(url_for('admin.index'))
    return render_template('admin/editar.html', usuario=usuario)

@admin_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
@solo_admin
def eliminar(id):
    usuario = Usuario.query.get_or_404(id)
    if usuario.id == current_user.id:
        flash('No puedes eliminar tu propio usuario.', 'danger')
        return redirect(url_for('admin.index'))
    username = usuario.username
    db.session.delete(usuario)
    db.session.commit()
    flash(f'Usuario {username} eliminado correctamente.', 'success')
    return redirect(url_for('admin.index'))