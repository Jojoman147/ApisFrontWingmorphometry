import cv2
import numpy as np
from tkinter import filedialog
from tkinter import Tk
import matplotlib.pyplot as plt
import pandas as pd
import os

# Globálne premenné pre ukladanie bodov
body = []
# Funkcia pre výpočet plochy polygonu v mm²
def vypocet_plochy_polygonu(body_polygonu, skala):
    x = [bod[0] for bod in body_polygonu]
    y = [bod[1] for bod in body_polygonu]
    return 0.5 * np.abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))) * skala**2

# Funkcia pre výpočet bodu 45 bod na 0-7 radialny index k Diskodialnej odchylke 
def vypocet_bodu45(bod2, bod9, bod7):
    u = bod9 - bod2
    v = bod7 - bod2
    t = np.dot(u, v) / np.dot(u, u)
    bod45 = bod2 + t * u
    return bod45
# Funkcia pre výpočet bodu 55 k DO ako bod najbližši k bodu 5 
def vypocet_bodu55(bod5, bod45, bod7):
    u = bod7 - bod45
    v = bod5 - bod45
    t = np.dot(u, v) / np.dot(u, u)
    bod55 = bod45 + t * u
    return bod55
# Funkcia pre výpočet vzdialenosti DO
def vypocet_vzdialenosti_DO(bod5, bod55, skala):
    return np.linalg.norm(bod5 - bod55) * skala

# Funkcia pre výpočet bodu 40 vypočet aR bR
def vypocet_bodu40(bod2, bod5, bod9):
    u = bod9 - bod2
    v = bod5 - bod2
    t = np.dot(u, v) / np.dot(u, u)
    bod40 = bod2 + t * u
    return bod40
# Funkcia pre zaznačovanie bodov na obrázok
def onclick(event):
    x, y = event.xdata, event.ydata
    if event.button == 1 and event.dblclick:
        plt.plot(x, y, 'go')
        body.append((x, y))
        plt.text(x, y, str(len(body)-1), color='red')  # Označenie bodu číslicou
        plt.draw()

# Funkcia pre výpočet uhla medzi troma bodmi
def vypocet_uhla(bod1, bod2, bod3):
    a = np.array(bod1)
    b = np.array(bod2)
    c = np.array(bod3)

    ba = a - b
    bc = c - b

    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(cosine_angle)

    return np.degrees(angle)

# Funkcia pre výpočet vzdialenosti medzi dvoma bodmi
def vypocet_vzdialenosti(bod1, bod2, skala):
    return np.sqrt((bod2[0] - bod1[0])**2 + (bod2[1] - bod1[1])**2) * skala

def zobraz_obrazok():
    # Vytvorenie skrytého hlavného okna
    Tk().withdraw()

    # Otvorenie dialógového okna pre výber súborov
    cesta_k_obrazku = filedialog.askopenfilename()

    # Načítanie obrázka
    obrazok = cv2.imread(cesta_k_obrazku)
    obrazok = cv2.cvtColor(obrazok, cv2.COLOR_BGR2RGB)

    fig, ax = plt.subplots()
    ax.imshow(obrazok)

    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()

    # Výpočet uhlov a vzdialeností
    data = []
    if len(body) >= 2:
        # Výpočet škály na základe vzdialenosti medzi prvými dvoma bodmi
        skala = 1 / vypocet_vzdialenosti(body[0], body[1], 1)

        vzdialenost = vypocet_vzdialenosti(body[0], body[1], skala)
        data.append(['Kalibrácia', f'{vzdialenost} mm'])
         # Výpočet aR a bR
        bod2 = np.array(body[2])
        bod5 = np.array(body[5])
        bod9 = np.array(body[9])
        bod40 = vypocet_bodu40(bod2, bod5, bod9)
        aR = vypocet_vzdialenosti(bod2, bod40, skala)
        data.append(['Dĺžka aR', f'{aR}'])

        bR = vypocet_vzdialenosti(bod9, bod40, skala)
        data.append(['Dĺžka bR', f'{bR}'])
         # Výpočet DO
        bod2 = np.array(body[2])
        bod5 = np.array(body[5])
        bod9 = np.array(body[9])
        bod7 = np.array(body[7])
        bod45 = vypocet_bodu45(bod2, bod9, bod7)
        bod55 = vypocet_bodu55(bod5, bod45, bod7)
        DO = vypocet_vzdialenosti_DO(bod5, bod55, skala)
        data.append(['Vzdialenosť DO', f'{DO}'])
        

    if len(body) >= 3:
       
        # Výpočet vzdialenosti
        vzdialenostA = vypocet_vzdialenosti(body[4], body[6], skala)
        data.append(['Dlzka A', f'{vzdialenostA}'])
        vzdialenostB = vypocet_vzdialenosti(body[3], body[4], skala)
        data.append(['Dlzka B', f'{vzdialenostB}'])
        vzdialenostC = vypocet_vzdialenosti(body[5], body[6], skala)
        data.append(['Dlzka C', f'{vzdialenostC}'])
        vzdialenostD = vypocet_vzdialenosti(body[13], body[17], skala)
        data.append(['Dlzka D', f'{vzdialenostD}'])
        vnutornadlzka = vypocet_vzdialenosti(body[3], body[16], skala)
        data.append(['vnutornadlzka', f'{vnutornadlzka}'])
        vnutornasirka = vypocet_vzdialenosti(body[9], body[15], skala)
        data.append(['vnutornasirka', f'{vnutornasirka}'])
        radialfield = vypocet_vzdialenosti(body[2], body[9], skala)
        data.append(['radialfield', f'{radialfield}'])
        predlaketnyC = vypocet_vzdialenosti(body[6], body[11], skala)
        data.append(['predlaketnyC', f'{predlaketnyC}'])
        predlaketnyM = vypocet_vzdialenosti(body[10], body[12], skala)
        data.append(['predlaketnyM', f'{predlaketnyM}'])
        cinkovyC = vypocet_vzdialenosti(body[3], body[6], skala)
        data.append(['cinkovyC', f'{cinkovyC}'])
        cinkovyM = vypocet_vzdialenosti(body[7], body[8], skala)
        data.append(['cinkovyM', f'{cinkovyM}'])



    if len(body) >= 4:
        uhol_A1 = vypocet_uhla(body[4], body[3], body[6])
        data.append(['Uhol A1', f'{uhol_A1}'])
        uhol_A4 = vypocet_uhla(body[6], body[3], body[7])
        data.append(['Uhol A4', f'{uhol_A4}'])
        uhol_B3 = vypocet_uhla(body[3], body[6], body[5])
        data.append(['Uhol B3', f'{uhol_B3}'])
        uhol_B4 = vypocet_uhla(body[3], body[6], body[7])
        data.append(['Uhol B4', f'{uhol_B4}'])
        uhol_D7 = vypocet_uhla(body[6], body[5], body[15])
        data.append(['Uhol D7', f'{uhol_D7}'])
        uhol_E9 = vypocet_uhla(body[8], body[7], body[12])
        data.append(['Uhol E9', f'{uhol_E9}'])
        uhol_G7 = vypocet_uhla(body[5], body[15], body[6])
        data.append(['Uhol G7', f'{uhol_G7}'])
        uhol_G18 = vypocet_uhla(body[14], body[15], body[16])
        data.append(['Uhol G18', f'{uhol_G18}'])
        uhol_H12 = vypocet_uhla(body[13], body[12], body[14])
        data.append(['Uhol H12', f'{uhol_H12}'])
        uhol_J10 = vypocet_uhla(body[8], body[11], body[12])
        data.append(['Uhol J10', f'{uhol_J10}'])
        uhol_J16 = vypocet_uhla(body[10], body[11], body[20])
        data.append(['Uhol J16', f'{uhol_J16}'])
        uhol_K19 = vypocet_uhla(body[14], body[13], body[16])
        data.append(['Uhol K19', f'{uhol_K19}'])
        uhol_L13 = vypocet_uhla(body[7], body[9], body[8])
        data.append(['Uhol L13', f'{uhol_L13}'])
        uhol_M17 = vypocet_uhla(body[9], body[10], body[20])
        data.append(['Uhol M17', f'{uhol_M17}'])
        uhol_N23 = vypocet_uhla(body[11], body[20], body[19])
        data.append(['Uhol N23', f'{uhol_N23}'])
        uhol_O26 = vypocet_uhla(body[17], body[16], body[18])
        data.append(['Uhol O26', f'{uhol_O26}'])
        uhol_Q21 = vypocet_uhla(body[13], body[18], body[19])
        data.append(['Uhol Q21', f'{uhol_Q21}'])

        body_polygonu = [body[i] for i in [3,7,9,20,19,18,17,16,15,14,5,4]]
        plocha = vypocet_plochy_polygonu(body_polygonu,skala)
        data.append(['Area 6', f'{plocha}'])


    # Vytvorenie DataFrame a export do Excelu
    df = pd.DataFrame(data, columns=['Parameter', 'Hodnota'])
    
    # Kontrola, či súbor už existuje, a prípadne pridanie čísla na koniec názvu súboru
    i = 1
    while os.path.exists(f'vysledky{i}.xlsx'):
        i += 1

    df.to_excel(f'vysledky{i}.xlsx', index=False)
# Zavolanie funkcie
zobraz_obrazok()

