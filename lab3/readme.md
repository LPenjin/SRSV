LAB3. Upravljanje sustavom korištenjem višedretvenosti

Python u sebi nem ugrađeni SCHED_FIFO raspoređivač i dretve ne mogu imati prioritete.

Zato u strukturi podataka dretve odredim njezin prioritet. Kada podatak dode na ulaz, simulator ulaza prvo stavi posao u red koji prvo gleda prioritet dretve a zatim vrijeme dospijeća.

Dretve prvo čekaju na semaforu, te tada ne rade nista, ali kada rade posao, procesor je zauzet.

Zbog toga kada se ne korisit SCHED_FIFO raspoređivač sve dretve pokušavaju raditi svoj posao odjedanput te će se problemi češće desiti jer jedna drugoj kradu procesorsko vrijeme i znatno se uspore.

S obzirom da se gleda prioritet, neke dretve mogu čekati jako dugo jer nikada ne dođu na red.
