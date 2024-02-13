# -*- coding: utf-8 -*-

# Copyright (C) Fiz Vazquez vud1@sindominio.net
# Copyright (C) Arto Jantunen <viiru@iki.fi>

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

import csv
from pytrainer.gui.dialogs import save_file_chooser_dialog
from pytrainer.core.activity import Activity


class Save(object):
    CSV_HEADER = (
        "date_time_local",
        "title",
        "sports.name",
        "distance",
        "duration",
        "average",
        "maxspeed",
        "pace",
        "maxpace",
        "beats",
        "maxbeats",
        "calories",
        "upositive",
        "unegative",
        "comments",
    )

    def __init__(self, ddbb):
        self.ddbb = ddbb

    @staticmethod
    def _convert_activity(activity):
        for value in (
                activity.date_time_local,
                activity.title,
                activity.sport.name,
                activity.distance,
                activity.duration,
                activity.average,
                activity.maxspeed,
                activity.pace,
                activity.maxpace,
                activity.beats,
                activity.maxbeats,
                activity.calories,
                activity.upositive,
                activity.unegative,
                activity.comments,
        ):
            if isinstance(value, float):
                yield round(value, 2)
            else:
                yield value

    def _read_activities(self):
        with self.ddbb.sessionmaker.begin() as session:
            for activity in session.query(Activity).order_by(Activity.date_time_utc):
                yield self._convert_activity(activity)

    def run(self):
        filename = save_file_chooser_dialog(title="savecsvfile", pattern="*.csv")
        with open(filename, 'w', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, lineterminator="\n")
            # CSV Header
            writer.writerow(self.CSV_HEADER)
            writer.writerows(self._read_activities())
