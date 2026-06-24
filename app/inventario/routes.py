from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import db, Equipo

inventario_bp = Blueprint('inventario', __name__, url_prefix='/inventario')

@inventario_bp.route('/')
@login_required
def index():
    equipos = Equipo.query.order_by(Equipo.codigo).all()
    return render_template('inventario/index.html', equipos=equipos)

@inventario_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    if request.method == 'POST':
        equipo = Equipo(
            codigo=request.form.get('codigo'),
            marca=request.form.get('marca'),
            modelo=request.form.get('modelo'),
            serial=request.form.get('serial'),
            departamento=request.form.get('departamento'),
            tipo_disco=request.form.get('tipo_disco'),
            capacidad_disco=request.form.get('capacidad_disco') or None,
            ram_gb=request.form.get('ram_gb'),
            sistema_operativo=request.form.get('sistema_operativo'),
            estado=request.form.get('estado'),
            updated_by=current_user.id
        )
        db.session.add(equipo)
        db.session.commit()
        flash(f'Equipo {equipo.codigo} registrado correctamente.', 'success')
        return redirect(url_for('inventario.index'))
    return render_template('inventario/nuevo.html')

@inventario_bp.route('/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar(id):
    equipo = Equipo.query.get_or_404(id)
    if request.method == 'POST':
        equipo.marca = request.form.get('marca')
        equipo.modelo = request.form.get('modelo')
        equipo.serial = request.form.get('serial')
        equipo.departamento = request.form.get('departamento')
        equipo.tipo_disco = request.form.get('tipo_disco')
        equipo.capacidad_disco = request.form.get('capacidad_disco') or None
        equipo.ram_gb = request.form.get('ram_gb')
        equipo.sistema_operativo = request.form.get('sistema_operativo')
        equipo.estado = request.form.get('estado')
        equipo.updated_by = current_user.id
        db.session.commit()
        flash(f'Equipo {equipo.codigo} actualizado correctamente.', 'success')
        return redirect(url_for('inventario.index'))
    return render_template('inventario/editar.html', equipo=equipo)

@inventario_bp.route('/eliminar/<int:id>', methods=['POST'])
@login_required
def eliminar(id):
    equipo = Equipo.query.get_or_404(id)
    codigo = equipo.codigo
    db.session.delete(equipo)
    db.session.commit()
    flash(f'Equipo {codigo} eliminado correctamente.', 'success')
    return redirect(url_for('inventario.index'))