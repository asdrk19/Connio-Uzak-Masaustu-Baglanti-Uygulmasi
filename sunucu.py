import sys
import asyncio
import websockets
import pyautogui
import base64
import socket
import firebase_admin
import random
import threading  
import time       
from firebase_admin import credentials, db
from io import BytesIO
from PIL import ImageGrab, ImageDraw
from PyQt6 import QtCore, QtWidgets

try:
    from first import Ui_MainWindow
except ImportError:
    print("Hata: 'first.py' dosyası bulunamadı. Lütfen tasarım dosyanızın adının doğru olduğundan emin olun.")
    sys.exit()


class ServerWorker(QtCore.QThread):
    status_signal = QtCore.pyqtSignal(str)
    code_signal = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._is_running = True
        self.loop = None
        self.server = None
        self.pico_server = None
        self.WIDTH, self.HEIGHT = pyautogui.size()
        
        # Cenuta VDS IP Adresi
        self.vps_ip = "89.252.153.77" 
        
        # Ağ geçidine bağlı olan Pico W cihazlarını tutan liste
        self.pico_websockets = set()

    def stop(self):
        self._is_running = False
        if self.loop:
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.wait() 

    def run(self):
        self._is_running = True

        try:
            # Firebase Başlatma
            if not firebase_admin._apps:
                cred = credentials.Certificate("anahtar.json")
                firebase_admin.initialize_app(cred, {
                    'databaseURL': 'https://ip-port-firebase-default-rtdb.europe-west1.firebasedatabase.app'
                })

            yeni_kod = str(random.randint(100000, 999999))
            self.code_signal.emit(yeni_kod)

            db.reference('baglanti_bilgisi').set({
                'ip': self.vps_ip,
                'port': "8887",
                'kod': yeni_kod
            })

            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

            # 1. DIŞ DÜNYA (TELEFON) İÇİN TÜNEL PORTU (8887)
            self.server = self.loop.run_until_complete(
                websockets.serve(self.handle_client, "0.0.0.0", 8887)
            )
            
            # 2. İÇ AĞ (PICO W) İÇİN İZOLE EDİLMİŞ IOT PORTU (8001)
            self.pico_server = self.loop.run_until_complete(
                websockets.serve(self.handle_pico, "0.0.0.0", 8001, ping_interval=None)
            )

            self.status_signal.emit("Sunucu Aktif -\n Tünel Kuruluyor...")

            threading.Thread(target=self.tunnel_loop, daemon=True).start()

            self.loop.run_forever()

            self.server.close()
            self.pico_server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

        except Exception as e:
            if "already in use" in str(e) or "10048" in str(e):
                self.status_signal.emit("HATA: Port 8887 veya 8001 meşgul!")
            else:
                self.status_signal.emit(f"Hata oluştu: {str(e)}")

    def tunnel_loop(self):
        """Yerel WebSocket ile Cenuta VDS arasında köprü kuran tünel döngüsü"""
        while self._is_running:
            try:
                print(f"\n[TÜNEL] Cenuta VDS ({self.vps_ip}:9000) portuna bağlanılıyor...")
                vps_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                vps_sock.connect((self.vps_ip, 9000))
                print("[TÜNEL] Cenuta VDS'e başarıyla bağlanıldı. Telefondan istek bekleniyor...")
                
                first_data = vps_sock.recv(4096)
                if not first_data:
                    vps_sock.close()
                    continue
                
                print(f"[TÜNEL] Telefondan {len(first_data)} byte veri geldi! Yerel WebSocket'e aktarılıyor...")
                local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                local_sock.connect(('127.0.0.1', 8887))
                
                local_sock.sendall(first_data)
                self.status_signal.emit("Tünel Aktif -\n Bağlantı Kuruldu!")
                
                def forward(src, dst):
                    try:
                        while self._is_running:
                            d = src.recv(4096)
                            if not d: break
                            dst.sendall(d)
                    except: pass
                    finally:
                        try: src.close()
                        except: pass
                        try: dst.close()
                        except: pass
                
                t1 = threading.Thread(target=forward, args=(vps_sock, local_sock), daemon=True)
                t2 = threading.Thread(target=forward, args=(local_sock, vps_sock), daemon=True)
                t1.start()
                t2.start()
                
                while self._is_running and t1.is_alive() and t2.is_alive():
                    time.sleep(0.2)
                print("[TÜNEL] Canlı oturum sona erdi. Yeni bağlantı bekleniyor...")
                    
            except Exception as e:
                print(f"[TÜNEL GİRİŞ HATASI] Cenuta'ya bağlanılamadı. VDS kapalı olabilir! Hata: {e}")
                time.sleep(2)

    async def handle_pico(self, websocket):
        """Yerel ağdan gelen Raspberry Pi Pico W bağlantılarını yönetir"""
        print("\n[IoT] 🟢 Raspberry Pi Pico W Ağ Geçidine Bağlandı!")
        self.pico_websockets.add(websocket)
        try:
            async for message in websocket:
                pass # Sensör verisi gelirse burada işlenebilir
        except:
            pass
        finally:
            print("\n[IoT] 🔴 Raspberry Pi Pico W Bağlantısı Koptu!")
            self.pico_websockets.discard(websocket)

    async def handle_client(self, websocket):
        """Telefondan (Tünel üzerinden) gelen uzak masaüstü ve IoT komutlarını yönetir"""
        print("\n[UYGULAMA] 🔥 Telefon bağlantıyı BAŞARIYLA tamamladı!")
        self.status_signal.emit("Bağlantı Kuruldu!")
        stream_task = asyncio.create_task(self.stream_screen(websocket))

        try:
            async for message in websocket:
                if message == "double_click": pyautogui.doubleClick()
                elif message == "right_click": pyautogui.rightClick()
                elif message.startswith("write_text:"):
                    pyautogui.write(message.split("write_text:", 1)[1])
                elif message == "open_cmd":
                    pyautogui.hotkey('win', 'r')
                    time.sleep(0.2)
                    pyautogui.write('cmd')
                    pyautogui.press('enter')
                elif message == "open_taskmgr": pyautogui.hotkey('ctrl', 'shift', 'esc')
                elif message == "show_desktop": pyautogui.hotkey('win', 'd')
                elif message == "press_enter": pyautogui.press('enter')
                elif message == "press_esc": pyautogui.press('esc')
                elif message == "alt_tab": pyautogui.hotkey('ctrl', 'alt', 'tab')
                
                # --- IoT GÜNEŞ PANELİ TETİKLEYİCİLERİ ---
                elif message == "motor_ac":
                    print("[IoT] ☀️ Güneş Paneli Motoru ÇALIŞTIRILDI!")
                    for pico_ws in list(self.pico_websockets):
                        asyncio.create_task(pico_ws.send("ON"))
                    
                elif message == "motor_kapat":
                    print("[IoT] ☀️ Güneş Paneli Motoru KAPATILDI!")
                    for pico_ws in list(self.pico_websockets):
                        asyncio.create_task(pico_ws.send("OFF"))
                # ----------------------------------------

                elif ":" in message:
                    try:
                        action, coords = message.split(":", 1)
                        tx = float(coords.split(",")[0]) * self.WIDTH
                        ty = float(coords.split(",")[1]) * self.HEIGHT
                        if action == "mouse_down": pyautogui.mouseDown(tx, ty)
                        elif action == "mouse_move": pyautogui.moveTo(tx, ty)
                        elif action == "mouse_up": pyautogui.mouseUp(tx, ty)
                    except: pass
                else:
                    try:
                        tx = float(message.split(",")[0]) * self.WIDTH
                        ty = float(message.split(",")[1]) * self.HEIGHT
                        pyautogui.click(tx, ty)
                    except: pass
        except websockets.exceptions.ConnectionClosed:
            print("[UYGULAMA] ❌ Telefon bağlantıyı kapattı.")
            self.status_signal.emit("Bağlantı Kesildi.")
        finally:
            stream_task.cancel()

    async def stream_screen(self, websocket):
        """Ekran görüntüsünü optimize ederek (Hız Modu) telefona basar"""
        print("[YAYIN] 📽 Canlı ekran yayını döngüsü başlatıldı (HIZ MODU)!")
        while self._is_running:
            try:
                img = ImageGrab.grab()
                
                # HIZ OPTİMİZASYONU: Çözünürlüğü %50 küçült
                img = img.resize((int(img.width * 0.5), int(img.height * 0.5)))
                
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                try:
                    cursor_x, cursor_y = pyautogui.position()
                    # Resim küçüldüğü için imleç koordinatları da %50 oranlanır
                    c_x, c_y = int(cursor_x * 0.5), int(cursor_y * 0.5)
                    ImageDraw.Draw(img).ellipse([c_x - 4, c_y - 4, c_x + 4, c_y + 4], fill=(255, 51, 51), outline=(255, 255, 255))
                except: pass

                buffer = BytesIO()
                
                # KALİTE OPTİMİZASYONU: JPEG Kalitesini 40'a çekerek veriyi hafiflet
                img.save(buffer, format="JPEG", quality=40)
                
                await websocket.send(base64.b64encode(buffer.getvalue()).decode())
                
                # Ağı darboğazdan kurtarmak için FPS ayarı
                await asyncio.sleep(0.08)
            except Exception as e:
                print(f"[YAYIN HATASI] Görüntü gönderilemedi: {e}")
                break

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.worker = None
        self.ui.push_baslat.clicked.connect(self.start_conn)
        self.ui.push_durdur.clicked.connect(self.stop_conn)
        self.ui.push_durdur.setEnabled(False)

    def start_conn(self):
        if self.worker and self.worker.isRunning(): return
        self.worker = ServerWorker()
        self.worker.status_signal.connect(self.update_status)
        self.worker.code_signal.connect(self.update_code)
        self.worker.start()
        self.ui.push_baslat.setEnabled(False)
        self.ui.push_durdur.setEnabled(True)
        self.ui.push_baslat.setText("Bağlantı Açık...")

    def stop_conn(self):
        if self.worker:
            self.worker.stop()
            self.ui.label_durum.setText("Durum: Bağlantı Sonlandırıldı.")
            self.ui.label_kod.setText("KODUNUZ: ---")
            self.ui.push_baslat.setEnabled(True)
            self.ui.push_durdur.setEnabled(False)
            self.ui.push_baslat.setText("Bağlantıyı Başlat")

    def update_status(self, text): self.ui.label_durum.setText(f"Durum: {text}")
    def update_code(self, code): self.ui.label_kod.setText(f"KODUNUZ:\n{code}")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())