from datetime import date
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models import db, Mantenimiento, Equipo

mantenimientos_bp = Blueprint('mantenimientos', __name__, url_prefix='/mantenimientos')

@mantenimientos_bp.route('/')
@login_required
def index():
    mantenimientos = Mantenimiento.query.order_by(Mantenimiento.fecha.desc()).all()
    return render_template('mantenimientos/index.html', mantenimientos=mantenimientos)

@mantenimientos_bp.route('/nuevo/<int:equipo_id>', methods=['GET', 'POST'])
@login_required
def nuevo(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    if request.method == 'POST':
        mantenimiento = Mantenimiento(
            equipo_id=equipo.id,
            fecha=request.form.get('fecha'),
            tipo=request.form.get('tipo'),
            actividades=request.form.get('actividades'),
            tecnico_responsable=request.form.get('tecnico_responsable'),
            observaciones=request.form.get('observaciones'),
            updated_by=current_user.id
        )
        db.session.add(mantenimiento)
        db.session.commit()
        flash(f'Mantenimiento registrado correctamente para el equipo {equipo.codigo}.', 'success')
        return redirect(url_for('mantenimientos.historial', equipo_id=equipo.id))
    return render_template('mantenimientos/nuevo.html', equipo=equipo, today=date.today())

@mantenimientos_bp.route('/historial/<int:equipo_id>')
@login_required
def historial(equipo_id):
    equipo = Equipo.query.get_or_404(equipo_id)
    mantenimientos = Mantenimiento.query.filter_by(equipo_id=equipo_id)\
                                        .order_by(Mantenimiento.fecha.desc()).all()
    return render_template('mantenimientos/historial.html',
                           equipo=equipo, mantenimientos=mantenimientos)