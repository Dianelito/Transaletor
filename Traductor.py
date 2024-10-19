import re
import os
from deep_translator import GoogleTranslator
from tqdm import tqdm
import time
import logging

# Configuración de logging
logging.basicConfig(filename='traductor.log', level=logging.ERROR)

def translate_text_between_apostrophes(file_path, output_file_path, progress_bar):
    # Inicializa el traductor
    translator = GoogleTranslator(source='en', target='es')
    
    # Lee el archivo de entrada
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Encuentra todos los textos entre ' '
    matches = re.findall(r"'(.*?)'", content)
    
    # Encuentra los textos después de "material:"
    materials = set(re.findall(r"material:\s*'(.*?)'", content))
    
    # Encuentra los textos entre {}
    ignored_texts = set(re.findall(r"\{(.*?)\}", content))
    
    # Procesa el contenido para reemplazar los textos no deseados con un marcador
    def mark_text(content, search, marker):
        # Escapa los caracteres especiales en el texto a buscar
        search = re.escape(search)
        # Reemplaza el texto en el contenido
        return re.sub(f"'{search}'", f"'{marker}'", content)
    
    # Reemplaza el texto entre {} con un marcador temporal
    content_with_marker = mark_text(content, "{", "__START_MARKER__")
    content_with_marker = mark_text(content_with_marker, "}", "__END_MARKER__")
    
    translated_content = content_with_marker

    # Traduce solo los textos que no están en ignored_texts ni en materials
    for match in matches:
        if match not in materials and match not in ignored_texts:
            try:
                # Traduce el texto encontrado
                translated_text = translator.translate(match)
                # Reemplaza el texto original por el traducido en el contenido
                translated_content = mark_text(translated_content, match, translated_text)
                progress_bar.update(1)
            except Exception as e:
                # Registra el error y continua con el siguiente texto
                logging.error(f"Error al traducir '{match}': {e}")
    
    # Restaura el texto entre {} al contenido traducido
    translated_content = translated_content.replace("__START_MARKER__", "{")
    translated_content = translated_content.replace("__END_MARKER__", "}")
    
    # Guarda el contenido traducido al finalizar
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(translated_content)

def translate_files_in_directory(directory_path):
    files_translated = False
    files_to_translate = [f for f in os.listdir(directory_path) if f.endswith(('.yml', '.txt', '.json'))]
    total_files = len(files_to_translate)
    
    if total_files == 0:
        print("Archivos no encontrados para traducir")
        return

    # Configura la barra de progreso
    with tqdm(total=total_files, desc="Traduciendo archivos", unit="archivo") as progress_bar:
        for file in files_to_translate:
            file_path = os.path.join(directory_path, file)
            output_file_path = os.path.join(directory_path, f"{os.path.splitext(file)[0]}-traducido{os.path.splitext(file)[1]}")
            print(f'Traduciendo {file_path} a {output_file_path}...')
            translate_text_between_apostrophes(file_path, output_file_path, progress_bar)
            files_translated = True
    
    if files_translated:
        print("Traducción completada.")

if __name__ == "__main__":
    # Obtén la ruta de la carpeta donde se encuentra el script
    current_directory = os.path.dirname(os.path.abspath(__file__))
    print(f"Buscando archivos en la carpeta: {current_directory}")
    translate_files_in_directory(current_directory)
    
    # Espera a que el usuario cierre el script manualmente
    input("Presiona Enter para cerrar...")
