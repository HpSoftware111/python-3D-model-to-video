## script para convertir grafico textanalizer a video mp4 ###
## Genera dos videos: uno con fondo negro y otro con fondo blanco
## Sin zoom, sin slow motion - rotación normal a 360 grados


import time
import math
import base64
import numpy as np
from io import BytesIO
from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import cv2
import os
from pathlib import Path

# Workaround para webdriver_manager encoding issue
os.environ['WDM_LOG_LEVEL'] = '0'
try:
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    ChromeDriverManager = None

# ==============================
# CONFIGURACIÓN
# ==============================

# Obtener la ruta absoluta del directorio actual
BASE_DIR = Path(__file__).parent.absolute()
HTML_PATH = str(BASE_DIR / "grafico.html")

OUTPUT_VIDEO_BLACK = str(BASE_DIR / "grafico_black.mp4")
OUTPUT_VIDEO_WHITE = str(BASE_DIR / "grafico_white.mp4")

FPS = 30
DURATION = 30
FRAMES = FPS * DURATION

WIDTH = 1600
HEIGHT = 1200

# ==============================
# FUNCIÓN PARA GENERAR VIDEO
# ==============================

def generar_video(background_color, output_path, video_name):
    """
    Genera un video con el color de fondo especificado.
    background_color: 'black' o 'white'
    """
    print(f"\n{'='*50}")
    print(f"Generando video: {video_name}")
    print(f"Fondo: {background_color}")
    print(f"{'='*50}\n")
    
    # Inicializar Chrome
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument(f"--window-size={WIDTH},{HEIGHT}")

if ChromeDriverManager:
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        driver = webdriver.Chrome(options=options)
else:
    driver = webdriver.Chrome(options=options)

    try:
html_url = "file:///" + HTML_PATH.replace("\\", "/")
driver.get(html_url)

# Esperar a que Plotly cargue completamente
        time.sleep(5)

        # Esperar a que el gráfico esté listo
driver.execute_script("""
    return new Promise((resolve) => {
        if (typeof Plotly !== 'undefined') {
            var checkReady = setInterval(function() {
                var plotDiv = document.querySelector('.plotly-graph-div');
                if (plotDiv && plotDiv.data) {
                    clearInterval(checkReady);
                    resolve(true);
                }
            }, 100);
            setTimeout(() => {
                clearInterval(checkReady);
                resolve(true);
            }, 10000);
        } else {
            resolve(true);
        }
    });
""")

# Obtener ID del div Plotly
plot_div = driver.find_element("xpath", "//div[contains(@class,'plotly-graph-div')]")
plot_id = plot_div.get_attribute("id")

        # Configurar según el color de fondo
        bg_color = 'black' if background_color == 'black' else 'white'
        line_color = 'rgba(255, 255, 255, 1)' if background_color == 'black' else 'rgba(0, 0, 0, 1)'
        
        driver.execute_script(f"""
            // Establecer fondo en el body
            document.body.style.backgroundColor = '{bg_color}';
            document.body.style.margin = '0';
            document.body.style.padding = '0';
            
            // Configurar Plotly
            var gd = document.getElementById("{plot_id}");
            if (gd && gd.data) {{
                // Aumentar el grosor y brillo de las líneas
                var updatedData = gd.data.map(function(trace) {{
                    if (trace.type === 'scatter3d' && trace.mode && trace.mode.includes('lines')) {{
                        if (!trace.line) trace.line = {{}};
                        trace.line.width = (trace.line.width || 3) * 2;
                        
                        if (trace.line.color) {{
                            var color = trace.line.color;
                            if (typeof color === 'string' && color.startsWith('rgba')) {{
                                var match = color.match(/rgba?\\((\\d+),(\\d+),(\\d+)/);
                                if (match) {{
                                    var r = Math.min(255, parseInt(match[1]) + 100);
                                    var g = Math.min(255, parseInt(match[2]) + 100);
                                    var b = Math.min(255, parseInt(match[3]) + 100);
                                    trace.line.color = 'rgba(' + r + ',' + g + ',' + b + ',1)';
                                }}
                            }} else if (typeof color === 'string' && color.startsWith('rgb')) {{
                                var match = color.match(/rgb\\((\\d+),(\\d+),(\\d+)/);
                                if (match) {{
                                    var r = Math.min(255, parseInt(match[1]) + 100);
                                    var g = Math.min(255, parseInt(match[2]) + 100);
                                    var b = Math.min(255, parseInt(match[3]) + 100);
                                    trace.line.color = 'rgb(' + r + ',' + g + ',' + b + ')';
                                }}
                            }}
                        }} else {{
                            trace.line.color = '{line_color}';
                        }}
                    }}
                    if (trace.marker && trace.marker.color) {{
                        var mColor = trace.marker.color;
                        if (typeof mColor === 'string' && mColor.startsWith('rgba')) {{
                            var match = mColor.match(/rgba?\\((\\d+),(\\d+),(\\d+)/);
                            if (match) {{
                                var r = Math.min(255, parseInt(match[1]) + 50);
                                var g = Math.min(255, parseInt(match[2]) + 50);
                                var b = Math.min(255, parseInt(match[3]) + 50);
                                trace.marker.color = 'rgba(' + r + ',' + g + ',' + b + ',0.8)';
                            }}
                        }}
                    }}
                    return trace;
                }});
                
                Plotly.restyle(gd, updatedData);
                
                Plotly.relayout(gd, {{
                    'scene.bgcolor': '{bg_color}',
                    'paper_bgcolor': '{bg_color}',
                    'plot_bgcolor': '{bg_color}',
                    // Ocultar ejes X, Y, Z completamente
                    'scene.xaxis.visible': false,
                    'scene.yaxis.visible': false,
                    'scene.zaxis.visible': false,
                    'scene.xaxis.showticklabels': false,
                    'scene.yaxis.showticklabels': false,
                    'scene.zaxis.showticklabels': false,
                    'scene.xaxis.title': {{'text': ''}},
                    'scene.yaxis.title': {{'text': ''}},
                    'scene.zaxis.title': {{'text': ''}},
                    'scene.xaxis.showgrid': false,
                    'scene.yaxis.showgrid': false,
                    'scene.zaxis.showgrid': false,
                    'scene.xaxis.showbackground': false,
                    'scene.yaxis.showbackground': false,
                    'scene.zaxis.showbackground': false,
                    'scene.xaxis.showspikes': false,
                    'scene.yaxis.showspikes': false,
                    'scene.zaxis.showspikes': false,
                    'scene.xaxis.zeroline': false,
                    'scene.yaxis.zeroline': false,
                    'scene.zaxis.zeroline': false
                }});
            }}
        """)
        
        time.sleep(2)
        
        # Configurar video
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(output_path, fourcc, FPS, (WIDTH, HEIGHT))

if not video.isOpened():
    print("Error: No se pudo abrir el VideoWriter. Intentando con codec alternativo...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
            video = cv2.VideoWriter(output_path.replace('.mp4', '.avi'), fourcc, FPS, (WIDTH, HEIGHT))
    if not video.isOpened():
        raise RuntimeError("No se pudo inicializar el VideoWriter con ningún codec")

        # Generar frames
print(f"Generando {FRAMES} frames...")

for i in range(FRAMES):
    if (i + 1) % 30 == 0:
        print(f"Procesando frame {i + 1}/{FRAMES}...")

            # Vista estática fija - SIN ROTACIÓN, SIN ZOOM, SIN MOVIMIENTO
            # Mantener la misma vista en todos los frames (como tutela app)
            # Solo configurar la cámara una vez al inicio, luego no cambiar
            if i == 0:
                driver.execute_script(
                    f"""
                    var gd = document.getElementById("{plot_id}");
                    Plotly.relayout(gd, {{
                    'scene.camera': {{
                    eye: {{
                    x: 2.5,
                    y: 0.0,
                    z: 1.2
                    }}
                    }}
                    }});
                    """
                )
                time.sleep(0.5)  # Esperar a que se establezca la vista inicial
            
            time.sleep(0.03)

            # Capturar el elemento del gráfico
            try:
                location = plot_div.location
                size = plot_div.size
                
                full_screenshot = driver.get_screenshot_as_png()
                img_arr = np.frombuffer(full_screenshot, np.uint8)
                full_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
                
                if full_frame is not None:
                    x = location['x']
                    y = location['y']
                    w = size['width']
                    h = size['height']
                    
                    x = max(0, int(x))
                    y = max(0, int(y))
                    w = min(w, full_frame.shape[1] - x)
                    h = min(h, full_frame.shape[0] - y)
                    
                    if w > 0 and h > 0:
                        graph_frame = full_frame[y:y+h, x:x+w]
                    else:
                        graph_frame = full_frame
                else:
                    graph_frame = None
                    
            except Exception as e:
                print(f"Error capturando elemento: {e}, usando screenshot completo")
    png = driver.get_screenshot_as_png()
                img_arr = np.frombuffer(png, np.uint8)
                graph_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
            
            # Procesar frame
            if graph_frame is not None and graph_frame.size > 0:
                # Crear frame con el color de fondo
                if background_color == 'black':
                    frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
                else:
                    frame = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255
                
                graph_h, graph_w = graph_frame.shape[:2]
                scale = min(WIDTH / graph_w, HEIGHT / graph_h)
                new_w = int(graph_w * scale)
                new_h = int(graph_h * scale)
                
                resized_graph = cv2.resize(graph_frame, (new_w, new_h))
                
                # Mejorar visibilidad solo para fondo negro
                if background_color == 'black':
                    enhanced = resized_graph.astype(np.float32)
                    enhanced = enhanced + 30  # Aumentar brillo
                    enhanced = enhanced * 1.3  # Aumentar contraste
                    enhanced = np.clip(enhanced, 0, 255)
                    resized_graph = enhanced.astype(np.uint8)
                
                y_offset = (HEIGHT - new_h) // 2
                x_offset = (WIDTH - new_w) // 2
                
                frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized_graph
                
        video.write(frame)
    else:
                print(f"Warning: Frame {i} es None o vacío, saltando...")

video.release()
        print(f"\n✓ Video {video_name} generado exitosamente: {output_path}")
        
    finally:
driver.quit()

# ==============================
# GENERAR AMBOS VIDEOS
# ==============================

if __name__ == "__main__":
    print("\n" + "="*60)
    print(" GENERADOR DE VIDEOS PLOTLY")
    print("="*60)
    print(f"Frames totales: {FRAMES}")
    print(f"Duración: {DURATION} segundos")
    print(f"FPS: {FPS}")
    print(f"Resolución: {WIDTH}x{HEIGHT}")
    print("Vista: Estática fija (sin rotación, sin zoom, sin movimiento)")
    print("Igual a tutela app - vista normal")
    print("="*60)
    
    # Generar video con fondo negro
    generar_video('black', OUTPUT_VIDEO_BLACK, 'BLACK VIEW')
    
    # Generar video con fondo blanco
    generar_video('white', OUTPUT_VIDEO_WHITE, 'WHITE VIEW')
    
    print("\n" + "="*60)
    print(" ¡AMBOS VIDEOS GENERADOS EXITOSAMENTE!")
    print("="*60)
    print(f"Video negro: {OUTPUT_VIDEO_BLACK}")
    print(f"Video blanco: {OUTPUT_VIDEO_WHITE}")
    print("="*60 + "\n")
