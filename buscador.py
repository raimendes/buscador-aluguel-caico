import os
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Seus bairros de interesse em Caicó
BAIRROS = ["Penedo", "Castelo Branco", "Nova Descoberta", "Maynard"]

def enviar_telegram(mensagem):
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})
            print("Mensagem enviada para o Telegram!")
        except Exception as e:
            print(f"Erro ao enviar para o Telegram: {e}")

def buscar():
    print("Iniciando busca automatizada em Caicó...")
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    urls = [
        "https://erikacorretora.com/todos-os-imoveis/",
        "https://rn.olx.com.br/rio-grande-do-norte/serido/caico/imoveis/aluguel"
    ]

    encontrados = []
    
    for url in urls:
        try:
            print(f"Verificando site: {url}")
            driver.get(url)
            time.sleep(5)
            # Scroll para carregar imóveis escondidos
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = soup.find_all("a", href=True)
            
            for l in links:
                texto = l.get_text().lower()
                href = l["href"]
                # Filtra pelos bairros escolhidos
                if any(b.lower() in texto for b in BAIRROS):
                    if href not in encontrados and "http" in href:
                        encontrados.append(href)
                        print(f"Imóvel encontrado no bairro: {texto.strip()[:30]}")
        except Exception as e:
            print(f"Erro ao processar {url}: {e}")
            continue
    
    driver.quit()

    if encontrados:
        msg = "🏠 *Novos imóveis em Caicó encontrados!*\n\n" + "\n".join(encontrados[:5])
        enviar_telegram(msg)
    else:
        print("Nenhum imóvel novo nos bairros Penedo, Maynard, Castelo Branco ou Nova Descoberta.")

if __name__ == "__main__":
    buscar()
