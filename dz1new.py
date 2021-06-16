from vepar import *


class T(TipoviTokena):
	
    FOR, IF, IN, RANGE, WHILE, TOČKAZ, DVOTOČKA, OOTV, OZATV, JEDNAKO, RAZLIČITO = 'for', 'if', 'in', 'range', 'while', ';', ':', '(', ')', '=', '!='
    VOTV, VZATV, MANJE, VEĆE, UOTV, UZATV = '{}<>[]'
    PLUS, MINUS, PUTA, KROZ, NA, ZAREZ = '+-*/^,'
    JJEDNAKO = '=='
    MANJEJ, VEĆEJ = '<=', '>='
    NEG, KONJ, DISJ = '!&|'
    NUM, LOG = 'num', 'log'
    ALARM = 'alarm' #naredbe za aktuatore
    ISITHERE, READTEMP =  'isItHere', 'readTemp' #funkcije za očitavanja stanja okoline
    class BROJ(Token): #double
        def vrijednost(self, _): return double(self.sadržaj)
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
    class SIME(Token): pass
    #class LISTA(Token): pass
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
    
##Ne radi nam sat u lexer-u - budemo popravili
    
def an(lex):
    for znak in lex:
        if znak.isspace(): lex.zanemari()
        elif znak.isdecimal():
            if lex >= ':': # sat oblika x:yz , x in range(0,10)
                if lex.pogledaj() in ['0','1','2','3','4','5']:
                   lex.čitaj()
                   if lex.pogledaj().isdecimal():
                        lex.čitaj()
                        yield lex.token(T.SAT)
                   else: lex.vrati()
                #else: lex.vrati()
            elif znak in {'1', '2'}: #sat oblika xy:zw, x in {1,2}, if x == 1, y in range(0,10), if x == 2, y in {0,1,2,3}
                if znak == '1':
                    if lex.pogledaj().isdecimal():
                        lex.čitaj()
                        if lex >= ':': # sat oblika x:yz , x in range(0,10)
                            if lex.pogledaj() in ['0','1','2','3','4','5']:
                                lex.čitaj()
                                if lex.pogledaj().isdecimal(): # in {'0','1','2','3','4','5','6','7','8','9'}:
                                    lex.čitaj()
                                    yield lex.token(T.SAT)
                                else: lex.vrati()
                        else: lex.vrati()
                elif znak == '2':
                    if lex.pogledaj() in ['0', '1', '2', '3']:
                        lex.čitaj()
                        if lex >= ':': 
                            if lex.pogledaj() in ['0','1','2','3','4','5']:
                                lex.čitaj()
                                if lex.pogledaj().isdecimal():
                                    lex.čitaj()
                                    yield lex.token(T.SAT)
                                else: lex.vrati()
                            else: lex.vrati()
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
       # elif znak == '[':
        #    num = 1
         #   prvoo = lex.čitaj()
          #  if prvoo.isalnum() or prvoo == '[':
           #     if prvoo =='[':
            #        num += 1
             #   lex.zvijezda(str.isalnum)
              #  while lex >= ',' or lex >= ' ': lex.zvijezda(str.isalnum)
            #lex >> ']'
           # num -=1
            #if prvoo == 0:
             #   yield lex.token(T.LISTA)
        elif znak == '#':
            lex.pročitaj_do('#')
            lex.zanemari()
        #elif znak == '*':
            #yield lex.token(T.NA if lex >= '*' else T.PUTA)
        elif znak == '=': yield lex.token(T.JJEDNAKO if lex >= '=' else T.JEDNAKO)
        else: yield lex.literal(T)
        




### BKG:
# start -> naredba naredbe
# naredbe -> '' | naredba naredbe
# naredba -> petlja | if | BREAK | pridruži | instrukcija
# petlja -> while | for
# for -> FOR IME IN RANGE OOTV BROJ ZAREZ BROJ ZAREZ aritizraz OZATV DVOTOČKA | FOR IME IN lista DVOTOČKA
# if -> IF uvjet DVOTOČKA naredba
# while -> WHILE uvjet DVOTOČKA VOTV naredbe VZATV
# uvjet -> formula | aritizraz relacija aritizraz | sat relacija sat

# relacija -> MANJE | MANJEJ | VEĆE | VEĆEJ | JJEDNAKO
# lista -> UOTV elementi UZTV
# elementi -> aritizraz | aritizraz ZAREZ elementi | '' | lista ZAREZ elementi
# numcast -> OOTV NUM OZATV formula
# logcast -> OOTV LOG OZATV aritizraz

# aritizraz -> aritizraz PLUS član | aritizraz MINUS član | član
# član -> član PUTA faktor | član KROZ faktor | faktor
# faktor -> baza NA faktor | baza | MINUS faktor
# baza -> BROJ | IME | OTV aritizraz OZATV | numcast

# formula -> NEG formula | PVAR | OOTV formula binvez formula OZATV | logcast | ISTINA | LAŽ
# binvez -> KONJ | DISJ
#### još ćemo nadodati ako što bude potrebno

# pridruži -> ime JEDANKO tip
# ime -> IME | LIME | PVAR | SIME
# tip -> aritizraz | lista | formula | SAT
# instrukcija -> alarm |
# funkcija -> readTemp | isItHere

# sat -> BROJ DVOTOČKA BROJ BROJ | BROJ BROJ DVOTOČKA BROJ BROJ


class P(Parser):
    def start(self):
        naredbe = [self.naredba()]
        while not self > KRAJ: naredbe.append(self.naredba())
        return Program(naredbe) ## ast
    def naredba(self):
        if self > T.IF: return self.grananje()
        elif self > T.FOR: return self.za()
        elif self > T.WHILE: return self.dok()
        elif self > T.BREAK: return T.PREKID
       # elif self #instrukcija
        else:
            ime = self.ime()
            self >> T.JEDNAKO
            return Pridruživanje(ime, self.tipa(ime)) #ast
    def za(self): pass
    def dok(self): pass
    def grananje(self): pass
    def tipa(self, ime):
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
    def formula(self): pass
    def sat(self): pass
        
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
    def vrijednost(self): return [el.vrijednost() for el in self.elementi]

class Sat(AST('sat')):
    def vrijednost(self): pass

class Zbroj(AST('pribrojnici')):
    def vrijednost(self, mem, unutar):
        return sum(p.vrijednost(mem, unutar) for p in self.pribrojnici)
    
class Suprotan(AST('od')):
    def vrijednost(self, mem, unutar): return -self.od.vrijednost(mem, unutar)
    
class Umnožak(AST('faktori')):
    def vrijednost(self, mem, unutar):
        p = 1
        for faktor in self.faktori: p *= faktor.vrijednost(mem, unutar)
        return p

class Potencija(AST('baza eksponent') ):
    def vrijednost(self, mem, unutar):
        return baza.vrijednost(mem, unutar) ** eksponent.vrijednost(mem, unutar)


class Usporedba(AST('lijevo relacija desno')):
    def vrijednost(self, mem, unutar):
        l = self.lijevo.vrijednost(mem, unutar)
        d = self.desno.vrijednost(mem, unutar)
        if self.relacija ^ T.JJEDNAKO: return l == d
        elif self.relacija ^ T.MANJE: return l < d
        elif self.relacija ^ T.VEĆE: return l > d
        elif self.relacija ^ T.MANJEJ: return l <= d
        elif self.relacija ^ T.VEĆEJ: return l >= d
        elif self.relacija ^ T.RAZLIČITO: return l != d
        else: assert False, f'Nepoznata relacija {self.relacija}'

        
        
#ulaz = '#asdasd#'
#ulaz = '!(P5&!!(P6 | P9))'
#ulaz = '123456, 456'
#ulaz = 'for math in range (1,2,3): naredba'
#ulaz = 'if a < 2:825 : naredba'
#ulaz = 'vlagazraka = 289^91'
#ulaz = 'a8 = [[4 ,8]]'
ulaz = '23:69'
#ulaz = 'a = 8'
#ulaz = 'P5 = true'
#print(ulaz)

#print(x for x in mem_okol)
P.tokeniziraj(ulaz)