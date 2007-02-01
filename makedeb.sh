#/bin/bash

version="1.2.0"

cd ..

cp -rf pytrainer2 pytrainer-$version
tar -cvzf pytrainer-$version.tar.gz --exclude=*.pyc --exclude=.svn --exclude=DOC --exclude=extensions --exclude=maps pytrainer-$version
rm -rf pytrainer-$version
mv pytrainer-$version.tar.gz /home/vud1/debian/pytrainer/

cd pytrainer

echo "se ha creado /home/vud1/debian/pytrainer/pytrainer-$version.tar.gz"

