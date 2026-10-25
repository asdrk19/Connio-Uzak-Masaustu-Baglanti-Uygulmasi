from PyQt6 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(736, 475)
        MainWindow.setMinimumSize(QtCore.QSize(736, 475))
        MainWindow.setMaximumSize(QtCore.QSize(736, 475))

        # Ana pencere arka planı görseldeki gibi açık gri/modern bir tona çekildi
        MainWindow.setStyleSheet("background-color: 'white';")

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # --- LOGO ALANI ---
        self.label_logo = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_logo.setGeometry(QtCore.QRect(268, 20, 200, 130))
        self.label_logo.setStyleSheet("""
                    background-image: url('connio_logo_.png');
                    background-repeat: no-repeat;
                    background-position: center;
                    background-color: transparent;
                """)
        self.label_logo.setObjectName("label_logo")

        # --- ETİKETLER VE BUTONLAR ---

        self.label_hosgeldiniz = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_hosgeldiniz.setGeometry(QtCore.QRect(268, 170, 200, 31))
        self.label_hosgeldiniz.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.push_baslat = QtWidgets.QPushButton(parent=self.centralwidget)
        self.push_baslat.setGeometry(QtCore.QRect(234, 220, 131, 32))

        self.push_durdur = QtWidgets.QPushButton(parent=self.centralwidget)
        self.push_durdur.setGeometry(QtCore.QRect(371, 220, 131, 32))

        self.label_kod = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_kod.setGeometry(QtCore.QRect(234, 270, 268, 71))
        self.label_kod.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.label_durum = QtWidgets.QLabel(parent=self.centralwidget)
        self.label_durum.setGeometry(QtCore.QRect(234, 360, 268, 71))
        self.label_durum.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        MainWindow.setCentralWidget(self.centralwidget)
        self.retranslateUi(MainWindow)

        # --- YENİ MODERN STİL TANIMLAMALARI (Görsele Uygun) ---

        # Bilgi ve Başlık Kutuları İçin Stil (Açık gri arka plan, ince soft border ve oval köşeler)
        box_style = """
            background-color: #e8eaed; 
            color: #202124; 
            border: 1px solid #bdc1c6; 
            border-radius: 10px;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        """
        self.label_hosgeldiniz.setStyleSheet(box_style)
        self.label_kod.setStyleSheet(box_style + "font-size: 14px; font-weight: 500;")
        self.label_durum.setStyleSheet(box_style + "font-size: 13px;")

        # Başlat Butonu Stili (Görseldeki canlı yeşil, beyaz yazı ve oval köşeler)
        self.push_baslat.setStyleSheet("""
            QPushButton {
                background-color: #0ea651; 
                color: white; 
                border: none; 
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0c8f44;
            }
            QPushButton:disabled {
                background-color: #bdc1c6;
                color: #757575;
            }
        """)

        # Sonlandır Butonu Stili (Görseldeki sade beyaz/gri buton tasarımı)
        self.push_durdur.setStyleSheet("""
            QPushButton {
                background-color: #ffffff; 
                color: #3c4043; 
                border: 1px solid #bdc1c6; 
                border-radius: 8px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #f8f9fa;
            }
            QPushButton:disabled {
                background-color: #f1f3f4;
                color: #c4c7c5;
                border: 1px solid #e3e3e3;
            }
        """)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Connio"))
        self.label_hosgeldiniz.setText(_translate("MainWindow", "HOŞ GELDİNİZ"))
        self.push_baslat.setText(_translate("MainWindow", "Bağlantıyı Başlat"))
        self.push_durdur.setText(_translate("MainWindow", "Bağlantıyı Sonlandır"))
        self.label_kod.setText(_translate("MainWindow", "KODUNUZ: ---"))
        self.label_durum.setText(_translate("MainWindow", "Bağlantı Durumu: \n Bekleniyor"))


