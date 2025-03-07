import qrcode

# La URL que deseas convertir en un código QR (tu dirección IP local)
url = "http://192.168.32.189:5000"  # Asegúrate de reemplazar con tu IP

# Generar el código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(url)
qr.make(fit=True)

# Crear la imagen del código QR
img = qr.make_image(fill='black', back_color='white')

# Guardar la imagen del código QR
img.save("codigo_qr.png")
