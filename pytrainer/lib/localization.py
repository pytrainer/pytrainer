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
import logging
import os.path


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
    logging.debug("gettext_path: %s", gettext_path)

    locale.bindtextdomain("pytrainer", gettext_path)
    locale.textdomain("pytrainer")
    gettext.install("pytrainer", gettext_path)
