#!/bin/sh
if [ "$#" -ne 1 ]; then
	echo "SCRIPT >> Illegal number of parameters"
	exit 1
fi
if [ ! -f "$1" ]; then
	echo "SCRIPT >> That is not an existing file"
	exit 2
fi

echo "SCRIPT >> Creating transitional files"
cp dz1new.py tmp.py
echo >> tmp.py
echo "ulaz='''" >> tmp.py
cat $1 >> tmp.py
echo "'''" >> tmp.py
echo >> tmp.py
echo "prog = P(ulaz); prog.izvrši()" >> tmp.py
echo "SCRIPT >> Running program"
printf "\n\n"
python tmp.py
printf "\n\n"
echo "SCRIPT >> Cleaning up"
rm -f tmp.py
