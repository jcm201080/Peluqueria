import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/servicios')
def servicios():
    return render_template('servicios.html')


# Configurar la carpeta donde están las imágenes
IMAGE_FOLDER = 'static/img'
IMAGES_PER_PAGE = 20  # Número de imágenes por página

@app.route('/fotos')
def fotos():
    # Carpeta donde están las imágenes
    folder = os.path.join(app.static_folder, "img/fotos")

    # Obtener todas las imágenes de la carpeta
    imagenes = [f"img/fotos/{img}" for img in os.listdir(folder) if img.endswith(('png', 'jpg', 'jpeg', 'gif'))]

    # Paginación
    page = request.args.get('page', 1, type=int)
    per_page = 20  # Número de imágenes por página
    total_pages = (len(imagenes) + per_page - 1) // per_page  # Calcular total de páginas

    start = (page - 1) * per_page
    end = start + per_page
    imagenes_pagina = imagenes[start:end]

    print(f"Total de imágenes detectadas: {len(imagenes)}")
    print(imagenes)  # Para ver la lista de archivos detectados

    return render_template('fotos.html', imagenes=imagenes_pagina, page=page, total_pages=total_pages)


@app.route('/contacto')
def contacto():
    return render_template('contacto.html')




if __name__ == '__main__':
    # Asegúrate de que el servidor se ejecuta en todas las interfaces de red (0.0.0.0)
    port = int(os.environ.get("PORT", 5000))  # Usa el puerto de Render
    app.run(host='0.0.0.0', port=port)



