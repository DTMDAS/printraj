import os
from flask import Flask, request, jsonify
from PIL import Image, ImageWin
import win32print
import win32ui

app = Flask(__name__)

# Upload hone wali photos ka folder
UPLOAD_FOLDER = 'received_photos'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def print_photo(image_path):
    try:
        # Aapke Windows PC ka DEFAULT PRINTER select karega
        printer_name = win32print.GetDefaultPrinter()
        print(f"Printing job sent to printer: {printer_name}")

        hprinter = win32print.OpenPrinter(printer_name)
        
        # Image open karein
        img = Image.open(image_path)
        
        # Windows Printer DC Setup
        hdc = win32ui.CreateDC()
        hdc.CreatePrinterDC(printer_name)
        hdc.StartDoc("QR Photo Print")
        hdc.StartPage()

        # Page ka print area get karein
        printable_width = hdc.GetDeviceCaps(110)
        printable_height = hdc.GetDeviceCaps(111)

        # Image ko page par fit karne ke liye resize karein
        img.thumbnail((printable_width, printable_height), Image.Resampling.LANCZOS)

        dib = ImageWin.Dib(img)
        dib.draw(hdc.GetHandleOutput(), (0, 0, img.size[0], img.size[1]))

        hdc.EndPage()
        hdc.EndDoc()
        hdc.DeleteDC()
        win32print.ClosePrinter(hprinter)
        return True
    except Exception as e:
        print(f"Printing Error: {e}")
        return False

@app.route('/upload', methods=['POST'])
def handle_upload():
    if 'photo' not in request.files:
        return jsonify({'message': 'Photo file nahi mili'}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({'message': 'Koi photo select nahi hui'}), 400

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    # Image ko Printer par bhejein
    if print_photo(filepath):
        return jsonify({'message': 'Photo successfully printer ko bhej di gayi hai!'}), 200
    else:
        return jsonify({'message': 'Print failed! Check karein printer USB se connect aur ON hai ya nahi.'}), 500

if __name__ == '__main__':
    print("Print Server Running on Port 5000...")
    app.run(host='0.0.0.0', port=5000)
