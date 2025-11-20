## script para adecuar el grafico para convertirlo en mp4
## no lo convierte, lo adecua
## Usa Selenium para extraer los datos de Plotly desde el HTML renderizado

import json
import time
import os
from pathlib import Path
import plotly.graph_objects as go
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Workaround para webdriver_manager encoding issue
os.environ['WDM_LOG_LEVEL'] = '0'
try:
    from webdriver_manager.chrome import ChromeDriverManager
except Exception:
    # Si falla, intentar usar el driver del sistema
    ChromeDriverManager = None

# Obtener la ruta absoluta del directorio actual
BASE_DIR = Path(__file__).parent.absolute()

# Ruta del HTML original
INPUT_HTML = str(BASE_DIR / "grafico.html")

# Ruta del HTML que vamos a generar INLINE
OUTPUT_HTML = str(BASE_DIR / "grafico_inline.html")


def extraer_data_y_layout_con_selenium(html_path: str):
    """
    Usa Selenium para cargar el HTML y extraer los datos de Plotly usando JavaScript.
    """
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1600,1200")
    
    if ChromeDriverManager:
        try:
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=options)
        except Exception:
            # Fallback: usar driver del sistema
            driver = webdriver.Chrome(options=options)
    else:
        driver = webdriver.Chrome(options=options)
    
    try:
        html_url = "file:///" + html_path.replace("\\", "/")
        driver.get(html_url)
        
        # Esperar a que Plotly cargue
        time.sleep(3)
        
        # Encontrar el div de Plotly
        plot_div = driver.find_element("xpath", "//div[contains(@class,'plotly-graph-div')]")
        plot_id = plot_div.get_attribute("id")
        
        # Extraer data y layout usando JavaScript
        data_layout_script = f"""
        var gd = document.getElementById("{plot_id}");
        if (gd && gd.data && gd.layout) {{
            return JSON.stringify({{
                data: gd.data,
                layout: gd.layout
            }});
        }}
        return null;
        """
        
        result = driver.execute_script(data_layout_script)
        
        if not result:
            raise ValueError("No se pudieron extraer los datos de Plotly del HTML.")
        
        plotly_data = json.loads(result)
        return plotly_data['data'], plotly_data['layout']
        
    finally:
        driver.quit()


def main():
    print("Extrayendo datos de Plotly desde el HTML...")
    data, layout = extraer_data_y_layout_con_selenium(INPUT_HTML)
    
    print("Reconstruyendo figura Plotly...")
    # Reconstruir figura Plotly
    fig = go.Figure(data=data, layout=layout)
    
    print("Generando HTML con Plotly inline...")
    # Exportar con Plotly JS embebido (INLINE)
    fig.write_html(OUTPUT_HTML, include_plotlyjs="inline", full_html=True)
    
    print("\nHTML INLINE generado correctamente en:")
    print(OUTPUT_HTML)


if __name__ == "__main__":
    main()


