# -*- coding: iso-8859-1 -*-

#Copyright (C) Nathan Jones ncjones@users.sourceforge.net

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

class UpgradeContext(object):
    
    """Context used by upgrade scripts.
    
    Provides access to the application base dir."""
    
    def __init__(self, conf_dir):
        self.conf_dir = conf_dir
    
# sqlalchemy-migrate does not provide any means to inject the context object in
# to upgrade scripts so instead we provide access via this global which must be
# initialised before upgrading.
UPGRADE_CONTEXT = None
