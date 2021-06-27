from vepar import *
from datetime import datetime
from time import sleep

#senzori
okolina = {'Rex': True, 'Fifi': True, 'Kokos': True} # je li pas prisutan
glad = {'Rex': False, 'Fifi': True, 'Kokos': False} #je li pas gladan
temperatura=37.5 #temperatura zraka

#aktuatori
alarm = False # je li upaljen alarm
klima = 0 # promjena temperature u sekundi
trazim = [] #koga trazim, od kada
hranim = [] #koga hranim, od kada

zadnja_provjera=datetime.now().timestamp()

N = "'"

class T(TipoviTokena):
    FOR, IF, WHILE, DVOTOČKA, OOTV, OZATV, JEDNAKO, RAZLIČITO = 'for', 'if', 'while', ':', '(', ')', '=', '!='
    VOTV, VZATV, MANJE, VEĆE, UOTV, UZATV = '{}<>[]'
    PLUS, MINUS, PUTA, KROZ, NA, ZAREZ = '+-*/^,'
    JJEDNAKO = '=='
    MANJEJ, VEĆEJ, PLUSP, PLUSJ, MINUSM, MINUSJ, PUTAJ, KROZJ = '<=', '>=', '++', '+=', '--', '-=', '*=', '/='
    NEG, KONJ, DISJ = '!&|'
    MOD = '%'
    NUM, LOG, LIST, STR = 'num', 'log', 'list', 'str'
    ALARM, CONDCHN, DOGSEARCH, FEED, STOPSEARCH, STOPFEED, REFRESH = 'alarm', 'condChn', 'dogSearch', 'feed', 'stopSearch', 'stopFeed', 'refresh' #naredbe za aktuatore, condChn mijenja klimu, refresh osvježava senzore
    ISITHERE, READTEMP, ISHUNGRY =  'isItHere', 'readTemp', 'isHungry' #funkcije za očitavanja stanja okoline
    PRINTOUT, LENGTH = 'printout', 'length'
    CURRENTTIME = 'currentTime'
    class BROJ(Token): #double
        def vrijednost(self, _): return float(self.sadržaj)
    class IME(Token): #varijabla za numerički tip
        def vrijednost(self, mem): return mem[self]
    class PVAR(Token): #varijabla za logički tip
        def vrijednost(self, mem): return mem[self]
    class LIME(Token): #varijabla za liste
        def vrijednost(self,mem): return mem[self]
    class SIME(Token): #varijabla za sat
        def vrijednost (self, mem): return mem[self]
    class SBROJ(Token): #posebni oblik broja za sat
        def vrijednost(self, _): return int(self.sadržaj)
    class MBROJ(Token): #posebni oblik broja za sat
        def vrijednost(self,_): return self.sadržaj
    class ISTINA(Token):
        literal = 'yes'
        def vrijednost(self,_): return True
    class LAŽ(Token):
        literal = 'no'
        def vrijednost(self,_): return False
    class NEPOZNATO(Token,):
        literal = 'unknown'
        def vrijednost(self,_): return None
    class BREAK(Token):
        literal = 'break'
        def izvrši(self, mem): raise Prekid
    class STRIME(Token): #vaijabla za string
        def vrijednost(self,mem): return mem[self]
    class STRING(Token):
        def vrijednost(self,_): return self.sadržaj[1:-1]
    class TOČKAZ(Token):
        literal = ';'
        def vrijednost(self,_): return self.sadržaj
    class INDEX(Token): #indexiranje liste
        def vrijednost(self,mem): return int(self.sadržaj[1:len(self.sadržaj)])
    class PAS(LIME): #posebna lista u kojem robot čuva imena pasa
        literal = '_dog'

    
def an(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '!':
            if lex >= '=': yield lex.token(T.RAZLIČITO)
            else: yield lex.token(T.NEG)
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: yield lex.token(T.PLUS)
        elif znak.isdecimal():
            if znak == '1':
                if lex.pogledaj().isdecimal():
                    lex.čitaj()
                    if lex.pogledaj() == ':':
                        yield lex.token(T.SBROJ)
                    else:
                        lex.zvijezda(str.isdecimal)
                        if lex >= '.': 
                            lex.plus(str.isdecimal)
                            yield lex.token(T.BROJ)
                        else: yield lex.token(T.BROJ)
                else:
                    lex.zvijezda(str.isdecimal)
                    if lex >= '.': 
                        lex.plus(str.isdecimal)
                        yield lex.token(T.BROJ)
                    else: yield lex.token(T.BROJ)
            elif znak == '2':
                if lex.pogledaj() in ['0', '1', '2', '3']:
                    lex.čitaj()
                    if lex.pogledaj() == ':':
                        yield lex.token(T.SBROJ)
                    else:
                        lex.zvijezda(str.isdecimal)
                        if lex >= '.': 
                            lex.plus(str.isdecimal)
                            yield lex.token(T.BROJ)
                        else: yield lex.token(T.BROJ)
                else:
                    lex.zvijezda(str.isdecimal)
                    if lex >= '.': 
                        lex.plus(str.isdecimal)
                        yield lex.token(T.BROJ)
                    else: yield lex.token(T.BROJ)
            elif znak == '0':
                if lex.pogledaj().isdecimal():
                    lex.čitaj()
                    yield lex.token(T.MBROJ)
                else:
                    lex.zvijezda(str.isdecimal)
                    if lex >= '.': 
                        lex.plus(str.isdecimal)
                        yield lex.token(T.BROJ)
                    else: yield lex.token(T.BROJ)
            else:
                lex.zvijezda(str.isdecimal)
                if lex >= '.': 
                    lex.plus(str.isdecimal)
                    yield lex.token(T.BROJ)
                else: yield lex.token(T.BROJ)
        elif znak == 'P': ## logička varijabla
            prvo = lex.čitaj()
            if not prvo.isdecimal():
                raise lex.greška('očekivana znamenka')
            if prvo != '0': lex.zvijezda(str.isdigit)
            yield lex.token(T.PVAR)
        elif znak == '_': ## ime liste
            lex.zvijezda(identifikator)
            yield lex.literal(T.LIME, case=True)
        elif znak == '$': ## ime varijable za sat
            lex.zvijezda(identifikator)
            yield lex.token(T.SIME)
        elif znak == '~': #varijabla za string
            lex.zvijezda(str.isalnum)
            yield lex.token(T.STRIME)
        elif znak == N:
            lex.pročitaj_do(N)
            yield lex.token(T.STRING)
        elif znak.isalpha(): ## numerička varijabla
            lex.zvijezda(identifikator)
            yield lex.literal(T.IME, case=True)
        elif znak == '#': #komentari
            lex.pročitaj_do('#', više_redova=True)
            lex.zanemari()
        elif znak == '=': yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak == '>': yield lex.token(T.VEĆEJ if lex >= '=' else T.VEĆE)
        elif znak == '<': yield lex.token(T.MANJEJ if lex >= '=' else T.MANJE)
        elif znak == '-': 
            if lex >= '-': yield lex.token(T.MINUSM)
            elif lex >= '=': yield lex.token(T.MINUSJ)
            else: yield lex.token(T.MINUS)
        elif znak =='*': yield lex.token(T.PUTAJ if lex >= '=' else T.PUTA)
        elif znak == '/': yield lex.token(T.KROZJ if lex >= '=' else T.KROZ)
        elif znak == '!': yield lex.token(T.RAZLIČITO if lex >= '=' else T.NEG)
        elif znak == '%':
            if lex.pogledaj().isdecimal():
                lex.plus(str.isdecimal)
                yield lex.token(T.INDEX)
            else: yield lex.token(T.MOD)
        else: yield lex.literal(T)
        

### BKG:
# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | if | BREAK TOČKAZAREZ | pridruži | condChn  | dogSearch | feed | stopSearch | stopFeed | refresh | ispis | alarm | IME inkr/dekr
# petlja -> while naredba | for naredba | while VOTV naredbe VZATV | for VOTV naredbe VZATV
# for -> FOR OOTV pridruži TOĆKAZ logizraz TOČKAZ IME inkr/dekr
# inkr/dekr -> PLUSP | PLUSJ aritizraz | MINUSM | MINUSJ arititraz | PUTAJ aritizraz | KROZJ aritizraz 
# if -> IF OOTV logizraz OZATV VOTV naredbe VZATV
# while -> WHILE OOTV logizraz OZATV

# pridruži -> IME JEDNAKO aritizraz | LIME JEDNAKO liste | PVAR JEDNAKO logizraz | SIME JEDNAKO sat | STRIME JEDNAKO string | LIME UOTV index UZATV izraz | 

## tipovi podataka
# aritizraz -> aritizraz PLUS član | aritizraz MINUS član | član 
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor
# baza -> BROJ | IME | OOTV aritizraz OZATV | numcast | LENGTH OOTV liste OZATV | LENGTH OOTV string OZATV

# logizraz -> logizraz DISJ logčlan | logčlan
# logčlan -> logčlan KONJ logfaktor | logfaktor
# logfaktor -> NEG logfaktor | PVAR | ISTINA | LAŽ | NEPOZNATO | aritizraz relacija aritizraz | sat relacija sat | logcast | string relacija string | isithere | ishungry

# relacija -> MANJE | MANJEJ | VEĆE | VEĆEJ | JJEDNAKO | RAZLIČITO

# string -> STRIME | STRING | stringcast

# sat -> sbroj DVOTOČKA BROJ | sbroj DVOTOČKA MBROJ | SIME | CURRENTTIME OOTV OZATV
# sbroj -> SBROJ | MBROJ

# liste -> lista | LIME | listcast
# lista -> UOTV elementi UZTV | listcast
# elementi -> aritizraz ZAREZ elementi | '' | lista ZAREZ elementi | STRING ZAREZ elementi | sat ZAREZ elementi

##castanje
# numcast -> OOTV NUM OZATV izraz
# logcast -> OOTV LOG OZATV  izraz
# listcast -> OOTV LIST OZATV izraz 
# strcast -> OOTV STR OZATV izraz 
# izraz -> aritizraz | logizraz | sat | string

##funkcije i naredbe
# ispis -> PRINTOUT OOTV printizraz TOČKAZ printizraz OZATV
# printizraz -> lista | logizraz | '' | sat | string | aritizraz 
# condChn -> condChn OOTV aritizraz OZATV
# dogSearch -> dogSearch OOTV pas OZATV
# feed -> feed OOTV pas OZATV
# stopSearch -> stopSearch OOTV pas OZATV
# stopFeed -> stopFeed OOTV pas OZATV
# refresh -> refresh
# funkcija -> readtemp | isithere | ishungry
# readtemp -> READTEMP
# isithere -> isItHere OOTV pas OZATV
# ishungry -> isHungry OOTV pas OZATV
# alarm -> ALARM OOTV aritizraz OZATV
# pas -> string | PAS UOTV index UZATV
# index -> INDEX | MOD IME


class P(Parser):
    def start(self):
        naredbe = [self.naredba()]
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe) ## ast
        
    def naredba(self):
        if self > T.IF: return self.grananje()
        elif self > T.FOR: return self.za()
        elif self > T.WHILE: return self.dok()
        elif br := self >= T.BREAK:
            self >> T.TOČKAZ
            return br
        elif self > T.PRINTOUT: return self.ispis()
        elif self > T.ALARM: return self.alarm()
        elif self > T.CONDCHN: return self.condChn()
        elif self > T.DOGSEARCH: return self.dogSearch()
        elif self > T.FEED: return self.feed()
        elif self > T.STOPSEARCH: return self.stopSearch()
        elif self > T.STOPFEED: return self.stopFeed()
        elif self > T.REFRESH: return self.refresh()
        elif ime := self >= T.IME:
            if self >= T.PLUSP: return PPlus(ime)
            elif self >= T.PLUSJ: return PlusJ(ime, self.aritizraz())
            elif self >= T.MINUSM: return MMinus(ime)
            elif self >= T.MINUSJ: return MinusJ(ime, self.aritizraz())
            elif self >= T.PUTAJ: return PutaJ(ime, self.aritizraz())
            elif self >= T.KROZJ: return KrozJ(ime, self.aritizraz())
            else:
                self >> T.JEDNAKO
                if lista := self >= T.LIME:
                    self >> T.UOTV
                    ind =  self.index()
                    self >> T.UZATV
                    return PridruživanjeIzListe(ime, ind, lista)
                else: return Pridruživanje(ime, self.tip(ime)) 
        elif ime := self >= T.LIME:
            if self >= T.UOTV:
                ind = self.index()
                self >> T.UZATV
                self >> T.JEDNAKO
                if iz := self >= T.LIME:
                    self >> T.UOTV
                    ind2 = self.index()
                    self >> T.UZATV
                    return PridruživanjeUListi(ime, ind, Index(iz, ind2))
                else: return PridruživanjeUListi(ime, ind, self.izraz())
            else: 
                self >> T.JEDNAKO
                if lista := self >= T.LIME:
                    if self >= T.UOTV:
                        ind = self.index()
                        self >> T.UZATV
                        return PridruživanjeIzListe(ime, ind, lista)
                    else: return Pridruživanje(ime, lista)
                else: return Pridruživanje(ime, self.tip(ime)) 
        elif ime := self >= {T.SIME, T.STRIME, T.PAS, T.PVAR}:
            self >> T.JEDNAKO
            if lista := self >= T.LIME:
                    self >> T.UOTV
                    ind = self.index()
                    self >> T.UZATV
                    return PridruživanjeIzListe(ime, ind, lista)
            else: return Pridruživanje(ime, self.tip(ime))
            
    def za(self): #for petlja
        self >> T.FOR, self >> T.OOTV
        naredba1 = self.naredba()
        self >> T.TOČKAZ
        
        logiz = self.logizraz()
        self >> T.TOČKAZ

        naredba2 = self.naredba()
        self >> T.OZATV

        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja(naredba1, logiz, naredba2, blok)
        
    def dok(self): #while petlja
        self >> T.WHILE, self >> T.OOTV
        logiz = self.logizraz()
        self >> T.OZATV
        
        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        naredba1 = nenavedeno
        naredba2 = nenavedeno
        return Petlja(naredba1, logiz, naredba2, blok)
        
    def grananje(self): #if
        self >> T.IF, self >> T.OOTV
        uvjet = self.logizraz()
        self >> T.OZATV
        
        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Grananje(uvjet, blok)

    def tip(self, ime):
        if ime ^ T.IME: return self.aritizraz()
        elif ime ^ T.LIME: return self.lista()
        elif ime ^ T.PVAR: return self.logizraz()
        elif ime ^ T.SIME: return self.sat()
        elif ime ^ T.STRIME: return self.string()
        elif ime ^ T.PAS: return self.pas()
        else: assert False, f'Nepoznat tip od {ime}'

    def isItHere(self):
        if self >= T.ISITHERE:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return IsItHere(pas)

    def isHungry(self):
        if self >= T.ISHUNGRY:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return IsHungry(pas)

    def alarm(self):
        if self >= T.ALARM:
            self >> T.OOTV
            sekunde = self.aritizraz()
            self >> T.OZATV
            return Alarm(sekunde)

    def condChn(self):
        if self >= T.CONDCHN:
            self >> T.OOTV
            snaga = self.aritizraz()
            self >> T.OZATV
            return CondChn(snaga)

    def dogSearch(self):
        if self >= T.DOGSEARCH:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return DogSearch(pas)

    def feed(self):
        if self >= T.FEED:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return Feed(pas)

    def stopSearch(self):
        if self >= T.STOPSEARCH:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return StopSearch(pas)

    def stopFeed(self):
        if self >= T.STOPFEED:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return StopFeed(pas)

    def refresh(self):
        if self >= T.REFRESH:
            return Refresh()

    def relacija(self):
        return self >> {T.MANJEJ, T.MANJE, T.VEĆE, T.VEĆEJ, T.JJEDNAKO, T.RAZLIČITO}

    def aritizraz(self):
        članovi = [self.član()]
        while True:
            if self >= T.PLUS: 
                self.tokena_parsirano += 1
                članovi.append(self.član())
            elif self >= T.MINUS: 
                self.tokena_parsirano += 1
                članovi.append(Suprotan(self.član()))
            else: return Zbroj.ili_samo(članovi)
        
    def član(self):
        faktori = [self.faktor()]
        while True:
            if self >= T.PUTA: 
                self.tokena_parsirano += 1
                faktori.append(self.faktor())
            elif self >= T.KROZ: 
                self.tokena_parsirano += 1
                faktori.append(Recipročan(self.faktor()))
            else: return Umnožak.ili_samo(faktori)
            
    def faktor(self):
        if self >= T.MINUS: 
            self.tokena_parsirano += 1
            return Suprotan(self.faktor())
        baza = self.baza()
        if self >= T.NA: 
            self.tokena_parsirano += 1
            return Potencija(baza, self.faktor())
        else: return baza
    
    def baza(self): 
        if self >= T.OOTV:
            self.tokena_parsirano += 1
            if self > T.NUM:
               # self.tokena_parsirano += 1
                trenutni = self.cast()
            else:
                trenutni = self.aritizraz()
                self >> T.OZATV
                self.tokena_parsirano += 1
        elif self >= T.LENGTH:
            self.tokena_parsirano += 1
            self >> T.OOTV
            self.tokena_parsirano += 1
            if self > {T.STRIME, T.STRING}: item = self.string()
            else: item = self.lista()
            self >> T.OZATV
            self.tokena_parsirano += 1
            return Duljina(item)
        elif self >= T.READTEMP:
            self.tokena_parsirano += 1
            return ReadTemp()
        elif lista := self >= T.LIME:
            self >> T.UOTV
            ind = self.index()
            self >> T.UZATV 
            trenutni = Index(lista, ind)
        else: 
            trenutni = self >> {T.BROJ, T.IME}
            self.tokena_parsirano += 1
        return trenutni
    
    def logizraz(self):
        članovi = [self.logčlan()]
        while True:
            if self >= T.DISJ: članovi.append(self.logčlan())
            else: return Disjunkcija.ili_samo(članovi) #ast

    def logčlan(self):
        faktori = [self.logfaktor()]
        while True:
            if self >= T.KONJ: faktori.append(self.logfaktor())
            else: return Konjunkcija.ili_samo(faktori) #ast

    def logfaktor(self):
        if self >= T.NEG: return Negacija(self.logfaktor())
        elif faktor := self >= {T.ISTINA, T.NEPOZNATO, T.LAŽ}: return faktor
        elif faktor := self >= T.PVAR:
            if self > {T.JJEDNAKO, T.MANJE, T.MANJEJ, T.VEĆE, T.VEĆEJ, T.RAZLIČITO}: return Usporedba(faktor, self.relacija(), self.logizraz())
            else: return faktor
        elif self > {T.SBROJ, T.MBROJ, T.SIME}: return Usporedba(self.sat(), self.relacija(), self.sat())
        elif self >= T.OOTV: 
            if self > T.LOG:
                return self.cast()
        elif self > {T.STRIME, T.STRING}: return Usporedba(self.string(), self.relacija(), self.string())
        elif self > T.ISITHERE: return self.isItHere()
        elif self > T.ISHUNGRY: return self.isHungry()
        elif lista := self >=T.LIME:
            self >> T.UOTV
            ind = self.index()
            self >> T.UZATV
            return Usporedba(Index(lista, ind), self.relacija(), self.aritizraz())
        else: return Usporedba(self.aritizraz(), self.relacija(), self.aritizraz())

    def cast(self):
        tip = self >> {T.NUM, T.LOG, T.LIST, T.STR}
        self.tokena_parsirano += 1
        self >> T.OZATV
        self.tokena_parsirano += 1
        return Cast(tip, self.izraz())

    def izraz(self):
        if self > {T.BROJ, T.MINUS, T.IME, T.OOTV}: return self.aritizraz()
        elif self > {T.SIME, T.SBROJ, T.CURRENTTIME}: return self.sat()
        elif self > {T.STRIME, T.STRING}: return self.string()
        elif self > {T.LIME, T.UOTV}: return self.lista()
        else: return self.logizraz()

    def lista(self):
        if self > T.LIME:

            self.tokena_parsirano += 1

            return self >> T.LIME
        if self > T.PAS: 
            self.tokena_parsirano += 1
            return self >> T.PAS
        if self >= T.OOTV:
            self.tokena_parsirano += 1
            if self > T.LIST:
                return self.cast()
        elif self >= T.UOTV:
            self.tokena_parsirano += 1
            if self >= T.UZATV: 
                self.tokena_parsirano += 1
                return Lista([])
            el = [self.element()]
            while self >= T.ZAREZ and not self>T.UZATV: 
                self.tokena_parsirano += 1
                el.append(self.element())
            self >> T.UZATV
            self.tokena_parsirano += 1
            return Lista(el)
    
    def element(self):
        if self > T.UOTV: return self.lista()
        elif self > T.STRING: return self.string()
        elif self > {T.SBROJ, T.MBROJ} : return self.sat()
        else: return self.aritizraz()
    
    def pas(self):
        self >> T.UOTV
        psi = [self.string()]
        while self >= T.ZAREZ and not self > T.UZATV: psi.append(self.string())
        self >> T.UZATV
        return Lista(psi)

    def index(self):
        if ind := self >= T.INDEX: return ind
        else:
            self >> T.MOD
            if ind := self >= T.IME: return ind
            else: return self.aritizraz()
    
    def sat(self): 
        if self >= T.CURRENTTIME: 
            self >> T.OOTV
            self >> T.OZATV
            return currentTime()
        elif self > T.SIME: return self >> T.SIME
        h = self >> {T.SBROJ, T.MBROJ}
        self >> T.DVOTOČKA
        min = self >> {T.BROJ, T.MBROJ}
        return Sat(h, min)
    
    def string(self):
        if self >= T.OOTV:
            self.tokena_parsirano += 1
            if self > T.STR:
                return self.cast()
        else: 
            return self >> {T.STRING, T.STRIME}
            self.tokena_parsirano += 1
    
    def ime(self):
        return self >> {T.IME, T.SIME, T.PVAR, T.LIME, T.STRIME, T.PAS}
    
    def ispis(self):
        if self >= T.PRINTOUT:
            self >> T.OOTV
            izrazi = [self.printizraz()]
            while not self > T.OZATV: izrazi.append(self.printizraz())
            self >> T.OZATV
            return Ispis(izrazi)

    tokena_parsirano = 0
    def printizraz(self):
        if self > T.UOTV: return self.lista()
        elif self > {T.SIME, T.SBROJ, T.MBROJ}: 
            return self.sat()
        elif self >= T.OOTV:
            if self > {T.STR, T.NUM, T.LOG, T.LIST}:
                return self.cast()
        elif forPrint := self >= T.LIME:
            if self >= T.UOTV:
                forPrint = Index(forPrint, self.index())
                self >> T.UZATV
                return forPrint
            else: return forPrint
        elif forPrint :=  self >= {T.STRING, T.STRIME, T.TOČKAZ, T.IME}: return forPrint
        elif forPrint := self >= T.PAS:
            if self >= T.UOTV:
                forPrint = Index(forPrint, self.index())
                self >> T.UZATV
                return forPrint
            else: return forPrint
        else:
            try:
                self.tokena_parsirano = 0
                return self.aritizraz()
            except:
                for _ in range(self.tokena_parsirano): self.vrati()
                return self.logizraz()
        
    lexer = an

class Prekid(NelokalnaKontrolaToka): """Signal koji šalje naredba break."""

### AST
# Program: naredbe:[naredba]


class Program(AST('naredbe')):
    def izvrši(self):
        mem = Memorija()
        try:  # break izvan petlje je zapravo sintaksna greška - kompliciranije
            for naredba in self.naredbe: naredba.izvrši(mem)
        except Prekid: raise SemantičkaGreška('nedozvoljen break izvan petlje')

class Lista(AST('elementi')):
    def vrijednost(self, mem): return [el.vrijednost(mem) for el in self.elementi]

class Sat(AST('sat minute')):
    def vrijednost(self, mem): 
        if str(self.sat.vrijednost(mem)) >= '00' and str(self.sat.vrijednost(mem)) < '24':
            if str(self.minute.vrijednost(mem)) >= '00' and str(self.minute.vrijednost(mem)) <= '09':
                return str(self.sat.vrijednost(mem)) + ':' + str(self.minute.vrijednost(mem))
            elif int(self.minute.vrijednost(mem)) >= 10 and int(self.minute.vrijednost(mem)) <= 59:
                return str(self.sat.vrijednost(mem)) + ':' + str(int(self.minute.vrijednost(mem))) 
            else:
                raise SemantičkaGreška('sat nedozvoljenog oblika')
        else:
            raise SemantičkaGreška('sat nedozvoljenog oblika')

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem):
        return sum(p.vrijednost(mem) for p in self.pribrojnici)
    
class Suprotan(AST('od')):
    def vrijednost(self, mem): return -self.od.vrijednost(mem)
    
class Umnožak(AST('faktori')):
    def vrijednost(self, mem):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem)
        return p

class Recipročan(AST('od')):
    def vrijednost(self,mem): 
        kroz = self.od.vrijednost(mem)
        if kroz != float(0): return 1/kroz

class PPlus(AST('pribrojnik')):
    def izvrši(self,mem): mem[self.pribrojnik] = self.pribrojnik.vrijednost(mem) + 1

class PlusJ(AST('pribrojnik1 pribrojik2')):
    def izvrši(self,mem): mem[self.pribrojnik1] = self.pribrojnik1.vrijednost(mem) + self.pribrojnik2.vrijednost(mem)

class MMinus(AST('pribrojnik')):
    def izvrši(self,mem): mem[self.pribrojnik] = self.pribrojnik.vrijednost(mem) - 1

class MinusJ(AST('pribrojnik1 pribrojik2')):
    def izvrši(self,mem): mem[self.pribrojnik1] = self.pribrojnik1.vrijednost(mem) - self.pribrojnik2.vrijednost(mem)

class PutaJ(AST('faktor1 faktor2')):
    def izvrši(self,mem): mem[self.faktor1] = self.faktor1.vrijednost(mem) * self.faktor2.vrijednost(mem)

class KrozJ(AST('faktor1 faktor2')):
    def izvrši(self,mem): mem[self.faktor1] = self.faktor1.vrijednost(mem) / self.faktor2.vrijednost(mem) #nula

class Potencija(AST('baza eksponent') ):
    def vrijednost(self, mem):
        return self.baza.vrijednost(mem) ** self.eksponent.vrijednost(mem)

class Konjunkcija(AST('konjunkti')):
    def vrijednost(self,mem):
        k = True
        for varijabla in self.konjunkti: k = k and varijabla.vrijednost(mem)
        return k

class Disjunkcija(AST('disjunkti')):
    def vrijednost(self,mem):
        d = False
        for varijabla in self.disjunkti: d = d or varijabla.vrijednost(mem)
        return d

class Negacija(AST('formula')):
    def vrijednost(self, mem): return not self.formula.vrijednost(mem)

class Cast(AST('tip izraz')):
    def vrijednost(self,mem):
        izraz = self.izraz.vrijednost(mem)
        if self.tip ^ T.NUM: 
            if not type(izraz) is str: return float(izraz) #sat
            if type(izraz) is str:
                if izraz.isdecimal(): return float(izraz)
                if not izraz.isdecimal():
                    spl1 = izraz.rsplit('.')
                    spl2 = izraz.rsplit(':')
                    if len(spl1) == 2 and len(spl2) == 1:
                        if spl1[0].isdecimal() and spl1[1].isdecimal(): return float(izraz)
                        else: raise SemantičkaGreška('Zadani string nije broj')
                    elif len(spl2) == 2 and len(spl1) == 1:
                        if spl2[0] >= '00' and spl2[0] <= '23':
                            if spl2[1] >= '00' and spl2[1] <='59':
                                return float(spl2[0]) + float(spl2[1])/60
                            else: return SemantičkaGreška('Zadani string nije broj')
                        else: return SemantičkaGreška('Zadani string nije broj')
                    else: return SemantičkaGreška('Zadani string nije broj')
        elif self.tip ^ T.LOG: return bool(izraz)
        elif self. tip ^ T.LIST: return [izraz]
        elif self.tip ^ T.STR: 
            if izraz is True: return 'yes'
            elif izraz is False: return 'no'
            elif izraz is None: return 'unknown'
            else: return str(izraz)

        
class Petlja(AST('naredba1 logiz naredba2 blok')):
    def izvrši(self, mem):
        if self.naredba1 is not nenavedeno: self.naredba1.izvrši(mem)
        while self.logiz.vrijednost(mem):
            try:
                for naredba in self.blok: naredba.izvrši(mem)
            except Prekid: break
            if self.naredba2 is not nenavedeno: self.naredba2.izvrši(mem) 

class Grananje(AST('uvjet blok')):
    def izvrši(self, mem):
        if self.uvjet.vrijednost(mem):
            for naredba in self.blok: naredba.izvrši(mem)
            

class Usporedba(AST('lijevo relacija desno')):
    def vrijednost(self, mem):
        l = self.lijevo.vrijednost(mem)
        d = self.desno.vrijednost(mem)
        if self.relacija ^ T.JJEDNAKO: return l == d
        elif self.relacija ^ T.MANJE: return l < d
        elif self.relacija ^ T.VEĆE: return l > d
        elif self.relacija ^ T.MANJEJ: return l <= d
        elif self.relacija ^ T.VEĆEJ: return l >= d
        elif self.relacija ^ T.RAZLIČITO: return l != d
        else: assert False, f'Nepoznata relacija {self.relacija}'

class IsItHere(AST('pas')):
    def vrijednost(self, mem):
        return okolina[self.pas.vrijednost(mem)]

class IsHungry(AST('pas')):
    def vrijednost(self, mem):
        return glad[self.pas.vrijednost(mem)]

class ReadTemp(AST('')):
    def vrijednost(self, mem):
        return temperatura

class currentTime(AST('')):
    def vrijednost(self,mem):
        return datetime.now().strftime("%H:%M")

class Index(AST('lista index')):
    def vrijednost(self,mem):
        return self.lista.vrijednost(mem)[int(self.index.vrijednost(mem))]

class Duljina(AST('čega')):
    def vrijednost(self, mem):
        return len(self.čega.vrijednost(mem))

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime] = self.pridruženo.vrijednost(mem) 

class PridruživanjeUListi(AST('ime ind pridruženo')):
    def izvrši(self,mem):
        mem[self.ime][int(self.ind.vrijednost(mem))] = self.pridruženo.vrijednost(mem) 

class PridruživanjeIzListe(AST('ime index lista')):
    def izvrši(self, mem):
        pridruži = self.lista.vrijednost(mem)[int(self.index.vrijednost(mem))]
        ime = self.ime
        greška = SemantičkaGreška('Pogrešni tip podataka')
        if ime ^ T.IME:
            if not type(pridruži) is float: raise greška
        if ime ^ T.LIME:
            if not type(pridruži) is list: raise greška
        if ime ^ T.STRIME:
            if not type(pridruži) is str: raise greška
        if ime ^ T.SIME: #to složiti
            if not type(pridruži) is str: raise greška
        if ime ^ T.PVAR:
            if not type(pridruži) is bool: raise greška
        mem[ime] = pridruži

class Ispis(AST('izrazi')):
    def izvrši(self, mem):
        for izraz in self.izrazi: 
            if izraz.vrijednost(mem) == ';':
               print(' ', end='')
            elif izraz.vrijednost(mem) is True:
               print('yes', end='')
            elif izraz.vrijednost(mem) is False:
                print('no', end='')
            elif izraz.vrijednost(mem) is None:
                print('unknown', end='')
            else:
                print(izraz.vrijednost(mem), end='')
        print()

class Alarm(AST('sekunde')):
    def izvrši(self,mem):
        s_od_epohe = datetime.now().timestamp()
        print('Palim alarm!')
        alarm = True
        while s_od_epohe+self.sekunde.vrijednost(mem) > datetime.now().timestamp() : sleep(1)
        print('Gasim alarm!')
        alarm= False
        
class CondChn(AST('snaga')):
    def izvrši(self,mem):
        global klima
        klima=self.snaga.vrijednost(mem)
        rijec = 'hladi' if klima<0 else 'grije'
        print('Mijenjam klimu da',rijec,abs(klima),'stupnjeva u sekundi.')

class DogSearch(AST('pas')):
    def izvrši(self,mem):
        global trazim
        tpas=self.pas.vrijednost(mem)
        for a in trazim:
            if tpas==a[0]:
                print('Vec trazim tog psa!')
                return
        if tpas not in okolina:
            print('Psa',tpas,'nemam zapisano')
            return
        if okolina[tpas]:
            print('Taj pas je prisutan')
            return
        trazim.append([tpas, datetime.now().timestamp()])
        print('Pocinjem traziti',tpas,'!')

class Feed(AST('pas')):
    def izvrši(self,mem):
        global hranim
        hpas=self.pas.vrijednost(mem)
        for a in hranim:
            if hpas==a[0]:
                print('Vec hranim tog psa!')
                return
        if hpas not in glad:
            print('Psa',hpas,'nemam zapisano')
            return
        if not glad[hpas]: 
            print('Taj pas nije gladan!')
            return
        hranim.append([hpas, datetime.now().timestamp()])
        print('Pocinjem hraniti',hpas,'!')


class StopSearch(AST('pas')):
    def izvrši(self,mem):
        global trazim
        tpas=self.pas.vrijednost(mem)
        i=-1
        for a in trazim:
            i+=1
            if tpas==a[0]:
                trazim.pop(i)
                print('Prestajem traziti',tpas,'!')
                return
        print('Ne trazim tog psa!')

class StopFeed(AST('pas')):
    def izvrši(self,mem):
        global hranim
        hpas=self.pas.vrijednost(mem)
        i=-1
        for a in hranim:
            i+=1
            if hpas==a[0]:
                hranim.pop(i)
                print('Prestajem hraniti',hpas,'!')
                return
        print('Ne hranim tog psa!')

class Refresh(AST('')): #ova funkcija je simulacija osvjezavanja senzora, prava funkcija bi jako ovisila o samom hardveru, i nebi radila ove izracune
    def izvrši(self,mem):
        global okolina, glad, trazim, hranim, temperatura, zadnja_provjera
        vrijeme=datetime.now().timestamp()
        i=-1
        for a in trazim:
            i+=1
            if a[1]+20<vrijeme and not okolina[a[0]]:
                print('Pronašao sam',a[0],'!')
                okolina[a[0]]=True
                trazim.pop(i)
        i=-1
        for a in hranim:
            i+=1
            if a[1]+5<vrijeme and glad[a[0]]:
                print('Nahranio sam',a[0],'!')
                glad[a[0]]=False
                hranim.pop(i)
        temperatura+=(vrijeme-zadnja_provjera)*klima
        zadnja_provjera=vrijeme

