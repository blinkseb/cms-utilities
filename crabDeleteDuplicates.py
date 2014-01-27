#! /bin/bash

if [ "$#" -ne 3 ]; then
  echo "Error: crabDeleteDuplicates [dpm_folder] [folder] [analysis_type]"
  exit
fi

dpm=$1;
dataset=$2;
type=$3;

crabOutputList.py $dataset $type  > __crabDeleteDuplicatesFile__

for file in `rfls $dpm`; do
  grep $file __crabDeleteDuplicatesFile__ &> /dev/null
  if [[ "$?" -eq 1 ]]; then
    echo "rfrm $file" >> crabDeleteDuplicatesFileScript.sh
  fi
done

rm __crabDeleteDuplicatesFile__

echo "Run crabDeleteDuplicatesFileScript.sh to actually delete files"
