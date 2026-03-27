import os
import time
import json
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# --- CONFIGURAÇÕES DO PROFESSOR MENDES ---
BAIRROS = ["Penedo", "Castelo Branco", "Nova Descoberta", "Maynard"]
ARQUIVO_VISTOS = "vistos.json"

def carregar_vistos():
    """Lê o arquivo JSON para saber o que já foi enviado anteriormente"""
    if os.path.exists(ARQUIVO_VISTOS):
        try:
            with open(ARQUIVO_VISTOS, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def salvar_vistos(vistos):
    """Salva a lista atualizada de links no JSON (Persistência)"""
    with open(ARQUIVO_VISTOS, "w") as f:
        json.dump(vistos, f, indent=4)

def enviar_telegram(mensagem):
    """Envia a notificação para o seu celular via API do Telegram"""
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        try:
            requests.post(url, data={"chat_id": chat_id, "text": mensagem, "parse_mode": "Markdown"})
        except Exception as e:
            print(f"Erro ao conectar com Telegram: {e}")

def buscar():
    print("🚀 Iniciando busca de aluguéis em Caicó...")
    vistos_antes = carregar_vistos()
    
    # Configuração do Navegador (Modo Headless para o Servidor)
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

    encontrados_agora = []

    for url in urls:
        try:
            print(f"🔎 Analisando: {url}")
            driver.get(url)
            time.sleep(5) # Espera o site carregar
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            soup = BeautifulSoup(driver.page_source, "html.parser")
            links = soup.find_all("a", href=True)
            
            for l in links:
                texto = l.get_text().lower()
                href = l["href"]
                
                # Lógica de Filtro: Bairro E Inédito
                if any(b.lower() in texto for b in BAIRROS):
                    if href not in vistos_antes and href not in encontrados_agora:
                        if "http" in href: # Garante que é um link válido
                            encontrados_agora.append(href)
        except Exception as e:
            print(f"⚠️ Erro ao acessar {url}: {e}")
            continue
    
    driver.quit()

    # --- RESULTADO DA MISSÃO ---
    if encontrados_agora:
        # Salva os novos no "banco de dados"
        nova_lista_vistos = vistos_antes + encontrados_agora
        salvar_vistos(nova_lista_vistos)
        
        # Envia os links novos para o Mendes
        links_texto = "\n".join(encontrados_agora[:5])
        msg_sucesso = f"🏠 *Novos imóveis encontrados em Caicó!*\n\n{links_texto}"
        enviar_telegram(msg_sucesso)
        print(f"✅ {len(encontrados_agora)} novos links enviados!")
    else:
        # Se não tiver nada novo, avisa que a busca foi feita com sucesso
        bairros_txt = ", ".join(BAIRROS)
        msg_vazia = f"🔍 *Busca Diária Concluída*\n\nNenhum imóvel novo foi postado hoje nos bairros: _{bairros_txt}_."
        enviar_telegram(msg_vazia)
        print("📭 Nada de novo, aviso de 'vazio' enviado.")

if __name__ == "__main__":
    buscar()
