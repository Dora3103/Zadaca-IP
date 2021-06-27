from dz1new import *

ulaz1 =  '''
$šetnja1 = 07:30
$šetnja2 = 20:30

_dog = ['Fifi', 'Kokos', 'Rex']

    for( i = 0; i < length(_dog); i++){
                if( !isItHere(_dog[%i]) ){
                    printout(_dog[%i]; 'je nestao!' )
                    dogSearch(_dog[%i])
                }
                if( isHungry(_dog[%i] ) ){
                    printout(_dog[%i]; 'je gladan' )
                    feed(_dog[%i])
                }
            }
    if( $šetnja1 == currentTime() | $šetnja2 == currentTime()){
        printout('Vrijeme je za šetnju')
    }

'''

#P.tokeniziraj(ulaz1)
prog1 = P(ulaz1)
#prikaz(prog1)
prog1.izvrši()

ulaz2 = '''
printout(readTemp) #citam temperaturu, postavim klimu na +0.01, čekam 4 sekunde, pokrecem senzore, citam ponovo - mora biti promijene# 
    condChn(0.01)
    alarm(4)
    refresh
    printout(readTemp)
    dogSearch('Fifi') #trazim fifi, ali je tu#
    feed('Kokos') #hranim kokos, ali je sit#
    feed('Fifi') #hranim fifi#
    stopFeed('Fifi') #prestajem hraniti fifi#
    feed('Rex') #taj pas ne postoji#
    feed('Fifi') #opet hranim fifi#
    alarm(6) #čekam 6 sekundi#
    refresh #fifi je sada sita#
    printout(isHungry('Fifi'))

'''

#P.tokeniziraj(ulaz2)
prog2 = P(ulaz2)
#prikaz(prog2)
prog2.izvrši()

qsis='''
_A = [39,17,89,67,10,39,45,67,50,65,59,9,66,51,6,16,94,68,75,94,74,33,58,61,40,76,3,6,37,8,64,98]
l = 0
h = length(_A) - 1
_stack = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #inicijaliziramo stack, recimo veličine 50, trebala bi nam dinamička alokacija memorije da možemo ovisno o duljini niza#
top = 0 #na stack ce ici pocetak i kraj nizova koje zelimo sortirat u iducoj iteraciji#
_stack[%top] = l
top++
_stack[%top] = h
while(top >= 0) {
        h = _stack[%top] #vucemo sa stacka jednu listu za sortiranje#
        top--
        l = _stack[%top]
        top--
        x = _A[%h]
        i = l-1
        for (j = l; j <= h-1; j++) { #radimo jednu iteraciju quicksorta#
                if (_A[%j] <= x) {
                        i++
                        temp = _A[%i]
                        _A[%i] = _A[%j]
                        _A[%j] = temp
                }
        }
        i++
        temp = _A[%i]
        _A[%i] = _A[%h]
        _A[%h] = temp
        #i je pivot#
        if (i-1 > l & i-1-l>6) { #lijevo od pivota cine novu listu za sort#
                top++
                _stack[%top] = l
                top++
                _stack[%top] = i-1
        }
        if (i-1 > l & i-1-l<=6 & i-1-l>1) { #ako je manja od 6 elemenata insertion sortaj ju#
                start = l
                end = i-1
                for (x = start + 1; x < end; x++) {
                        val = _A[%x]

                        for (j = x-1; j >= 0 & val < _A[%j]; j--) {
                                pos = j+1
                                _A[%pos] = _A[%j]

                        }
                        pos=j+1
                        _A[%pos] = val
                }
        }
        if (i+1 < h & h-i-1<=6 & h-i-1>6) { #desno od pivota cine novu listu za sort#
                top++
                _stack[%top] = i + 1
                top++
                _stack[%top] = h
        }
        if (i-1 > l & i-1-l<=6) { #ako je manja od 6 elemenata insertion sortaj ju#
                start = i+1
                end = h
                for (x = start + 1; x < end; x++) {
                        val = _A[%x]

                        for (j = x-1; j >= 0 & val < _A[%j]; j--) {
                                pos = j+1
                                _A[%pos] = _A[%j]

                        }
                        pos=j+1
                        _A[%pos] = val
                }
        }
}
for (i = 0; i < length(_A); i++) {
        printout(_A[%i])
}
'''
#P.tokeniziraj(qsis)
#prog3 = P(qsis)
#prikaz(prog3)
#prog3.izvrši()
