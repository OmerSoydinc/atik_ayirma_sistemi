# -*- coding: utf-8 -*-
"""
Created on Sat Feb 17 18:40:53 2024

@author: omers
"""

from PyQt5 import uic

with open('AnasayfaUI.py','w', encoding="utf-8") as fout:
    uic.compileUi('kullanici_paneli.ui', fout)
    

with open('AdminUI.py','w', encoding="utf-8") as fout:
    uic.compileUi('admin_paneli.ui', fout)



with open('GirisUI.py','w', encoding="utf-8") as fout:
    uic.compileUi('giris.ui', fout)
    
    
    
    