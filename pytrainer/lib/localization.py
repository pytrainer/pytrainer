#Copyright (C) Fiz Vazquez vud1@sindominio.net
#Copyright (C) Arto Jantunen <viiru@iki.fi>

#This program is free software; you can redistribute it and/or
#modify it under the terms of the GNU General Public License
#as published by the Free Software Foundation; either version 2
#of the License, or (at your option) any later version.

#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.

#You should have received a copy of the GNU General Public License
#along with this program; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import gettext
import locale
import os.path
import sys


def initialize_gettext():
    base_path = os.path.realpath(os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    ))
    if (
            os.path.exists(base_path + "/setup.py")
            and os.path.exists(base_path + "/locale")):
        gettext_path = os.path.join(base_path, "locale")
    else:
        gettext_path = os.path.realpath(os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "..",
            "..",
            "..",
            "share",
            "locale",
        ))
    print("gettext_path:", gettext_path)

    locale.bindtextdomain("pytrainer", gettext_path)
    locale.textdomain("pytrainer")
    if sys.version_info[0] == 2:
        gettext.install("pytrainer", gettext_path, unicode=1)
    else:
        gettext.install("pytrainer", gettext_path)

def locale_str(string):
    if sys.version_info[0] == 2:
        lcname, encoding=locale.getlocale()
        return string.decode(encoding)
    else:
        return string

def gtk_str(string):
    """On Python 2 GTK returns all strings as UTF-8 encoded str. See
https://python-gtk-3-tutorial.readthedocs.io/en/latest/unicode.html for
more details."""
    if sys.version_info[0] == 2:
        if string is None:
            return None
        else:
            return string.decode('utf-8')
    else:
        return string
