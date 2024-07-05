pytrainer - Free your sports
==================================================
pytrainer is a desktop application for logging and graphing sporting
activities such as running or cycling sessions. Data can be imported from GPS
devices, files or input manually. Currently pytrainer supports GPX, TCX, and
FIT files.

Installation
============
Most popular Linux distributions (Debian, Ubuntu, Fedora and so on) already
contain a pytrainer package, use that if available. If a package is not
available for your system you can install from source, see below.

Installation from source tarball
-----------------
Copy tarball file to a location where you have write and execution rights (e.g. your `$HOME` directory).

```shell
$ tar -xzf pytrainer-X.Y.Z.tar.gz
$ cd pytrainer-X.Y.Z
$ pip install ."[gui]"
$ pytrainer -i
```

Installation into a venv (for development)
------------------------------------------
This installation method is very similar to the basic source install above.
For development it makes more sense to start from a git clone instead of a
tarball, and also makes more sense to install into a virtual Python
environment.

```shell
git clone https://github.com/pytrainer/pytrainer.git
cd pytrainer
python3 -m venv .venv
.venv/bin/pip install -e ".[gui]"
.venv/bin/pytrainer -i
```

Additional packages
-------------------
For map functionality the GIR bindings for WebKit2 need to be installed.

* gpsbabel == 1.3.5 ("GoogleEarth" and "Garmin via GPSBabel 1.3.5" aka "garmin_hr")
* garmintools >= 0.10 ("Import from Garmin GPS device (via garmintools)" aka "garmintools_full" plugin)
* wordpresslib (already distributed within pytrainer tarball, wordpress extension)
* httplib2 >= 0.6.0 (wordpress extension)
* SOAPpy >= 0.11.6 (dotclear extension)
* GDAL (Elevation correction, via "gdal-python" or "python-gdal")
* perl (garmin-fit plugin)

Further Resources
-----------------
* FAQ [https://github.com/pytrainer/pytrainer/wiki/FAQ](https://github.com/pytrainer/pytrainer/wiki/FAQ)
* Distribution list: pytrainer-devel@lists.sourceforge.net
* Development guide: [https://github.com/pytrainer/pytrainer/wiki/Development-guide](https://github.com/pytrainer/pytrainer/wiki/Development-guide)
* Localization guide: [https://github.com/pytrainer/pytrainer/wiki/Localization-guide](https://github.com/pytrainer/pytrainer/wiki/Localization-guide)
* Report an Issue: [https://github.com/pytrainer/pytrainer/issues](https://github.com/pytrainer/pytrainer/issues)
