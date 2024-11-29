# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 18:44:08 2024

@author: omers
"""
import math
import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import *
from GirisUI import *
from AnasayfaUI import *
from AdminUI import *
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
import numpy as np
import cv2
import sqlite3

from PIL import Image, ImageTk
from ultralytics import YOLO

classNames = ["person", "bicycle", "car", "motorbike", "aeroplane", "bus", "train", "truck", "boat",
              "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
              "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack", "umbrella",
              "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball", "kite", "baseball bat",
              "baseball glove", "skateboard", "surfboard", "tennis racket", "bottle", "wine glass", "cup",
              "fork", "knife", "spoon", "bowl", "banana", "apple", "sandwich", "orange", "broccoli",
              "carrot", "hot dog", "pizza", "donut", "cake", "chair", "sofa", "pottedplant", "bed",
              "diningtable", "toilet", "tvmonitor", "laptop", "mouse", "remote", "keyboard", "cell phone",
              "microwave", "oven", "toaster", "sink", "refrigerator", "book", "clock", "vase", "scissors",
              "teddy bear", "hair drier", "toothbrush"
              ]

uygulama = QApplication(sys.argv)

ekran = QMainWindow()

ui = Ui_GirisEkrani()
ui.setupUi(ekran)

ekran.show()

# Veritabanı bağlantısı
global curs
global conn

conn = sqlite3.connect('atik_yonetim_sistemi.db')
curs = conn.cursor()

def yeniKayit():
    _kayit_isim = ui.kayit_isim.text()
    _kayit_soyisim = ui.kayit_soyisim.text()
    _kayit_tc = ui.kayit_tc.text()
    _kayit_telefon = ui.kayit_telefon.text()
    _kayit_sifre = ui.kayit_sifre.text()

    sorgu = "INSERT INTO Kullanicilar (adi, soyadi, tc, telefon, sifre) VALUES (?, ?, ?, ?, ?)"
    veriler = (_kayit_isim, _kayit_soyisim, _kayit_tc, _kayit_telefon, _kayit_sifre)

    curs.execute("SELECT * FROM Kullanicilar WHERE tc=? OR telefon=?", (_kayit_tc, _kayit_telefon))
    kayitlar = curs.fetchall()

    try:
        if kayitlar:
            QMessageBox.warning(ekran, "Hata", "Girilen TC veya telefon numarası zaten mevcut. Lütfen başka bir numara girin.")
        else:
            curs.execute(sorgu, veriler)
            conn.commit()
            QMessageBox.information(ekran, "Başarılı", "Kayıt başarıyla gerçekleştirildi.")
    except Exception as e:
        QMessageBox.warning(ekran, "Hata", f"Kayıt sırasında bir hata oluştu: {str(e)}")

def kullaniciGiris():
    _giris_tc = ui.giris_tc.text()
    _giris_sifre = ui.giris_sifre.text()

    curs.execute("SELECT * FROM Kullanicilar WHERE tc=? AND sifre=?", (_giris_tc, _giris_sifre))
    kayitlar = curs.fetchall()

    if kayitlar:
        ui2 = Ui_Kullanici_paneli()
        ui2.setupUi(ekran)
        ekran.show()
        QMessageBox.information(ekran, "Başarılı", "Giriş başarıyla gerçekleştirildi.")
        ui2.basla.clicked.connect(tespit_ekrani)
        
        
    else:
        QMessageBox.warning(ekran, "Hata", "Giriş bilgileri geçersiz.")


def tespit_ekrani():
    # Kameradan görüntü al
    cap = cv2.VideoCapture(0)
    
    #model = YOLO("resnet50_model.pt")
    model = "resnet50_model.pt"
    
    while True:
        ret, frame = cap.read()   # frame kameradan alınan görüntü
        # OpenCV görüntüyü renkli olarak alır, PyQt ile uyumlu hale getir
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        result = model(frame)
        
        for r in result:
            boxes = r.boxes
            for box in boxes:
                x1,y1,x2,y2 = box.xyxy[0]
                x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
                w , h = x2-x1 , y2-y1  
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                tespit_degeri = math.ceil((box.conf[0]*100))/100
                nesne_sinifi=  int(box.cls[0])
                print("tespit_degeri",tespit_degeri)
                print("nesne_sinifi",nesne_sinifi)
        
        height, width, channel = frame.shape
        step = channel * width
        
        # OpenCV görüntüyü QImage'e dönüştür
        qImg = QImage(frame.data, width, height, step, QImage.Format_RGB888)
        
        # QLabel'da görüntüyü göster
        ui2 = Ui_Kullanici_paneli()
        ui2.setupUi(ekran)  # Kullanıcı paneli ekranını yeniden yükle
        ui2.frame_degiskeni.setPixmap(QPixmap.fromImage(qImg))
        ekran.show()
        
        # Eğer kapatılmak istenirse döngüyü sonlandır
        if cv2.waitKey(1) & 0xFF == ord('q'):  # tespit_btn ye tekrar basılınca kapanır
            break
        
    cap.release()
    cv2.destroyAllWindows()




def AdminGiris():
    _giris_tc = ui.admin_tc.text()
    _giris_sifre = ui.admin_sifre.text()
    

    if (_giris_tc == "24019938994" and _giris_sifre == "12345"):
        ui2 = Ui_Admin_panel()
        ui2.setupUi(ekran)
        ekran.show()
        QMessageBox.information(ekran, "Başarılı", "Giriş başarıyla gerçekleştirildi.")
        curs.execute("select * from Kullanicilar")
        rows = curs.fetchall()
        
        
        if not rows:
            QMessageBox.warning(ekran, "Hata", "Veritabanında kayıtlı kullanıcı bulunamadı.")
        else:
            # tableWidget'ın satır ve sütun sayısını ayarla
            ui2.tablo.setRowCount(len(rows))
            if len(rows) > 0:
                ui2.tablo.setColumnCount(len(rows[0]))

            # Verileri tablo'a ekle
            for i, row in enumerate(rows):
                for j, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    ui2.tablo.setItem(i, j, item)
        
        for row in rows:
            print(row)
            

        

        #♣tableWidget
        
        
        
    else:
        QMessageBox.warning(ekran, "Hata", "Giriş bilgileri geçersiz.")

ui.kayit_ol_btn.clicked.connect(yeniKayit)
ui.giris_btn.clicked.connect(kullaniciGiris)
ui.admin_btn.clicked.connect(AdminGiris)

sys.exit(uygulama.exec_())
