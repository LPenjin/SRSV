import random
import random as rand
import time
import threading
import sys
import math

global end
end = False
global stanje
global trenutak_zadnje_promjene_stanja
global zadnji_odgovor
global trenutak_zadnjeg_odgovora
global start
global zadatak_u_obradi
zadatak_u_obradi = -1
global posao_u_obradi
posao_u_obradi = 0
global perioda
perioda = 0
global bez_prekoracenja
bez_prekoracenja = 0
global prekid
prekid = 100
global red
global stanje_reda
stanje_reda = 0
global zad
global druga_perioda
druga_perioda = 0
global prekinuti
prekinuti = 0
global ind
global postavi_prekid

def daj_iduci():
    global stanje_reda
    sljedeci_zadatak = 0
    tip = red[stanje_reda]
    stanje_reda = (stanje_reda + 1) % len(red)
    if tip != -1:
        sljedeci_zadatak = zad[tip][ind[tip]]
        ind[tip] = (ind[tip] + 1) % len(zad[tip])
    return sljedeci_zadatak

def radi_posao(x, timeout):
    global postavi_prekid, bez_prekoracenja, druga_perioda, prekinuti
    prekoracenje = False
    for i in range(math.floor(x/timeout)):
        time.sleep(timeout)
        if postavi_prekid:
            postavi_prekid = 0
            if bez_prekoracenja > 10:
                bez_prekoracenja = 0
                perioda = 2
                druga_perioda += 1
                print(f"({int(round((time.time() - start), 3) * 1000)}) Upravljac, dozvoljavam drugu periodu zadataku {zadatak_u_obradi}")
                prekoracenje = True
        else:
            prekinuti += 1
            print(f"({int(round((time.time() - start), 3) * 1000)}) Upravljac, prekidam obradu zadatka {zadatak_u_obradi}")
            return prekoracenje
    time.sleep(x%timeout)
    return prekoracenje


def controller():
    global postavi_prekid, bez_prekoracenja, zadatak_u_obradi
    obrada_list = [0.03, 0.05, 0.08, 0.12]
    timeout = 0.005
    while not end:
        if postavi_prekid:
            print("tu sam")
            postavi_prekid = 0
            zadatak_u_obradi = daj_iduci()
            if zadatak_u_obradi != -1 and trenutak_zadnjeg_odgovora[zadatak_u_obradi] < trenutak_zadnje_promjene_stanja[zadatak_u_obradi]:
                print(
                    f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {i}: promjena ({zadnji_odgovor[i]}->{stanje[i]}), obrađujem")
                perioda = 1
                vrijeme_obrade = random.choices(obrada_list, weights=[20, 50, 20, 10], k=1)[0]
                print(vrijeme_obrade)
                prekoracenje = radi_posao(vrijeme_obrade, timeout)
                if not prekoracenje:
                    #print("prekoracenjeeeeeeeeeeeeeeeeeee")
                    bez_prekoracenja += 1
                    trenutak_zadnjeg_odgovora[zadatak_u_obradi] = time.time() - start
                    print(
                        f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {i}: kraj obrade, postavljeno {stanje[i]}")
                    zadnji_odgovor[zadatak_u_obradi] = stanje[zadatak_u_obradi]
                else:
                    #print("tu sam")
                    postavi_prekid = 1
                    perioda = 0
                    continue
                perioda = 0

        time.sleep(timeout)




def simulator(ident: int, perioda: int):
    broj_promjena_stanja = 0
    suma_vremena_odgovora = 0
    maksimalno_vrijeme_odgovora = 0
    broj_problema = 0

    while not end:
        print(f"zapocinjem dretvu {ident}")
        stanje[ident] = rand.randint(100, 999)
        print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: promjena {stanje[ident]}")
        trenutak_zadnje_promjene_stanja[ident] = time.time() - start
        broj_promjena_stanja += 1

        time.sleep(perioda)

        if trenutak_zadnje_promjene_stanja[ident] > trenutak_zadnjeg_odgovora[ident]:
            print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: problem, nije odgovoreno; čekam odgovor")
            broj_problema += 1
            broj_promjena_stanja += -1
        else:
            trajanje_odgovora = trenutak_zadnjeg_odgovora[ident] - trenutak_zadnje_promjene_stanja[ident]
            suma_vremena_odgovora += trajanje_odgovora
            if maksimalno_vrijeme_odgovora < trajanje_odgovora:
                maksimalno_vrijeme_odgovora = trajanje_odgovora
            print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: odgovoreno ({trajanje_odgovora} od promjene")
    print(f"dretva {ident} -> prosjecno vrijeme odgovora = {suma_vremena_odgovora/broj_promjena_stanja}, max vrijeme: {maksimalno_vrijeme_odgovora }"
          f"broj problema: {broj_problema}")


if __name__ == "__main__":
    n = int(input("Unesi broj tipova zadataka: "))
    l = []
    for i in range(n):
        l.append([float(i) for i in input(f"Unesi period i broj zadataka za {i}. tip zadatatka odvojen razmakom: ").split(" ")])
    red = input(f"Unesi red: ").split(" ")
    red = [int(i) for i in red]
    index = 0
    zad = []
    for i in range(len(l)):
        tmp = []
        for j in range(int(l[i][1])):
            tmp.append(index)
            index += 1
        zad.append(tmp)
    stanje = [0 for i in range(index)]
    trenutak_zadnje_promjene_stanja = [0 for i in range(index)]
    zadnji_odgovor = [0 for i in range(index)]
    trenutak_zadnjeg_odgovora = [0 for i in range(index)]
    ind = [0 for i in range(n)]
    start = time.time()
    j = 0
    for i in range(len(zad)):
        for j in zad[i]:
            threading.Thread(target=simulator, args=(j, l[i][0],)).start()
    time.sleep(0.02)
    postavi_prekid = 1
    threading.Thread(target=controller).start()
    while True:
        try:
            time.sleep(0.1)
            print(f"({int(round((time.time() - start), 3) * 1000)}) Postavljam prekid")
            postavi_prekid = 1
        except KeyboardInterrupt:
            end = True
            print(f"Broj drugih perioda je {druga_perioda}")
            print(f"Broj prekinutih zadataka je {prekinuti}")
            time.sleep(1)
            sys.exit(0)
