import random
import random as rand
import time
import threading
import sys

global end
end = False
global stanje
global trenutak_zadnje_promjene_stanja
global zadnji_odgovor
global trenutak_zadnjeg_odgovora
global start

def controller(n):
    obrada_list = [0.03, 0.05, 0.08, 0.12]
    while not end:
        for i in range(n):
            if trenutak_zadnjeg_odgovora[i] < trenutak_zadnje_promjene_stanja[i]:
                print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {i}: promjena ({zadnji_odgovor[i]}->{stanje[i]}), obrađujem")
                vrijeme_obrade = random.choices(obrada_list, weights=[20, 50, 20, 10], k=1)[0]
                time.sleep(vrijeme_obrade)
                trenutak_zadnjeg_odgovora[i] = time.time() - start
                print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {i}: kraj obrade, postavljeno {stanje[i]}")
                zadnji_odgovor[i] = stanje[i]
            else:
                print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {i}: nema promjene {stanje[i]}")



def simulator(ident: int, perioda: int, nul_perioda: int, k: int):
    broj_promjena_stanja = 0
    suma_vremena_odgovora = 0
    maksimalno_vrijeme_odgovora = 0
    broj_problema = 0

    while not end:
        if time.time() - start > nul_perioda:
            print(f"zapocinjem dretvu {ident}")
            stanje[ident] = rand.randint(100, 999)
            print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: promjena {stanje[ident]}")
            trenutak_zadnje_promjene_stanja[ident] = time.time() - start
            #print("Tu sam")
            broj_promjena_stanja += 1

            time.sleep(1)

            if trenutak_zadnje_promjene_stanja[ident] > trenutak_zadnjeg_odgovora[ident]:
                print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: problem, nije odgovoreno; čekam odgovor")
                broj_problema += 1
                while trenutak_zadnje_promjene_stanja[ident] > trenutak_zadnjeg_odgovora[ident]:
                    time.sleep(0.01)
                    if end:
                        break
            else:
                trajanje_odgovora = trenutak_zadnjeg_odgovora[ident] - trenutak_zadnje_promjene_stanja[ident]

                suma_vremena_odgovora += trajanje_odgovora
                if maksimalno_vrijeme_odgovora < trajanje_odgovora:
                    maksimalno_vrijeme_odgovora = trajanje_odgovora
                dodatna_odgoda = random.uniform(0, k) * perioda
                print(f"({int(round((time.time() - start), 3) * 1000)})dretva-{ident}: odgovoreno ({trajanje_odgovora} od promjene; spavam do {(time.time() - start) + perioda + dodatna_odgoda}")
                time.sleep(perioda + dodatna_odgoda)
    print(f"dretva {ident} -> prosjecno vrijeme odgovora = {suma_vremena_odgovora/broj_promjena_stanja}, max vrijeme: {maksimalno_vrijeme_odgovora }"
          f"broj problema: {broj_problema}")


if __name__ == "__main__":
    n = int(input("Unesi broj ulaza: "))
    l = []
    for i in range(n):
        l.append(input("Unesi period i nul period odvojen razmakom: ").split(" "))
    k = int(input("Unesi k: "))
    stanje = [0 for i in range(n)]
    trenutak_zadnje_promjene_stanja = [0 for i in range(n)]
    zadnji_odgovor = [0 for i in range(n)]
    trenutak_zadnjeg_odgovora = [0 for i in range(n)]
    start = time.time()
    for i in range(n):
        threading.Thread(target=simulator, args=(i, float(l[i][0]), float(l[i][1]), k,)).start()
    threading.Thread(target=controller, args=(n,)).start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            end = True
            time.sleep(1)
            sys.exit(0)

