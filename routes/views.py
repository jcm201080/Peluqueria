from flask import Blueprint, render_template, request, redirect, url_for, flash
from database.models import db, Valoracion
from sqlalchemy import func  # ¡NUEVO! Necesario para calcular medias matemáticas

views_bp = Blueprint('views', __name__)

@views_bp.route('/valorar', methods=['GET', 'POST'])
def valorar():
    if request.method == 'POST':
        # Recogemos las tres notas
        e_servicio = request.form.get('estrellas_servicio')
        e_app = request.form.get('estrellas_app')
        e_reserva = request.form.get('estrellas_reserva')
        comentario = request.form.get('comentario')
        
        if e_servicio and e_app and e_reserva:
            nueva_valoracion = Valoracion(
                estrellas_servicio=int(e_servicio),
                estrellas_app=int(e_app),
                estrellas_reserva=int(e_reserva),
                comentario=comentario
            )
            db.session.add(nueva_valoracion)
            db.session.commit()
            
            flash('¡Gracias por tu tiempo! Tu opinión nos ayuda a ser mejores.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Por favor, puntúa todas las opciones con estrellas.', 'error')
            
    # --- LÓGICA GET: Calcular medias para mostrarlas ---
    medias = db.session.query(
        func.avg(Valoracion.estrellas_servicio).label('media_servicio'),
        func.avg(Valoracion.estrellas_app).label('media_app'),
        func.avg(Valoracion.estrellas_reserva).label('media_reserva'),
        func.count(Valoracion.id).label('total')
    ).first()

    # Formateamos las notas a 1 decimal (ej: 4.8) o ponemos 0 si aún no hay votos
    stats = {
        'servicio': round(medias.media_servicio, 1) if medias.media_servicio else 0,
        'app': round(medias.media_app, 1) if medias.media_app else 0,
        'reserva': round(medias.media_reserva, 1) if medias.media_reserva else 0,
        'total': medias.total if medias.total else 0
    }

    return render_template('valorar.html', stats=stats)