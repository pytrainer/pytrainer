seguir=""
nota=0
deci=0
car=1
chon=0
rem=""
inversion=""
er=deci
hex=0
no=""
noe=""
while car==1:
    try:
        opcion=raw_input("""Elige la opcion que deceas realizar:\n  a) Convertir un numero Binario a Decimal.\n  b) Convertir un numero Decimal a Binario.\n  c) Convertir un numero Decimal a Hexadecimal.\nEscribe la opcion: """)
        if opcion=="a":
            bin=str(raw_input("Dame un numero Binario: "))
            try:
                print int(bin,2), "Este es tu numero en Decimal"
            except:
                print "No es binario"
            seguir=raw_input("¿Deseas Continuar?(s/n): ")
        if opcion=="b":
            try:
                num=int(raw_input("Dame un numero Decimal: "))
                while num!=0:
                    chon=num%2
                    rem+=str(chon)
		    print num
                    num/=2
                for caracter in rem:
                    inversion=caracter+inversion
                print inversion, "Este es tu numero en Binario"
            except:
                print "No es un numero decimal"
            inversion=""
            rem=""
            seguir=raw_input("¿Deseas Continuar?(s/n): ")
        if opcion=="c":
            try:
                deci=int(raw_input("Dame un numero Decimal: "))
                while deci>0:
                    hex=deci%16
                    if hex<10:
                        no=str(hex)
                    if hex==10:
                        no="A"
                    if hex==11:
                        no="B"
                    if hex==12:
                        no="C"
                    if hex==13:
                        no="D"
                    if hex==14:
                        no="E"
                    if hex==15:
                        no="F"
                    noe+=no
                    deci/=16
                for caracter in noe:
                    inversion=caracter+inversion
                print inversion,"Este es tu numero en Hexadecimal."
                inversion=""
                noe=""
            except:
                print "No es un numero decimal"
            seguir=raw_input("¿Deseas Continuar?(s/n): ")
    except:
        print "Opcion Invalida"
        seguir=raw_input("¿Deseas Continuar?(s/n): ")
    if seguir=="s":
        car=1
    elif seguir=="n":
        print "FINALIZADO"
        car=0
    else:
        print "Opcion no valida"
            
