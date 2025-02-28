import easyocr
import csv
import tkinter as tk
from tkinter import filedialog, messagebox
import os
from PIL import Image, ImageGrab



def normalize_key(key):
    """
    Normaliza la clave para comparación: elimina espacios, símbolos y convierte a minúsculas.
    """
    return key.lower().replace(" ", "").replace("é", "e").replace("í", "i")

# Columnas actualizadas del CSV 
csv_columns = [
    'Origen genético', 'Efecto', 'Sabor','Tipo de variedad', 'THC', 'CBD', 'Tipo'
]

def process_screenshot(image_path):
    try:
        reader = easyocr.Reader(['es'])
        result = reader.readtext(image_path, detail=0, paragraph=True)

        data = {}
        current_key = None  # Rastrea la última clave detectada
        print("=== Líneas OCR detectadas ===")
        
        for line in result:
            line = line.strip()
            print(f"> Línea original: '{line}'")
            
            if ':' in line:
                # Procesar clave-valor en la misma línea
                parts = line.split(':', 1)
                key = parts[0].strip()
                value = parts[1].strip() if len(parts) > 1 else ''
                
                # Buscar coincidencia en columnas
                matched = False
                normalized_key = normalize_key(key)
                for col in csv_columns:
                    if normalize_key(col) == normalized_key:
                        data[col] = value
                        current_key = col if not value else None  # Si hay valor, resetea clave activa
                        print(f"    --> Asignado a '{col}': '{value}'")
                        matched = True
                        break
                if not matched:
                    current_key = None
                    
            elif current_key:
                # Si hay una clave activa, asigna esta línea como su valor
                if data.get(current_key):
                    data[current_key] += " " + line  # Concatena valores (ej: "Afrutado; Cítrico")
                else:
                    data[current_key] = line
                print(f"    --> Valor añadido a '{current_key}': '{line}'")
                
            else:
                print(f"  Línea ignorada (sin clave activa): '{line}'")
                
        return data
    except Exception as e:
        print(f"Error: {e}")
        return None

def save_to_csv(data):
    """
    Guarda el diccionario 'data' en un archivo CSV llamado 'cepas.csv'.
    Si el archivo no existe, escribe primero la cabecera.
    """
    csv_file = 'cepas.csv'
    file_exists = os.path.isfile(csv_file)

    try:
        with open(csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(csv_columns)

            
            row = [data.get(col, 'N/A') for col in csv_columns]
            writer.writerow(row)

        print(f"Datos guardados en '{csv_file}'.")
    except Exception as e:
        print(f"Error guardando en CSV: {e}")

def upload_screenshot():
    """
    Abre una ventana de Tkinter para que el usuario suba la captura desde el portapapeles o desde un archivo.
    """
    root = tk.Tk()
    root.geometry('200x200')
    root.title("Subir Captura")

    def load_image():
        nonlocal image_path
        try:
            # Intenta obtener imagen desde el portapapeles
            img = ImageGrab.grabclipboard()
            if img and messagebox.askyesno("Portapapeles", "¿Pegar imagen desde el portapapeles?"):
                temp_file = 'temp_screenshot.png'
                img.save(temp_file)
                image_path = temp_file
            else:
                # Si no hay imagen en portapapeles o el usuario elige 'No'
                image_path = filedialog.askopenfilename(
                    filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp"), ("Todos los archivos", "*.*")]
                )
            root.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la imagen: {e}")
            root.destroy()

    image_path = None
    tk.Button(root, text="Subir Screenshot", command=load_image).pack(pady=80)
    root.mainloop()
    return image_path

def main():
    print("=== Extracción de Datos de Captura (EasyOCR) ===")
    print("Por favor, sube la captura con los detalles de la cepa.\n")

    image_path = upload_screenshot()
    if not image_path:
        print("No se ha proporcionado ninguna imagen. Saliendo.")
        return

    screenshot_data = process_screenshot(image_path)
    if not screenshot_data:
        print("No se pudo extraer información de la captura. Saliendo.")
        return

    save_to_csv(screenshot_data)

    # Elimina el archivo temporal si se usó
    if os.path.exists('temp_screenshot.png'):
        os.remove('temp_screenshot.png')

    print("Proceso finalizado con éxito.")

if __name__ == "__main__":
    main()