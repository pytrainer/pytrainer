[pytrainer](http://sourceforge.net/projects/pytrainer/) - Free your sports
==================================================

Source Repository Structure
---------------------------
* **bin** pytrainer executable *python script* files
* **extensions** addons to extend pytrainer basic functionality
* **glade** user interface design
* **import** files to parse different source formats
* **locale** localization files
* **man** source manpage
* **plugins** files to retrieve data from different sources
* **pytrainer** core files
* **schemas** schemas to support correct xml parsing
* **utils** localization shell script


Installation from source tarball
-----------------
Copy tarball file to a location where you have write and execution rights (e.g. `/tmp` or your `$HOME` directory). Make sure executables are under your `$PATH`.

    $ tar -xzf pytrainer-X.Y.Z.tar.gz
    $ cd pytrainer-X.Y.Z
    $ sudo python setup.py install
    $ pytrainer -i

For more information about the process, please check [Distutils documentation] (http://docs.python.org/distutils/setupscript.html)

Further Resources
-----------------
* FAQ [http://sourceforge.net/apps/trac/pytrainer/wiki/faq] (http://sourceforge.net/apps/trac/pytrainer/wiki/faq)
* Distribution list: pytrainer-devel@lists.sourceforge.net
* Development guide: [http://sourceforge.net/apps/trac/pytrainer/wiki/DevelopmentGuide](http://sourceforge.net/apps/trac/pytrainer/wiki/DevelopmentGuide)
* Localization guide: [http://sourceforge.net/apps/trac/pytrainer/wiki/LocalizationGuide] (http://sourceforge.net/apps/trac/pytrainer/wiki/LocalizationGuide)
* Report an Issue: [https://github.com/pytrainer/pytrainer/issues](https://github.com/pytrainer/pytrainer/issues)

