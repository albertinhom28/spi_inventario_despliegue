from flask import Blueprint, render_template, Response
from flask_login import login_required, current_user
from app.models import Equipo, Mantenimiento
from xhtml2pdf import pisa
import io
from datetime import date

reportes_bp = Blueprint('reportes', __name__, url_prefix='/reportes')

@reportes_bp.route('/')
@login_required
def index():
    total_equipos        = Equipo.query.count()
    equipos_operativos   = Equipo.query.filter_by(estado='operativo').count()
    equipos_mtto         = Equipo.query.filter_by(estado='mantenimiento').count()
    equipos_desincorp    = Equipo.query.filter_by(estado='desincorporado').count()
    equipos_averiados    = Equipo.query.filter_by(estado='averiado').count()
    total_mantenimientos = Mantenimiento.query.count()
    preventivos          = Mantenimiento.query.filter_by(tipo='preventivo').count()
    correctivos          = Mantenimiento.query.filter_by(tipo='correctivo').count()

    equipos = Equipo.query.filter(Equipo.estado != 'desincorporado').all()
    vencidos   = len([e for e in equipos if e.nivel_alerta() == 'vencido'])
    pendientes = len([e for e in equipos if e.nivel_alerta() == 'pendiente'])
    proximos   = len([e for e in equipos if e.nivel_alerta() == 'proximo'])
    alertas_activas = vencidos + pendientes + proximos

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

@reportes_bp.route('/exportar-pdf')
@login_required
def exportar_pdf():
    equipos = Equipo.query.order_by(Equipo.codigo).all()
    fecha_generacion = date.today().strftime('%d/%m/%Y')

    html = render_template('reportes/reporte_pdf.html',
        equipos=equipos,
        fecha_generacion=fecha_generacion,
        total=len(equipos),
        operativos=len([e for e in equipos if e.estado == 'operativo']),
        en_mtto=len([e for e in equipos if e.estado == 'mantenimiento']),
        averiados=len([e for e in equipos if e.estado == 'averiado']),
        desincorporados=len([e for e in equipos if e.estado == 'desincorporado']),
    )

    pdf_buffer = io.BytesIO()
    pisa.CreatePDF(io.StringIO(html), dest=pdf_buffer)
    pdf_buffer.seek(0)

    return Response(
        pdf_buffer,
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=reporte_inventario_spi_{date.today()}.pdf'}
    )