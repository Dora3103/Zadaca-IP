# Zadaca-IP

Druga domaća zadaća
8. lipnja 2020.
Nedavno ste se zaposlili u uspješnoj firmi koja se pokušava probiti na propulzivan,
no sve zasićeniji tržišni segment. Vaš projektni tim je zadužen dizajnirati jezik za
programiranje revolucionarnog novog robota (detalje robota precizirajte sami; ideja
mora biti kreativna kako bi robot postao hit te kako bi firma i dalje mogla plaćati
besplatne ručkove radi kojih ste tamo). Jezik mora imati barem:
• jedan brojevni, jedan logički te jedan lisni tip (liste osim vrijednosti brojevnog i
logičkog tipa mogu sadržavati druge liste),
• izraze koji sadrže:
– jednostavna pridruživanja (varijabla poprima vrijednost izraza odgovarajućeg tipa) te eksplicitno pretvaranje iz bilo kojeg tipa u bilo koji tip,
– aritmetičke operacije (četiri osnovne operacije, unarni minus, potenciranje,
usporedbe <, >, ≤, ≥, =, 6=),
– barem dvije funkcije za očitavanje stanja okoline pomoću ugrađenih senzora
(npr. temperatura i vlažnost zraka, postojanje prepreke, tlak pare u bojleru,
potpuna zatvorenost ventila, razina zvuka, itd.),
– tri istinosne konstante i logičke veznike (¬, ∧, ∨) Kleenejeve trovaljane
logike (https://en.wikipedia.org/wiki/Three-valued_logic); ideja je
olakšati zaključivanje s nepotpunim podacima,
• naredbe koje podržavaju:
– grananje, petlje i nelokalnu kontrolu toka,
– barem dvije instrukcije za upotrebu ugrađenih aktuatora (npr. pomicanje,
svrdlanje, hlađenje, zalijevanje, zvučna uzbuna, centrifugiranje, itd.) čime
se može promijeniti stanje okoline te
• jednu vrstu komentara (linijske ili višelinijske).
Napišite lekser, gramatiku i parser za svoj jezik. Napišite i semantički analizator
koji za zadani niz naredbi te zadanu okolinu (inicijaliziranu prije uključivanja robota
koji izvršava naredbe) vizualizira/ispisuje utjecaj rada robota na spomenutu okolinu.
Dokumentirajte svoj kod komentarima i/ili tekstom u odvojenoj datoteci.
Napišite barem tri programa za svog robota: dva sasvim uobičajena za njegovu
upotrebu te jedan krajnje impresivan kojim ćete zadiviti i šefa i stručnjake iz ostalih
timova. Kompliciranije dijelove tih programa pojasnite komentarima u njihovom kodu.
Za dodatne bodove, proširite jezik daljnjim mogućnostima i/ili napravite slajdove
pomoću kojih ćete prezentirati svoj dizajn na skorom projektnom sastanku
