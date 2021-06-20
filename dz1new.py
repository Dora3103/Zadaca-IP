from vepar import *


class T(TipoviTokena):
	
    FOR, IF, IN, RANGE, WHILE, TOČKAZ, DVOTOČKA, OOTV, OZATV, JEDNAKO, RAZLIČITO = 'for', 'if', 'in', 'range', 'while', ';', ':', '(', ')', '=', '!='
    VOTV, VZATV, MANJE, VEĆE, UOTV, UZATV = '{}<>[]'
    PLUS, MINUS, PUTA, KROZ, NA, ZAREZ = '+-*/^,'
    JJEDNAKO = '=='
    MANJEJ, VEĆEJ, PLUSP, PLUSJ = '<=', '>=', '++', '+='
    NEG, KONJ, DISJ = '!&|'
    NUM, LOG = 'num', 'log'
    ALARM = 'alarm' #naredbe za aktuatore
    ISITHERE, READTEMP =  'isItHere', 'readTemp' #funkcije za očitavanja stanja okoline
    class BROJ(Token): #double
        def vrijednost(self, _): return float(self.sadržaj)
        def optim(self): return self
    class IME(Token):
        def vrijednost(self, mem): return mem[self]
    class SAT(Token):
        def vrijednost(self, mem): return mem[self]
    class PVAR(Token):
        def vrijednost(self, mem): return mem[self]
        def optim(self): return self
    class LIME(Token):
        def vrijednost(self,mem): return mem[self]
    class SIME(Token): 
        def vrijednost (self, mem): return mem[self]
    class BROJS(Token):
        def vrijednost(self,_): return self.sadržaj[1:-1]
    class KOMENTAR(Token): pass
    class ISTINA(Token):
        literal = 'yes'
        def vrijednost(self): return True
    class LAŽ(Token):
        literal = 'no'
        def vrijednost(self): return False
    class NEPOZNATO(Token):
        literal = 'unknown'
        def vrijednost(self): return None
    class BREAK(Token):
        literal = 'break'
        def izvrši(self, mem): raise Prekid
    

    
def an(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak == '!':
            if lex >= '=': yield lex.token(T.RAZLIČITO)
            else: yield lex.token(T.NEG)
        elif znak == '+':
            if lex >= '+': yield lex.token(T.PLUSP)
            elif lex >= '=': yield lex.token(T.PLUSJ)
            else: raise lex.greška('u ovom jeziku nema samostalnog +')
        elif znak.isdecimal():
            if znak == '0':
                if lex.pogledaj().isdecimal():
                    lex.čitaj()
                    yield lex.token(T.BROJS)
            else:
                lex.zvijezda(str.isdecimal)
                if lex >= '.': 
                    lex.zvijezda(str.isdecimal)
                    yield lex.token(T.BROJ)
                else: yield lex.token(T.BROJ)
        elif znak == 'P': ## logička varijabla
            prvo = lex.čitaj()
            if not prvo.isdecimal():
                raise lex.greška('očekivana znamenka')
            if prvo != '0': lex.zvijezda(str.isdigit)
            yield lex.token(T.PVAR)
        elif znak == '_': ## ime liste
            lex.zvijezda(str.isalnum)
            yield lex.token(T.LIME)
        elif znak == '$': ## ime varijable za sat
            lex.zvijezda(str.isalnum)
            yield lex.token(T.SIME)
        elif znak.isalpha(): ## numerička varijabla
            lex.zvijezda(str.isalnum)
            yield lex.literal(T.IME, case=False)
        elif znak == '#':
            lex.pročitaj_do('#')
            lex.zanemari()
        elif znak == '=': yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        else: yield lex.literal(T)
        

### BKG:
# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | if | BREAK TOČKAZAREZ | pridruži | instrukcija
# petlja -> while naredba | for naredba | while VOTV naredbe VZATV | for VOTV naredbe VZATV
# for -> FOR OOTV IME# JEDNAKO BROJ TOČKAZ IME# MANJE BROJ TOČKAZ IME# inkrement OZATV
# inkrement -> PLUSP | PLUSJ BROJ
# grananje -> if naredba | if VOTV naredbe VZATV
# if -> IF OOTV uvjet OZATV
# while -> WHILE OOTV uvjet OZATV
# uvjet -> formula | OOTV aritizraz OZATV relacija OOTV aritizraz OZATV | sat relacija sat | IME relacija aritizraz

# relacija -> MANJE | MANJEJ | VEĆE | VEĆEJ | JJEDNAKO
# lista -> UOTV elementi UZTV
# elementi -> aritizraz ZAREZ elementi | '' | lista ZAREZ elementi
# numcast -> OOTV NUM OZATV formula
# logcast -> OOTV LOG OZATV aritizraz

# aritizraz -> aritizraz PLUS član | aritizraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor
# baza -> BROJ | IME | OTV aritizraz OZATV | numcast

# formula -> NEG formula | PVAR | OOTV formula binvez formula OZATV | logcast | ISTINA | LAŽ | NEPOZNATO
# binvez -> KONJ | DISJ
#### još ćemo nadodati ako što bude potrebno

# pridruži -> ime JEDANKO tip
# ime -> IME | LIME | PVAR | SIME
# tip -> aritizraz | lista | formula | SAT
# instrukcija -> alarm | -- ovo dovrsiti
# funkcija -> readTemp | isItHere -- ovo dovrsiti
# sat -> BROJ DVOTOČKA BROJ | BROJ DVOTOČKA BROJS


class P(Parser):
    def start(self):
        naredbe = [self.naredba()]
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe) ## ast
        
    def naredba(self):
        if self > T.IF: return self.grananje()
        elif self > T.FOR: return self.za()
        elif self > T.WHILE: return self.dok()
        elif ime := self > {T.IME, T.LIME, T.SIME}:
            self >> T.JEDNAKO
            return Pridruživanje(ime, self.tip(ime)) #ast
        # elif self #instrukcija
        elif br := self >> T.BREAK:
            self >> T.TOČKAZ
            return br
            
    def za(self):
        kriva_varijabla = SemantičkaGreška('Sva tri dijela for-petlje moraju imati istu varijablu.')
        self >> T.FOR, self >> T.OOTV
        i = self >> T.IME
        self >> T.JEDNAKO
        početak = self >> T.BROJ
        self >> T.TOČKAZ

        if (self >> T.IME) != i: raise kriva_varijabla
        self >> T.MANJE
        granica = self >> T.BROJ
        self >> T.TOČKAZ

        if (self >> T.IME) != i: raise kriva_varijabla
        if self >= T.PLUSP: inkrement = nenavedeno
        elif self >> T.PLUSJ: inkrement = self >> T.BROJ
        self >> T.OZATV

        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja1(i, početak, granica, inkrement, blok)
        
    def dok(self):
        self >> T.WHILE, self >> T.OOTV
        uvjet = self.uvjet()
        self >> T.OZATV
        
        if self >= T.VOTV:
            blok = []
            while not self >= T.VZATV: blok.append(self.naredba())
        else: blok = [self.naredba()]
        return Petlja2(uvjet, blok)
        
    def grananje(self):
        self >> T.IF, self >> T.OOTV
        uvjet = self.uvjet()
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
        elif ime ^ T.PVAR: return self.formula()
        elif ime ^ T.SIME: return self.sat()
        else: assert False, f'Nepoznat tip od {ime}'

    def aritizraz(self):
        članovi = [self.član()]
        while True:
            if self >= T.PLUS: članovi.append(self.član())
            elif self >= T.MINUS: članovi.append(Suprotan(self.član())) #ast
            else: return Zbroj.ili_samo(članovi) #ast
        
    def član(self):
        faktori = [self.faktor()]
        while True:
            if self >= T.PUTA: faktori.append(self.faktor())
            elif self >= T.KROZ: članovi.append(Recipročan(self.faktor())) #ast
            else: return Umnožak.ili_samo(faktori)
            
    def faktor(self):
        if op := self >= T.MINUS: return Suprotan(self.faktor())
        baza = self.baza()
        if op := self >= T.NA: return Potencija(op, baza, self.faktor()) #ast
        else: return baza
    
    def baza(self): #dodaj numcast
        if self >= T.OOTV:
            if self >= T.NUM:
                trenutni = self.numcast()
            else:
                trenutni = self.aritizraz()
                self >> T.OZATV
        else: trenutni = self >> {T.BROJ, T.IME}
        return trenutni
    
    def numcast(self): 
        self >> T.OZATV
        #return vrijednost formula

    def logcast(self): pass

    def lista(self):
        if self >= T.UOTV:
            if self >= T.UZATV: return Lista([])
            el = [self.element()]
            while self>=T.ZAREZ and not self>T.UZATV: el.append(self.element())
            self >> T.UZATV
            return Lista(el)
    
    def element(self):
        if self > T.UOTV: return self.lista()
        else: return self.aritizraz()

    def formula(self): pass
    
    def sat(self): 
        h = self >> T.BROJ
        dvo = self >> T.DVOTOČKA
        min = self >> {T.BROJ, T.BROJS}
        return Sat(h, dvo, min)
    
    def ime(self):
        return self >> {T.IME, T.SIME, T.PVAR, T.LIME}
        
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
    def izvrši(self, mem): return [el.vrijednost(mem) for el in self.elementi]

class Sat(AST('sat dvotočka minute')):
    def izvrši(self, mem): 
        if self.sat.vrijednost(mem) >= 0 and self.sat.vrijednost(mem) < 24:
            if int(self.minute.vrijednost(mem)) >= 0 and int(self.minute.vrijednost(mem)) <= 59:
                return str(self.sat.vrijednost(mem)) + str(self.dvotočka) + str(self.minute.vrijednost(mem))
            else:
                raise SemantičkaGreška('sat nedozvoljenog oblika')
        else:
            raise SemantičkaGreška('sat nedozvoljenog oblika')

class Zbroj(AST('pribrojnici')):
    def izvrši(self, mem):
        return sum(p.vrijednost(mem) for p in self.pribrojnici)
    
class Suprotan(AST('od')):
    def izvrši(self, mem): return -self.od.vrijednost(mem)
    
class Umnožak(AST('faktori')):
    def izvrši(self, mem):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem)
        return p

class Potencija(AST('baza eksponent') ):
    def izvrši(self, mem):
        return baza.vrijednost(mem) ** eksponent.vrijednost(mem)

        
class Petlja1(AST('varijabla početak granica inkrement blok')):
    def izvrši(self, mem):
        kv = self.varijabla  # kontrolna varijabla petlje
        mem[kv] = self.početak.vrijednost(mem)
        while mem[kv] < self.granica.vrijednost(mem):
            try:
                for naredba in self.blok: naredba.izvrši(mem)
            except Prekid: break
            inkr = self.inkrement
            if inkr is nenavedeno: inkr = 1
            else: inkr = inkr.vrijednost(mem)
            mem[kv] += inkr
   
class Petlja2(AST('uvjet blok')):
    def izvrši(self, mem):
        kv = self.uvjet
        while kv:
            try:
                for naredba in self.blok: naredba.izvrši(mem)
            except Prekid: break
            
class Grananje(AST('uvjet blok')):
    def izvrši(self, mem):
        print(self.uvjet)       # stavila samo za provjeru - zašto nije oblika T.ISTINA/T.LAŽ?
        if self.uvjet:
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

class Pridruživanje(AST('ime pridruženo')):
    def izvrši(self, mem):
        mem[self.ime] = self.pridruženo.vrijednost(mem)      
        
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

prog = P(''' if( 50 != 50 ){
                for(ir = 1; ir < 20; ir++){
                    break;
                    }} ''')
prikaz(prog)
prog.izvrši()
#print(x for x in mem_okol)
#P.tokeniziraj(ulaz)