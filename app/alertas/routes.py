from flask import Blueprint, render_template
from flask_login import login_required
from app.models import Equipo

alertas_bp = Blueprint('alertas', __name__, url_prefix='/alertas')

@alertas_bp.route('/')
@login_required
def index():
    equipos = Equipo.query.filter(Equipo.estado != 'baja').all()
    
    vencidos  = [e for e in equipos if e.nivel_alerta() == 'vencido']
    pendientes = [e for e in equipos if e.nivel_alerta() == 'pendiente']
    proximos  = [e for e in equipos if e.nivel_alerta() == 'proximo']
    al_dia    = [e for e in equipos if e.nivel_alerta() is None]

    return render_template('alertas/index.html',
                           vencidos=vencidos,
                           pendientes=pendientes,
                           proximos=proximos,
                           al_dia=al_dia)