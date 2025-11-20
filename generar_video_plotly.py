## script para convertir grafico textanalizer a video mp4 ###




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
HTML_PATH = str(BASE_DIR / "grafico.html")  # Usar el HTML original

OUTPUT_VIDEO = str(BASE_DIR / "grafico.mp4")

FPS = 30
DURATION = 30
FRAMES = FPS * DURATION

WIDTH = 1600
HEIGHT = 1200

# ==============================
# INICIALIZAR CHROME HEADLESS
# ==============================

options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")
options.add_argument(f"--window-size={WIDTH},{HEIGHT}")

if ChromeDriverManager:
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    except Exception:
        # Fallback: usar driver del sistema
        driver = webdriver.Chrome(options=options)
else:
    driver = webdriver.Chrome(options=options)

html_url = "file:///" + HTML_PATH.replace("\\", "/")
driver.get(html_url)

# Esperar a que Plotly cargue completamente
time.sleep(5)  # Dar más tiempo para que cargue desde CDN

# Esperar a que el gráfico esté listo usando JavaScript
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

# Configurar página con fondo negro y configurar Plotly con fondo negro, ocultar todos los ejes
driver.execute_script(f"""
    // Establecer fondo negro en el body
    document.body.style.backgroundColor = 'black';
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    
    // Configurar el fondo de la escena 3D de Plotly a negro y ocultar todos los elementos de los ejes
    var gd = document.getElementById("{plot_id}");
    if (gd && gd.data) {{
        // Aumentar el grosor y brillo de las líneas en todos los traces
        var updatedData = gd.data.map(function(trace) {{
            if (trace.type === 'scatter3d' && trace.mode && trace.mode.includes('lines')) {{
                // Aumentar grosor de línea
                if (!trace.line) trace.line = {{}};
                trace.line.width = (trace.line.width || 3) * 2;
                
                // Hacer las líneas más brillantes si tienen color
                if (trace.line.color) {{
                    // Convertir colores oscuros a más brillantes
                    var color = trace.line.color;
                    if (typeof color === 'string' && color.startsWith('rgba')) {{
                        // Extraer valores RGB y aumentar brillo
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
                    // Si no tiene color, usar blanco brillante
                    trace.line.color = 'rgba(255, 255, 255, 1)';
                }}
            }}
            // También mejorar marcadores si existen
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
            'scene.bgcolor': 'black',
            'paper_bgcolor': 'black',
            'plot_bgcolor': 'black',
            // Ocultar ejes X, Y, Z completamente
            'scene.xaxis.visible': false,
            'scene.yaxis.visible': false,
            'scene.zaxis.visible': false,
            // Ocultar etiquetas de los ejes
            'scene.xaxis.showticklabels': false,
            'scene.yaxis.showticklabels': false,
            'scene.zaxis.showticklabels': false,
            // Ocultar títulos de los ejes
            'scene.xaxis.title': {{'text': ''}},
            'scene.yaxis.title': {{'text': ''}},
            'scene.zaxis.title': {{'text': ''}},
            // Ocultar líneas de cuadrícula
            'scene.xaxis.showgrid': false,
            'scene.yaxis.showgrid': false,
            'scene.zaxis.showgrid': false,
            // Ocultar planos de fondo
            'scene.xaxis.showbackground': false,
            'scene.yaxis.showbackground': false,
            'scene.zaxis.showbackground': false,
            // Ocultar spikes (líneas de referencia)
            'scene.xaxis.showspikes': false,
            'scene.yaxis.showspikes': false,
            'scene.zaxis.showspikes': false,
            // Ocultar escalas y rangos visibles
            'scene.xaxis.zeroline': false,
            'scene.yaxis.zeroline': false,
            'scene.zaxis.zeroline': false
        }});
    }}
""")

# Esperar un momento para que se apliquen los estilos y cambios de color
time.sleep(2)

# ==============================
# CONFIGURAR VIDEO
# ==============================

# Intentar usar H.264, si falla usar mp4v
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
# Alternativa: fourcc = cv2.VideoWriter_fourcc(*'avc1') para H.264
video = cv2.VideoWriter(OUTPUT_VIDEO, fourcc, FPS, (WIDTH, HEIGHT))

if not video.isOpened():
    print("Error: No se pudo abrir el VideoWriter. Intentando con codec alternativo...")
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    video = cv2.VideoWriter(OUTPUT_VIDEO.replace('.mp4', '.avi'), fourcc, FPS, (WIDTH, HEIGHT))
    if not video.isOpened():
        raise RuntimeError("No se pudo inicializar el VideoWriter con ningún codec")

# ==============================
# ANIMACIÓN (ROTACIÓN + ZOOM)
# ==============================

print(f"Generando {FRAMES} frames...")

for i in range(FRAMES):
    if (i + 1) % 30 == 0:
        print(f"Procesando frame {i + 1}/{FRAMES}...")

    # Rotación muy lenta (solo 90 grados en todo el video)
    angle = (i / FRAMES) * 90  # Rotación muy lenta y suave
    zoom = 1.0  # Sin zoom, distancia fija

    driver.execute_script(
        f"""
        var gd = document.getElementById("{plot_id}");
        Plotly.relayout(gd, {{
            'scene.camera': {{
                eye: {{
                    x: {zoom} * Math.cos({angle} * Math.PI/180),
                    y: {zoom} * Math.sin({angle} * Math.PI/180),
                    z: 1.2
                }}
            }}
        }});
        """
    )

    time.sleep(0.03)

    # Capturar el elemento del gráfico Plotly
    try:
        # Obtener la ubicación y tamaño del elemento
        location = plot_div.location
        size = plot_div.size
        
        # Capturar toda la pantalla
        full_screenshot = driver.get_screenshot_as_png()
        img_arr = np.frombuffer(full_screenshot, np.uint8)
        full_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
        
        if full_frame is not None:
            # Extraer solo la región del gráfico
            x = location['x']
            y = location['y']
            w = size['width']
            h = size['height']
            
            # Asegurar que las coordenadas estén dentro de los límites
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
        # Fallback: capturar toda la pantalla
        png = driver.get_screenshot_as_png()
        img_arr = np.frombuffer(png, np.uint8)
        graph_frame = cv2.imdecode(img_arr, cv2.IMREAD_COLOR)
    
    # Verificar que el frame sea válido
    if graph_frame is not None and graph_frame.size > 0:
        # Crear un frame negro del tamaño del video
        frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        # Obtener dimensiones del gráfico capturado
        graph_h, graph_w = graph_frame.shape[:2]
        
        # Calcular posición centrada para el gráfico
        # Mantener la relación de aspecto del gráfico
        scale = min(WIDTH / graph_w, HEIGHT / graph_h)
        new_w = int(graph_w * scale)
        new_h = int(graph_h * scale)
        
        # Redimensionar el gráfico manteniendo la relación de aspecto
        resized_graph = cv2.resize(graph_frame, (new_w, new_h))
        
        # Mejorar visibilidad de las líneas: aumentar brillo y contraste
        # Convertir a float para operaciones
        enhanced = resized_graph.astype(np.float32)
        
        # Aumentar brillo (sumar valor constante)
        enhanced = enhanced + 30  # Aumentar brillo
        
        # Aumentar contraste (multiplicar)
        enhanced = enhanced * 1.3  # Aumentar contraste
        
        # Asegurar que los valores estén en el rango [0, 255]
        enhanced = np.clip(enhanced, 0, 255)
        
        # Convertir de vuelta a uint8
        enhanced = enhanced.astype(np.uint8)
        
        # Calcular posición para centrar el gráfico en el frame negro
        y_offset = (HEIGHT - new_h) // 2
        x_offset = (WIDTH - new_w) // 2
        
        # Colocar el gráfico mejorado en el centro del frame negro
        frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = enhanced
        
        video.write(frame)
    else:
        print(f"Warning: Frame {i} es None o vacío, saltando...")

video.release()
driver.quit()

print("\n==============================")
print(" VIDEO GENERADO EXITOSAMENTE ")
print("==============================")
print(OUTPUT_VIDEO)
