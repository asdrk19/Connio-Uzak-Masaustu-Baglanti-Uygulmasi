import socket
import threading

def bridge(sock1, sock2):
    """İki soket arasında çift yönlü veri köprüsü kurar"""
    def pipe(src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data: break
                dst.sendall(data)
        except: pass
        finally:
            src.close()
            dst.close()

    threading.Thread(target=pipe, args=(sock1, sock2), daemon=True).start()
    threading.Thread(target=pipe, args=(sock2, sock1), daemon=True).start()

# 1. Telefonu bekleyen kapı (Port: 8887)
phone_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
phone_server.bind(('0.0.0.0', 8887))
phone_server.listen(1)

# 2. Evdeki bilgisayarı bekleyen kapı (Port: 9000)
pc_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pc_server.bind(('0.0.0.0', 9000))
pc_server.listen(1)

print("🚀 Connio Özel Tünel Sunucusu Aktif!")

while True:
    print("[*] Telefonun bağlanması bekleniyor (Port 8887)...")
    phone_sock, phone_addr = phone_server.accept()
    print(f"[+] Telefon bağlandı: {phone_addr}! Şimdi evdeki PC aranıyor...")

    print("[*] PC'nin tünele gelmesi bekleniyor (Port 9000)...")
    pc_sock, pc_addr = pc_server.accept()
    print(f"[+] PC bağlandı: {pc_addr}! Köprü kuruldu, veri akışı başlıyor.")

    bridge(phone_sock, pc_sock)