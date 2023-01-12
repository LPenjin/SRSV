import random
import random as rand
import time
import threading
import sys
import argparse
import os

global end
end = False
global stanje
global trenutak_zadnje_promjene_stanja
global zadnji_odgovor
global trenutak_zadnjeg_odgovora
global start
global broj_iteracija
broj_iteracija = 100000
global semaphore
global queue
queue = []


def get_priorities(l):
    tmp = [[l[i][0], i] for i in range(len(l))]
    tmp.sort()
    tmp2 = []
    priority = 2
    tmp2.append([priority, int(tmp[0][1])])
    for i in range(1, len(tmp)):
        if tmp[i-1][0] < tmp[i][0]:
            priority += 1
        tmp2.append([priority, int(tmp[i][1])])

    priorities2 = [0] * len(tmp)
    for i in tmp2:
        priorities2[i[1]] = i[0]
    return priorities2



def trosi_10_ms():
    a = 0
    for i in range(broj_iteracija):
        a += i
    return a

def odredi_broj_iteracija():
    global broj_iteracija
    vrti = 1
    while vrti:
        t0 = time.time()
        trosi_10_ms()
        t1 = time.time()
        if t1 - t0 > 0.01:
            vrti = 0
        else:
            broj_iteracija *= 10
    broj_iteracija = int((broj_iteracija * 10)/((t1-t0)*1000))

def simuliraj_x_ms(n):
    for i in range(int(n/10)):
        trosi_10_ms()


def controller(ulaz, period):
    obrada_list = [0.1, 0.2, 0.4, 0.7]
    while not end:
        if SCHED_FIFO:
            semaphore.acquire()
            if trenutak_zadnjeg_odgovora[ulaz] < trenutak_zadnje_promjene_stanja[ulaz]:
                if queue[0][2] == ulaz:
                    del(queue[0])
                    print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {ulaz}: promjena ({zadnji_odgovor[ulaz]}->{stanje[ulaz]}), obrađujem")
                    vrijeme_obrade = float(random.choices(obrada_list, weights=[50, 30, 15, 5], k=1)[0]) * period * 1000
                    print(f"Vrijeme obrade je {vrijeme_obrade}")
                    t0 = time.time()
                    a = simuliraj_x_ms(vrijeme_obrade)
                    t1 = time.time()
                    trenutak_zadnjeg_odgovora[ulaz] = time.time() - start
                    print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {ulaz}: kraj obrade, postavljeno {stanje[ulaz]}, utrošeno vrijeme: {t1-t0}")
                    zadnji_odgovor[ulaz] = stanje[ulaz]
            semaphore.release()
            #else:
                #print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {ulaz}: nema promjene {stanje[ulaz]}")
        else:
            print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {ulaz}: promjena ({zadnji_odgovor[ulaz]}->{stanje[ulaz]}), obrađujem")
            vrijeme_obrade = float(random.choices(obrada_list, weights=[50, 30, 15, 5], k=1)[0]) * period * 1000
            print(f"Vrijeme obrade je {vrijeme_obrade}")
            t0 = time.time()
            a = simuliraj_x_ms(vrijeme_obrade)
            t1 = time.time()
            trenutak_zadnjeg_odgovora[ulaz] = time.time() - start
            print(f"({int(round((time.time() - start), 3) * 1000)})upr: ulaz {ulaz}: kraj obrade, postavljeno {stanje[ulaz]}, utrošeno vrijeme: {t1 - t0}")
            zadnji_odgovor[ulaz] = stanje[ulaz]


def simulator(ident: int, perioda: int, nul_perioda: int, k: int, prioritet: int):
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
            if SCHED_FIFO:
                queue.append((prioritet, time.time(), ident))
                queue.sort()
            #print(queue)
            broj_promjena_stanja += 1

            time.sleep(perioda)

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
          f" broj problema: {broj_problema}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--SCHED_FIFO', dest='SCHED_FIFO', type=int, default=0, help='0 = SCHED_FIFO disabled, 1 = SCHED_FIFO enabled')
    parser.add_argument('-n', dest='n', type=int, default=0,
                        help='Number of maximum running threads')
    args = parser.parse_args()
    SCHED_FIFO = args.SCHED_FIFO
    if SCHED_FIFO:
        print("Koristim SCHED_FIFO")
    n = args.n
    semaphore = threading.Semaphore(n)
    t0 = time.time()
    odredi_broj_iteracija()
    print(time.time() - t0)
    print(broj_iteracija)
    n = int(input("Unesi broj ulaza: "))
    l = []
    for ulaz in range(n):
        l.append(input("Unesi period i nul period odvojen razmakom: ").split(" "))
    k = int(input("Unesi k: "))
    print(broj_iteracija)
    stanje = [0 for i in range(n)]
    trenutak_zadnje_promjene_stanja = [0 for i in range(n)]
    zadnji_odgovor = [0 for i in range(n)]
    trenutak_zadnjeg_odgovora = [0 for i in range(n)]
    start = time.time()
    priorities = get_priorities(l)
    print(priorities)
    for ulaz in range(n):
        threading.Thread(target=simulator, args=(ulaz, float(l[ulaz][0]), float(l[ulaz][1]), k, priorities[ulaz], )).start()
        threading.Thread(target=controller, args=(ulaz, float(l[ulaz][0]), )).start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            end = True
            time.sleep(1)
            sys.exit(0)

