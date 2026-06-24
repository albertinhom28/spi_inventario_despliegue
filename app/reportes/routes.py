from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Equipo, Mantenimiento

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def index():
    # Conteos generales
    total_equipos     = Equipo.query.count()
    equipos_operativos = Equipo.query.filter_by(estado='operativo').count()
    equipos_mtto      = Equipo.query.filter_by(estado='mantenimiento').count()
    equipos_desincorp      = Equipo.query.filter_by(estado='desincorporado').count()
    equipos_averiados    = Equipo.query.filter_by(estado='averiado').count()
    total_mantenimientos = Mantenimiento.query.count()
    preventivos       = Mantenimiento.query.filter_by(tipo='preventivo').count()
    correctivos       = Mantenimiento.query.filter_by(tipo='correctivo').count()

    # Alertas
    equipos = Equipo.query.filter(Equipo.estado != 'baja').all()
    vencidos  = len([e for e in equipos if e.nivel_alerta() == 'vencido'])
    pendientes = len([e for e in equipos if e.nivel_alerta() == 'pendiente'])
    proximos  = len([e for e in equipos if e.nivel_alerta() == 'proximo'])
    alertas_activas = vencidos + pendientes + proximos

    # Últimos 5 mantenimientos
    ultimos_mantenimientos = Mantenimiento.query.order_by(
        Mantenimiento.fecha.desc()).limit(5).all()

    return render_template('reportes/index.html',
        total_equipos=total_equipos,
        equipos_operativos=equipos_operativos,
        equipos_mtto=equipos_mtto,
        equipos_desincorp=equipos_desincorp,
        equipos_averiados=equipos_averiados,
        total_mantenimientos=total_mantenimientos,
        preventivos=preventivos,
        correctivos=correctivos,
        alertas_activas=alertas_activas,
        vencidos=vencidos,
        pendientes=pendientes,
        proximos=proximos,
        ultimos_mantenimientos=ultimos_mantenimientos,
    )