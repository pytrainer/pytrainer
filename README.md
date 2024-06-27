pytrainer - Free your sports
==================================================
pytrainer is a desktop application for logging and graphing sporting
activities such as running or cycling sessions. Data can be
imported from GPS devices, files or input manually. Currently
pytrainer supports GPX, TCX, and FIT files.

Source Repository Structure
---------------------------
* **extensions** addons to extend pytrainer basic functionality
* **glade** user interface design
* **imports** files to parse different source formats
* **locale** localization files
* **man** source manpage
* **plugins** files to retrieve data from different sources
* **pytrainer** core files
* **schemas** schemas to support correct xml parsing
* **utils** localization shell script

Installation from source tarball (using pip)
-----------------
Copy tarball file to a location where you have write and execution rights (e.g. `/tmp` or your `$HOME` directory). Make sure executables are under your `$PATH`.

`$ tar -xzf pytrainer-X.Y.Z.tar.gz`

`$ cd pytrainer-X.Y.Z`

`$ pip install pycairo pygobject`

`$ pip install .`

`$ pytrainer -i`

Installation from source tarball (deprecated method)
-----------------
Copy tarball file to a location where you have write and execution rights (e.g. `/tmp` or your `$HOME` directory). Make sure executables are under your `$PATH`.

`$ tar -xzf pytrainer-X.Y.Z.tar.gz`

`$ cd pytrainer-X.Y.Z`

`$ sudo python setup.py install`

`$ pytrainer -i`

For more information about the process, please check [Distutils documentation] (http://docs.python.org/3.11/distutils/setupscript.html)

Further Resources
-----------------
* FAQ [https://github.com/pytrainer/pytrainer/wiki/FAQ](https://github.com/pytrainer/pytrainer/wiki/FAQ)
* Distribution list: pytrainer-devel@lists.sourceforge.net
* Development guide: [https://github.com/pytrainer/pytrainer/wiki/Development-guide](https://github.com/pytrainer/pytrainer/wiki/Development-guide)
* Localization guide: [https://github.com/pytrainer/pytrainer/wiki/Localization-guide](https://github.com/pytrainer/pytrainer/wiki/Localization-guide)
* Report an Issue: [https://github.com/pytrainer/pytrainer/issues](https://github.com/pytrainer/pytrainer/issues)
