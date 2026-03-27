import os
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES ---
BAIRROS = ["Penedo", "Castelo Branco", "Nova Descoberta", "Maynard"]
ARQUIVO_VISTOS = "vistos.json"

# Puxa os dados das "Secrets" do GitHub (Segurança)
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    if TOKEN and CHAT_ID:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        data = {"chat_id": CHAT_ID, "text": mensagem, "parse_mode": "Markdown"}
        requests.post(url, data=data)

def carregar_vistos():
    if os.path.exists(ARQUIVO_VISTOS):
        with open(ARQUIVO_VISTOS, "r") as f:
            return json.load(f)
    return []

def salvar_vistos(vistos):
    with open(ARQUIVO_VISTOS, "w") as f:
        json.dump(vistos, f)

def configurar_browser():
    options = Options()
    options.add_argument("--headless") # Essencial para o GitHub Actions
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

def buscar_imoveis():
    driver = configurar_browser()
    vistos = carregar_vistos()
    novos_links = []
    
    # Lista de alvos em Caicó
    urls = [
        "https://erikacorretora.com/todos-os-imoveis/",
        "https://rn.olx.com.br/rio-grande-do-norte/serido/caico/imoveis/aluguel"
    ]

    for url in urls:
        try:
            print(f"Verificando: {url}")
            driver.get(url)
            time.sleep(5)
            
            # Rolar a página 3 vezes para carregar o 'Infinite Scroll'
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            # Busca todos os links que possam ser de imóveis
            links = soup.find_