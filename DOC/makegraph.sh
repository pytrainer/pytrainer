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

TMP_NUM=0
MEDIA_SUM=0
SUM_NUM=0
LAST_NUM=105

BOOL=1

absolute_diference() {
	if [ $tmp -lt 5 ] ; then
		if [ $tmp -gt -5 ] ; then
			BOOL=1
		else
			BOOL=2
		fi
	else
		BOOL=2
	fi
	 
	}

COUNT_NUM=1
TOTAL_NUM=1
calculate_number() {
	TMP_NUM=`echo $line | cut -d " " -f 3`
	tmp=`expr $TMP_NUM "-" $LAST_NUM`
	absolute_diference
	if [ $BOOL -eq 1 ] ; then
		let MEDIA_SUM+=$TMP_NUM
		TMP_NUM=`expr $TMP_NUM "+" 1`
		LAST_NUM=$TMP_NUM
			echo "$TMP_NUM" >> medicion.txt
		#if [ $COUNT_NUM -lt $REL ] ; then
		#	let COUNT_NUM+=1
			
		#else 
		#	value=`expr $MEDIA_SUM "/" $REL`
		#	echo "$value" >> medicion.txt
		#	let TOTAL_NUM+=1
		#	COUNT_NUM=1
		#	MEDIA_SUM=0
		#fi
	fi
	}

cat $1 | while read line; do calculate_number; done
