#!/bin/bash

i=1
c=0

# for file in `ls $1/in.([0-9])`;
# for file in `ls $1 | egrep -i in.[0-9]`;
# for file in `ls $1/in.[0-9]`;
for file in `ls $1/in.*`;
do 
    sudo isolate -t 1 -m 524288 -w 60 --box-id=0 --run $2 < $file > $1/out.$i
    
    DIFF=$(diff -w $1/"out."$i".txt" $1/out.$i)
    if [ "$DIFF" == "" ]
    then
      let "c++"
    fi
    let "i++"
done

let "i--"
# res="${c}/${i}"
res="{\"${c}\": \"${i}\"}"
echo -n $res
