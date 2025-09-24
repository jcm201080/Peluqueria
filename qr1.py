import qrcode

# Dirección IP de tu red local y puerto
url = "https://67c7-37-11-132-93.ngrok-free.app"


# Generar el código QR
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)

# Crear la imagen del código QR
qr.add_data(url)
qr.make(fit=True)

# Guardar la imagen del código QR
img = qr.make_image(fill_color="black", back_color="white")
img.save("qr_code_Ngrok.png")