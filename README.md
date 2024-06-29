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

`$ tar -xzf pytrainer-X.Y.Z.tar.gz`

`$ cd pytrainer-X.Y.Z`

`$ pip install ."[gui]"`

`$ pytrainer -i`

Installation into a venv (for development)
------------------------------------------
This installation method is very similar to the basic source install above.
For development it makes more sense to start from a git clone instead of a
tarball, and also makes more sense to install into a virtual Python
environment.

`git clone https://github.com/pytrainer/pytrainer.git`

`cd pytrainer`

`python3 -m venv .venv`

`.venv/bin/pip install -e ".[gui]"`

`.venv/bin/pytrainer -i`

Further Resources
-----------------
* FAQ [https://github.com/pytrainer/pytrainer/wiki/FAQ](https://github.com/pytrainer/pytrainer/wiki/FAQ)
* Distribution list: pytrainer-devel@lists.sourceforge.net
* Development guide: [https://github.com/pytrainer/pytrainer/wiki/Development-guide](https://github.com/pytrainer/pytrainer/wiki/Development-guide)
* Localization guide: [https://github.com/pytrainer/pytrainer/wiki/Localization-guide](https://github.com/pytrainer/pytrainer/wiki/Localization-guide)
* Report an Issue: [https://github.com/pytrainer/pytrainer/issues](https://github.com/pytrainer/pytrainer/issues)
