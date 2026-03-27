import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Bairros de interesse em Caicó
BAIRROS = ["Penedo", "Castelo Branco", "Nova Descoberta", "Maynard"]

def enviar_telegram(mensagem):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Erro ao enviar Telegram: {e}")

def buscar():
    print("Iniciando busca em Caicó...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    urls = [
        "https://erikacorretora.com/todos-os-imoveis/",
        "https://rn.olx.com.br/rio-grande-do-norte/serido/caico/imoveis/aluguel"
    ]

    encontrados = []
    
    for url in urls:
        try:
            print(f"Acessando: {url}")
            driver.get(url)
            time.sleep(5)
            # Scroll para carregar conteúdo dinâmico
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Busca todos os links da página
            links = soup.find_all("a", href=True)
            
            for l in links:
                texto = l.get_text().lower()
                href = l["href"]
                # Verifica se o texto do link contém algum dos bairros
                if any(b.lower() in texto for b in BAIRROS):
                    if href not in encontrados and "http" in href:
                        encontrados.append(href)
                        print(f"Achado: {href}")
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")
            continue
    
    driver.quit()
    
    if encontrados:
        # Pega os 5 primeiros para não lotar o Telegram
        lista_links = "\n".join(encontrados[:5])
        msg = f"🏠 *Novos imóveis em Caicó encontrados!*\n\n{lista_links}"
        enviar_telegram(msg)
    else:
        print("Nenhum imóvel novo nos bairros selecionados hoje.")

if __name__ == "__main__":
    buscar()
