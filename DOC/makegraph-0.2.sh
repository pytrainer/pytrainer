#!/bin/sh

PIXELES_w=800
PIXELES_h=200

#Primero calculamos el numero de lineas del archivo:
NUMLINES=`wc -l $1 | cut -d " " -f "1"`
echo "el numero de lines es $NUMLINES"
echo "-------------------------------"

#Ahora calculamos la relacion puntos-pixeles
REL=`expr $NUMLINES "/" $PIXELES_w`
echo "cada $REL lineas dibujamos un punto"
echo "-------------------------------"

#Empezamos a hacer los calculos
echo "empezamos a calcular, esto puede llevar unos segundos"

TMP_NUM=16
LAST_NUM=43
LAST_LAT=-3
LAST_LON=0


BOOL=1

absolute_diference() {
	if [ $tmp -lt 50 ] ; then
		if [ $tmp -gt -50 ] ; then
			BOOL=1
		else
			BOOL=2
		fi
	else
		BOOL=2
	fi
	 
	}

INICIO=0
TOTAL_DIST=0
calculate_number() {
	TMP_NUM=`echo $line | cut -d " " -f 3`
	TMP_LAT=`echo $line | cut -d " " -f 1`
	TMP_LON=`echo $line | cut -d " " -f 2`
	tmp=`expr $TMP_NUM "-" $LAST_NUM`
	absolute_diference
	if [ $BOOL -eq 1 ] ; then
		echo "registro: $TMP_NUM $TMP_LAT $TMP_LON"
		TMP_NUM=`expr $TMP_NUM "+" 1`
		TMP_LAT=`wcalc $TMP_LAT*0.01745329252 | cut -d "=" -f 2`
		TMP_LON=`wcalc $TMP_LON*0.01745329252 | cut -d "=" -f 2`
		if [ $INICIO -eq 1 ] ; then
			DIST=`wcalc "acos((sin($LAST_LAT)*sin($TMP_LAT))+(cos($LAST_LAT)*cos($TMP_LAT)*cos($TMP_LON-$LAST_LON)))*111.302" | cut -d "=" -f 2`
			if [ $DIST == 0 ]; then
				VAR="NULL"
			else
				if [ $DIST != -0 ]; then
					if [ $DIST != " " ]; then
						TOTAL_DIST=`wcalc "$TOTAL_DIST+$DIST" | cut -d "=" -f 2`
						echo $TOTAL_DIST
						echo "$TOTAL_DIST $TMP_NUM" >> medicion.txt
					fi
				fi
			fi
		fi
		LAST_NUM=$TMP_NUM
		LAST_LAT=$TMP_LAT
		LAST_LON=$TMP_LON
		INICIO=1
	fi
	}

cat $1 | while read line; do calculate_number; done

echo "hemos acabado de calcular, el fichero es medicion.txt"
