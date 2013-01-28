#!/bin/bash

HOME_DIR=`dirname $0`
CUR_DIR=`pwd`
HOME_DIR=$CUR_DIR

if [[ "$1" == "" ]]; then
	workdir=$CUR_DIR;
else
	workdir=$1
fi
echo "Transforming files in dir $workdir"
cd $workdir

for ext in "*.F"; do
	#files=`echo $ext`
	files=`find . -iname 'rd_frc.F'`
	if [ "$files" != "$ext" ]; then
		for file in $files ; do

			# sed will replace a symlink with the file it self.. Really annoying.
			#sed -i "" 's/^[*cC]/!/' $file
			# Moving this functionality to fix_line_conts.php

			${HOME_DIR}/fix_line_conts.php -f $file

		done
	fi;
done

cd $CUR_DIR
