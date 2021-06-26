from vepar import *
from datetime import datetime
from time import sleep

#senzori
okolina = {'Rex': True, 'Fifi': True, 'Kokos': True} # je li pas prisutan
glad = {'Rex': False, 'Fifi': True, 'Kokos': False} #je li pas gladan
temperatura=37.5 #temperatura zraka

#aktuatori
alarm = False # je li upaljen alarm

N = "'"

class T(TipoviTokena):
    FOR, IF, WHILE, DVOTOČKA, OOTV, OZATV, JEDNAKO, RAZLIČITO = 'for', 'if', 'while', ':', '(', ')', '=', '!='
    VOTV, VZATV, MANJE, VEĆE, UOTV, UZATV = '{}<>[]'
    PLUS, MINUS, PUTA, KROZ, NA, ZAREZ = '+-*/^,'
    JJEDNAKO = '=='
    MANJEJ, VEĆEJ, PLUSP, PLUSJ, MINUSM, MINUSJ = '<=', '>=', '++', '+=', '--', '-='
    NEG, KONJ, DISJ = '!&|'
    MOD = '%'
    NUM, LOG, LIST, STR = 'num', 'log', 'list', 'str'
    ALARM = 'alarm' #naredbe za aktuatore
    ISITHERE, READTEMP, ISHUNGRY =  'isItHere', 'readTemp', 'isHungry' #funkcije za očitavanja stanja okoline
    PRINTOUT, LENGTH = 'printout', 'length'
    #CURRENTTIME = 'currentTime'
    class BROJ(Token): #double
        def vrijednost(self, _): return float(self.sadržaj)
        def optim(self): return self
    class IME(Token):
        def vrijednost(self, mem): return mem[self]
    class PVAR(Token):
        def vrijednost(self, mem): return mem[self]
        def optim(self): return self
    class LIME(Token):
        def vrijednost(self,mem): return mem[self]
    class SIME(Token): 
        def vrijednost (self, mem): return mem[self]
    class SBROJ(Token):
        def vrijednost(self, _): return int(self.sadržaj)
    class MBROJ(Token):
        def vrijednost(self,_): return self.sadržaj
    class KOMENTAR(Token): pass
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
    class STRIME(Token):
        def vrijednost(self,mem): return mem[self]
    class STRING(Token):
        def vrijednost(self,_): return self.sadržaj[1:-1]
    class TOČKAZ(Token):
        literal = ';'
        def vrijednost(self,_): return self.sadržaj
    class CURRENTTIME(Token):
        literal = 'currentTime'
        def vrijednost(self,_): return datetime.now().strftime("%H:%M")
    class INDEX(Token):
        def vrijednost(self,mem): return int(self.sadržaj[1:len(self.sadržaj)])
    class PAS(LIME): #posebna lista u ojem robot čuva imena pasa
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
        elif znak == '~':
            lex.zvijezda(str.isalnum)
            yield lex.token(T.STRIME)
        elif znak == N:
            lex.pročitaj_do(N)
            yield lex.token(T.STRING)
        elif znak.isalpha(): ## numerička varijabla
            lex.zvijezda(identifikator)
            yield lex.literal(T.IME, case=True)
        elif znak == '#':
            lex.pročitaj_do('#', više_redova=True)
            lex.zanemari()
        elif znak == '=': yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        elif znak == '%':
            if lex.pogledaj().isdecimal():
                lex.plus(str.isdecimal)
                yield lex.token(T.INDEX)
            else: yield lex.token(T.MOD)
        else: yield lex.literal(T)
        

### BKG:
# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | if | BREAK TOČKAZAREZ | pridruži | instrukcija | IME PLUSP
# petlja -> while naredba | for naredba | while VOTV naredbe VZATV | for VOTV naredbe VZATV
# for -> FOR OOTV IME# JEDNAKO BROJ TOČKAZ IME# MANJE BROJ TOČKAZ IME# inkrement OZATV
# inkrement -> PLUSP | PLUSJ BROJ
# if -> IF OOTV uvjet OZATV VOTV naredbe VZATV
# while -> WHILE OOTV uvjet OZATV

# uvjet -> formula | OOTV aritizraz OZATV relacija OOTV aritizraz OZATV | sat relacija sat | IME relacija aritizraz

# pridruži -> IME JEDNAKO aritizraz | LIME JEDNAKO liste | PVAR JEDNAKO logizraz | SIME JEDNAKO sat | STRIME JEDNAKO string

## tipovi podataka
# aritizraz -> aritizraz PLUS član | aritizraz MINUS član | član 
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor
# baza -> BROJ | IME | OOTV aritizraz OZATV | numcast | length OOTV liste OZATV | length OOTV string OZATV

# logizraz -> logizraz DISJ logčlan | logčlan
# logčlan -> logčlan KONJ logfaktor | logfaktor
# logfaktor -> NEG logfaktor | PVAR | ISTINA | LAŽ | NEPOZNATO | aritizraz relacija aritizraz | sat relacija sat | logcast | string relacija string | isithere

# relacija -> MANJE | MANJEJ | VEĆE | VEĆEJ | JJEDNAKO | RAZLIČITO

# string -> STRIME | STRING | stringcast

# sat -> sbroj DVOTOČKA BROJ | sbroj DVOTOČKA MBROJ | SIME | currentTime OOTV OZATV
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
# printizraz -> lista | logizraz | '' | sat | string
# instrukcija -> alarm | -- ovo dovrsiti
# funkcija -> readTemp | isItHere -- ovo dovrsiti
# isithere -> isItHere OOTV pas OZATV
# pas -> string | PAS UOTV index UZATV
# index -> INDEx | MOD IME


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
        elif ime := self >= T.IME:
            if self >= T.PLUSP: return PPlus(ime)
            elif self >= T.PLUSJ: return PlusJ(ime, self.aritizraz()) #ast
            elif self >= T.MINUSM: return MMinus(ime) #ast
            elif self >= T.MINUSJ: return MinusJ(ime, self.aritizraz()) #ast
            else:
                self >> T.JEDNAKO
                return Pridruživanje(ime, self.tip(ime)) 
        elif ime := self >= {T.LIME, T.SIME, T.STRIME, T.PAS, T.PVAR}:
            self >> T.JEDNAKO
            return Pridruživanje(ime, self.tip(ime))

        # elif self #instrukcija
    
            
    def za(self):
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
        
    def dok(self):
        self >> T.WHILE, self >> T.OOTV
        #uvjet = self.uvjet()
        logiz = self.logizraz()
        self >> T.OZATV
        
        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        naredba1 = nenavedeno
        naredba2 = nenavedeno
        return Petlja(naredba1, logiz, naredba2, blok)
        
    def grananje(self):
        self >> T.IF, self >> T.OOTV
        #uvjet = self.uvjet()
        uvjet = self.logizraz()
        self >> T.OZATV
        
        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Grananje(uvjet, blok)
    
        
    def uvjet(self):
        if broj1 := self >= T.BROJ:
            rel = self >> {T.MANJE, T.VEĆE, T.JJEDNAKO, T.MANJEJ, T.VEĆEJ, T.RAZLIČITO}
            if self >= T.OOTV:
                broj2 = self.aritizraz()
                return Uvjet(broj1, broj2, rel)
            broj2 = self >> T.BROJ
            return Uvjet(broj1, broj2, rel)
        elif self >= T.OOTV:
            broj1 = self.aritizraz()
            self >> T.OZATV
            rel = self >> {T.MANJE, T.VEĆE, T.JJEDNAKO, T.MANJEJ, T.VEĆEJ, T.RAZLIČITO}
            if self >= T.OOTV:
                broj2 = self.aritizraz()
                self >> T.OZATV
                return Uvjet(broj1, broj2, rel)
            broj2 = self >> T.BROJ
            return Uvjet(broj1, broj2, rel)
        elif ime := self >= T.IME:
            rel = self >> {T.MANJE, T.VEĆE, T.JJEDNAKO, T.MANJEJ, T.VEĆEJ, T.RAZLIČITO}
            broj = self.aritizraz()
            return Uvjet(ime, broj, rel)
        else: formula = self.formula()
        return formula
        

    def tip(self, ime):
        if ime ^ T.IME: return self.aritizraz()
        elif ime ^ T.LIME: return self.lista()
        elif ime ^ T.PVAR: return self.logizraz()
        elif ime ^ T.SIME: return self.sat()
        elif ime ^ T.STRIME: return self.string()
        elif ime ^ T.PAS: return self.pas()
        else: assert False, f'Nepoznat tip od {ime}'

    def funkcija(self):
        if self >= T.ISITHERE:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return isItHere(pas)
        if self >= T.ISHUNGRY:
            self >> T.OOTV
            if lista := self >= T.PAS:
                self >> T.UOTV
                index = self.index()
                pas = Index(lista, index)
                self >> T.UZATV
            else: pas = self.string()
            self >> T.OZATV
            return isHungry(pas)
        if self >= T.READTEMP:
            return readTemp()
    

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
                članovi.append(Suprotan(self.član())) #ast
            else: return Zbroj.ili_samo(članovi) #ast
        
    def član(self):
        faktori = [self.faktor()]
        while True:
            if self >= T.PUTA: 
                self.tokena_parsirano += 1
                faktori.append(self.faktor())
            elif self >= T.KROZ: 
                self.tokena_parsirano += 1
                faktori.append(Recipročan(self.faktor())) #ast
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
    
    def baza(self): #dodaj numcast
        if self >= T.OOTV:
            self.tokena_parsirano += 1
            if self >= T.NUM:
                self.tokena_parsirano += 1
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
            return readTemp()
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
        elif self > {T.SBROJ, T.MBROJ, T.SIME}: return Usporedba(self.sat(), self.relacija(), self.sat())
        elif self >= T.OOTV: #arit izraz, možda promeniti zagrade
            if self > T.LOG:
                return self.cast()
        elif self > {T.STRIME, T.STRING}: return Usporedba(self.string(), self.relacija(), self.string())
        elif self > T.ISITHERE: return self.funkcija()
        elif self > T.ISHUNGRY: return self.funkcija()
        else: return Usporedba(self.aritizraz(), self.relacija(), self.aritizraz())

    def cast(self):
        tip = self >> {T.NUM, T.LOG, T.LIST, T.STR}
        self.tokena_parsirano += 1
        self >> T.OZATV
        self.tokena_parsirano += 1
        return Cast(tip, self.izraz())

    def izraz(self):
        if self > {T.BROJ, T.MINUS, T.IME, T.OOTV}: return self.aritizraz()
        elif self > {T.SIME, T.SBROJ}: return self.sat()
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
        elif self > T.SBROJ: return self.sat()
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
            return self >> T.IME

    
    def sat(self): 
        if sat := self >= T.CURRENTTIME: 
            self >> T.OOTV
            self >> T.OZATV
            return sat
        elif self > T.SIME: 
            sat = self >> T.SIME
            if self > {T.MANJE, T.MANJEJ, T.JJEDNAKO, T.RAZLIČITO, T.VEĆEJ, T.VEĆE}:
                return Usporedba(sat, self.relacija(), self.sat())
            else: return sat
        h = self >> {T.SBROJ, T.MBROJ}
        self >> T.DVOTOČKA
        min = self >> {T.BROJ, T.MBROJ}

        if self > {T.MANJE}:
            return Usporedba(Sat(h,min), self.relacija(), self.sat())
        else: return Sat(h, min)
    
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

    def alarm(self):
        if self >= T.ALARM:
            self >> T.OOTV
            sekunde = self.aritizraz()
            self >> T.OZATV
            return Alarm(sekunde)
    tokena_parsirano = 0
    def printizraz(self): #dodati aritizraz
        if self > T.UOTV: return self.lista()
        elif self > {T.SIME, T.SBROJ, T.MBROJ}: 
            return self.sat()
        elif self >= T.OOTV:
            if self > {T.STR, T.NUM, T.LOG, T.LIST}:
                return self.cast()
        elif forPrint :=  self >= {T.STRING, T.STRIME, T.LIME, T.TOČKAZ, T.IME}: return forPrint
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
    def vrijednost(self,mem): return 1/(self.od.vrijednost(mem))

class PPlus(AST('pribrojnik')):
    def izvrši(self,mem): mem[self.pribrojnik] = self.pribrojnik.vrijednost(mem) + 1

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
            return float(izraz) #popraviti za stringove i sat
        elif self.tip ^ T.LOG: return bool(izraz) #popraviti za sat
        elif self. tip ^ T.LIST: return [izraz]
        elif self.tip ^ T.STR: return str(izraz)

        
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
        #print(self.uvjet.vrijednost(mem))       # stavila samo za provjeru - zašto nije oblika T.ISTINA/T.LAŽ?
        if self.uvjet.vrijednost(mem):
            for naredba in self.blok: naredba.izvrši(mem)
            
        
class Uvjet(AST('lijevo desno relacija')):
    def izvrši(self, mem):
        l = self.lijevo.vrijednost(mem)
        r = self.relacija
        d = self.desno.vrijednost(mem)
        if r ^ T.MANJE:
            if l < d: return T.ISTINA
            else: return T.LAŽ
        elif r ^ T.VEĆE:
            if l > d: return T.ISTINA
            else: return T.LAŽ
        elif r ^ T.MANJEJ:
            if l <= d: return T.ISTINA
            else: return T.LAŽ
        elif r ^ T.VEĆEJ:
            if l >= d: return T.ISTINA
            else: return T.LAŽ
        elif r ^ T.JJEDNAKO:
            if l == d: return T.ISTINA
            else: return T.LAŽ
        elif r ^ T.RAZLIČITO:
            if l == d: return T.LAŽ
            else: return T.ISTINA
        else: assert False, 'nepokriveni slučaj'

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

class isItHere(AST('pas')):
    def vrijednost(self, mem):
        return okolina[self.pas.vrijednost(mem)]

class isHungry(AST('pas')):
    def vrijednost(self, mem):
        return glad[self.pas.vrijednost(mem)]

class readTemp(AST('')):
    def vrijednost(self, mem):
        return temperatura

class Index(AST('lista index')):
    def vrijednost(self,mem):
        return self.lista.vrijednost(mem)[int(self.index.vrijednost(mem))]

class Duljina(AST('čega')):
    def vrijednost(self, mem):
        return len(self.čega.vrijednost(mem))


class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime] = self.pridruženo.vrijednost(mem) 

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
        

        
#ulaz = '#asdasd#'
#ulaz = '!(P5&!!(P6 | P9))'
#ulaz = '123456, 456'
#ulaz = '1'
#P.tokeniziraj(ulaz)
#ulaz = 'for math in range (1,2,3): naredba'
#ulaz = 'if a < 2:825 : naredba'
#ulaz = 'vlagazraka = 289^91'
#ulaz = 'a8 = [[4 ,8]]'
#ulaz = '23:59'
#ulaz = 'a = 8'
#ulaz = 'P5 = true'
#print(ulaz)

#prog = P('_a = [[5+5], [6], [-4]]')
#prog.izvrši()

#prog = P(''' for(i = 5; i< 10; i++){} ''')
#prog = P(''' while(51 < 50){
#                break;} ''')

#prog = P(''' if( 50 == 50 ){
 #               for(ir = 1; ir < 20; ir++){
  #                  #printout(ir)#
   #                 break;
    #                }
     #               } ''')
#ulaz = '''a = 5+5 printout(a)'''
ulaz = '''
    _A=[1,'banana',3,'jabuka']
    for(i = 0; i < 15; i++){
    j = i
   # printout(i; j)#
    while(j < 10){
        j++
        printout(i; j; readTemp; isItHere('Fifi'); isHungry('Kokos'))
        alarm(4)
    }
} '''
#prog1 = P ('''a = 5+5 printout(a)''')
#prikaz(prog)
#prog1.izvrši()
#ulaz2 = "$s = 15:00 ~str = 'program' printout((list)$s; ~str)"
ulaz3 = "a = 5 b = 7.5 if(a+1 > b-1){ a = a + b } printout(a)"
ulaz4 = '''i = 0
            while(yes){
                if( i > 5 ){
                    break;
                }
                i++
            }
            printout(i)
'''
ulaz5 = "$s = currentTime() printout($s)"
ulaz7 = '''_dog = ['Fifi', 'Rex', 'Kokos']
            for( i = 0; i < length(_dog); i++){
                if( !isItHere(_dog[%i]) ){
                    printout(_dog[%i]; 'is gone!' )
                }
            }
'''
prog2 = P(ulaz)
#prikaz(prog2)
prog2.izvrši()
#print(x for x in mem_okol)
#P.tokeniziraj(ulaz5)
