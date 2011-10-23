from sqlalchemy import MetaData, Table, Column, Integer
from sqlalchemy.sql.expression import text
import logging

# record duration added in version 1.8.0

def upgrade(migrate_engine):
    add_duration_column(migrate_engine)
    populate_duration_values(migrate_engine)
    
def add_duration_column(migrate_engine):
    logging.info("Adding records.duration column")
    meta = MetaData(migrate_engine)
    records_table = Table("records", meta, autoload=True)
    duration_column = Column("duration", Integer)
    duration_column.create(records_table)
    logging.info("Created records.duration column")
    
def populate_duration_values(migrate_engine):
    logging.info("Populating records.duration column")
    records = migrate_engine.execute("select id_record, time from records where duration is null")
    for record in records:
        record_id = record["id_record"]
        record_time = record["time"]
        try:
            duration = int(record_time)
        except:
            logging.info("Error parsing time (%s) as int for record_id: %s" % (record_time, record_id))
            duration = 0
        logging.debug("setting record %s duration to %d" , record_id, duration)
        migrate_engine.execute(text("update records set duration=:duration where id_record=:record_id"), duration=duration, record_id=record_id)
    records.close()
    
# work around a migrate bug
try:
    import migrate.versioning.exceptions as ex1
    import migrate.changeset.exceptions as ex2
    ex1.MigrateDeprecationWarning = ex2.MigrateDeprecationWarning
except ImportError:
    pass
