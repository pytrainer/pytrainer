#!/usr/bin/env python

#Copyright (C) Kevin Dwyer kevin@pheared.net

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

import os

# Kind of lame to shell out for this....
f = os.popen("zenity --file-selection --title 'Choose a GPX file to import'")

file_name = f.read().strip()

rv = f.close()
if rv:
    if os.WEXITSTATUS(rv) != 0:
        raise Exception()

print file_name
