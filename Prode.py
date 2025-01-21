from flask import Flask, jsonify
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# Crear la app Flask
app = Flask(__name__)

# URL a scrapeo
URL = 'https://www.flashscore.com/tennis/'

# Función para verificar si la página está completamente cargada
def test_download(driver):
    time.sleep(3)
    page1 = driver.page_source
    time.sleep(5)
    page2 = driver.page_source
    index = 0
    while page1 != page2:
        if index == 5:
            print('Very slow internet speed!')
            page1 = None
            break
        print('Page loading...')
        time.sleep(5)
        page1 = page2
        page2 = driver.page_source
        index += 1
    return page1

# Ruta de la API para obtener los partidos
@app.route("/partidos", methods=["GET"])
def obtener_partidos():
    # Opciones de Selenium
    OPTIONS = webdriver.ChromeOptions()
    OPTIONS.add_argument('user-agent=Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Mobile Safari/537.36')
    OPTIONS.add_argument('--disable-blink-features=AutomationControlled')
    OPTIONS.add_argument('--headless=new')

    # Inicializar Selenium WebDriver
    driver = webdriver.Chrome(options=OPTIONS)
    driver.get(url=URL)
    time.sleep(5)

    # Obtener el contenido HTML de la página
    body = driver.execute_script("return document.body")
    source = body.get_attribute('innerHTML')
    soup = BeautifulSoup(source, "html.parser")

    # Encontrar todos los elementos de partidos
    matches = soup.find_all('div', class_=['event__header', 'event__match'])
    partidos = []

    # Iterar sobre los partidos encontrados y generar datos en JSON
    for match in matches:
        first_player = match.find('div', class_='event__participant event__participant--home')
        second_player = match.find('div', class_='event__participant event__participant--away')

        if not first_player:
            first_player = match.find('div', class_='event__participant event__participant--home fontExtraBold')
        if not second_player:
            second_player = match.find('div', class_='event__participant event__participant--away fontExtraBold')

        first_player = first_player.text if first_player else "Desconocido"
        second_player = second_player.text if second_player else "Desconocido"

        date_match = driver.find_element(By.XPATH, '//*[@id="calendarMenu"]').text.split(' ')[0]
        instancia = match.find('div', class_='event__stage')
        
        winner = ""
        pbyp = []
        round_match = "Desconocido"
        tourney_name = "Torneo desconocido"
        start_time = ""
        score = "N/A"
        instancia_text = "Desconocido"
        
        if instancia:
            instancia_text = instancia.text.strip()
            if "finished" in instancia_text.lower():
                # Si el partido terminó, obtener el puntaje
                first_player_score = match.find('div', class_='event__score event__score--home').text
                second_player_score = match.find('div', class_='event__score event__score--away').text
                score = f"{first_player_score}-{second_player_score}"
                winner = "first_player" if match.find(class_='duelParticipant__home') else "second_player"
            else:
                # Partido en curso
                pbyp = [0, 1]
        else:
            # Si no hay instancia, obtener la hora de inicio
            hora_inicio = match.find('div', class_='event__time')
            start_time = hora_inicio.text.strip() if hora_inicio else "Desconocido"

        # Estructura del JSON para cada partido
        partidos.append({
            "event_date": date_match,
            "event_time": start_time,
            "event_first_player": first_player,
            "event_second_player": second_player,
            "event_final_result": score,
            "event_status": instancia_text
        })

    driver.quit()
    return jsonify({"partidos": partidos})

# Iniciar el servidor Flask
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
