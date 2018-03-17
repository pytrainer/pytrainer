from pytrainer.lib import gpx
from pytrainer.upgrade.context import UPGRADE_CONTEXT
from sqlalchemy.sql.expression import text
import logging
import os.path
import sqlalchemy

#       lap info added in version 1.9.0
def upgrade(migrate_engine=None):
    if migrate_engine is None:
        # sqlalchemy-migrate 0.5.4 does not provide migrate engine to upgrade scripts
        migrate_engine = sqlalchemy.create_engine(UPGRADE_CONTEXT.db_url)
    logging.info("Populating laps details columns")
    resultset = migrate_engine.execute(text("select distinct record from laps where intensity is null"))
    record_ids = []
    for row in resultset:
        record_ids.append(row["record"])
    resultset.close()
    for record_id in record_ids:
        gpx_file = UPGRADE_CONTEXT.conf_dir + "/gpx/{0}.gpx".format(record_id)
        if os.path.isfile(gpx_file):
            gpx_record = gpx.Gpx(filename=gpx_file)
            populate_laps_from_gpx(migrate_engine, record_id, gpx_record)

def populate_laps_from_gpx(migrate_engine, record_id, gpx_record):
    resultset = migrate_engine.execute(text("select id_lap from laps where record=:record_id" ), record_id=record_id)
    lap_ids = []
    for row in resultset:
        lap_ids.append(row["id_lap"])
    resultset.close()
    if(len(lap_ids) > 0):
        logging.info("Populating laps from GPX for record %s" , record_id)
    for lap_id, gpx_lap in zip(lap_ids, gpx_record.getLaps()):
        populate_lap_from_gpx(migrate_engine, lap_id, gpx_lap)

def populate_lap_from_gpx(migrate_engine, lap_id, gpx_lap):
    logging.info("Populating lap details from GPX for lap %s" , lap_id)
    migrate_engine.execute(text("""update laps set
                                    intensity=:intensity,
                                    avg_hr=:avg_heart_rate,
                                    max_hr=:max_heart_rate,
                                    max_speed=:max_speed,
                                    laptrigger=:lap_trigger
                                    where id_lap=:lap_id"""),
                                    intensity=gpx_lap[7],
                                    avg_heart_rate=gpx_lap[8],
                                    max_heart_rate=gpx_lap[9],
                                    max_speed=float(gpx_lap[10]),
                                    lap_trigger=gpx_lap[11],
                                    lap_id=lap_id)

# work around a migrate bug
try:
    import migrate.versioning.exceptions as ex1
    import migrate.changeset.exceptions as ex2
    ex1.MigrateDeprecationWarning = ex2.MigrateDeprecationWarning
except:
    pass
