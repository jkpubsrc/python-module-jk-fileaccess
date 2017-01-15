DIRNAME=testA



cd $DIRNAME
find . -type f -printf "%s\t%T@\t%p\n" | gzip > ../$DIRNAME.index.gz


