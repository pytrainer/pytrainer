from sqlalchemy import *
from migrate import *
from migrate.changeset.constraint import ForeignKeyConstraint
from migrate.changeset import schema

pre_meta = MetaData()
post_meta = MetaData()
records = Table('records', pre_meta,
    Column('distance', FLOAT),
    Column('maxspeed', FLOAT),
    Column('maxpace', FLOAT),
    Column('title', VARCHAR(length=200)),
    Column('id_record', INTEGER, primary_key=True),
    Column('upositive', FLOAT),
    Column('average', FLOAT),
    Column('date_time_local', VARCHAR(length=40)),
    Column('calories', INTEGER),
    Column('date_time_utc', VARCHAR(length=40)),
    Column('comments', TEXT),
    Column('pace', FLOAT),
    Column('unegative', FLOAT),
    Column('duration', INTEGER),
    Column('beats', FLOAT),
    Column('gpslog', VARCHAR(length=200)),
    Column('time', VARCHAR(length=200)),
    Column('date', DATE),
    Column('sport', INTEGER),
    Column('maxbeats', FLOAT),
)
sports = Table('sports', pre_meta,
    Column('id_sports', INTEGER, primary_key=True),
    Column('name', VARCHAR(length=100)),
    Column('weight', FLOAT),
    Column('color', CHAR(length=6)),
    Column('max_pace', INTEGER),
    Column('met', FLOAT),
)
record_equipment = Table('record_equipment', pre_meta,
    Column('record_id', INTEGER),
    Column('equipment_id', INTEGER),
    Column('id', INTEGER, primary_key=True),
)
equipment = Table('equipment', pre_meta,
    Column('life_expectancy', INTEGER),
    Column('description', TEXT(length=200)),
    Column('notes', TEXT),
    Column('active', BOOLEAN),
    Column('id', INTEGER, primary_key=True),
    Column('prior_usage', INTEGER),
)
laps = Table('laps', pre_meta,
    Column('distance', FLOAT),
    Column('end_lon', FLOAT),
    Column('lap_number', INTEGER),
    Column('start_lon', FLOAT),
    Column('id_lap', INTEGER, primary_key=True),
    Column('calories', INTEGER),
    Column('avg_hr', INTEGER),
    Column('comments', TEXT),
    Column('elapsed_time', VARCHAR(length=20)),
    Column('record', INTEGER),
    Column('intensity', VARCHAR(length=7)),
    Column('laptrigger', VARCHAR(length=9)),
    Column('max_hr', INTEGER),
    Column('end_lat', FLOAT),
    Column('start_lat', FLOAT),
    Column('max_speed', FLOAT),
)

record_sport_fkey = ForeignKeyConstraint([records.c.sport], [sports.c.id_sports])
record_equipment_equipment_fkey = ForeignKeyConstraint([record_equipment.c.equipment_id], [equipment.c.id])
record_equipment_record_fkey = ForeignKeyConstraint([record_equipment.c.record_id], [records.c.id_record])
laps_records_fkey = ForeignKeyConstraint([laps.c.record], [records.c.id_record])

def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['records'].columns['time'].drop()
    record_sport_fkey.create()
    record_equipment_equipment_fkey.create()
    record_equipment_record_fkey.create()
    laps_records_fkey.create()
    sports.c.color.alter(nullable=False)
    sports.c.name.alter(nullable=False)
    sports.c.weight.alter(nullable=False)
    record_equipment.c.equipment_id.alter(nullable=False)
    record_equipment.c.record_id.alter(nullable=False)
    laps.c.record.alter(nullable=False)
    equipment.c.description.alter(type=Unicode(100))
    equipment_description_index = Index('ix_equipment_description',
                                            equipment.c.description,
                                            unique=True)
    equipment_description_index.create()
    sport_name_index = Index('ix_sports_name',
                                 sports.c.name,
                                 unique=True)
    sport_name_index.create()
    records_sport_index = Index('ix_records_sport', records.c.sport)
    records_sport_index.create()
    record_equipment_equipment_index = Index('ix_record_equipment_equipment_id',
                                                 record_equipment.c.equipment_id)
    record_equipment_equipment_index.create()
    record_equipment_record_index = Index('ix_record_equipment_record_id',
                                              record_equipment.c.record_id)
    record_equipment_record_index.create()
    laps_record_index = Index('ix_laps_record', laps.c.record)
    laps_record_index.create()
    # We essentially rewrite the entire database multiple times,
    # so here we clean up the mess we made.
    if migrate_engine.name == 'sqlite':
        migrate_engine.execute('VACUUM')

def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['records'].columns['time'].create()
    record_sport_fkey.drop()
    record_equipment_equipment_fkey.drop()
    record_equipment_record_fkey.drop()
    laps_records_fkey.drop()
    sports.c.color.alter(nullable=True)
    sports.c.name.alter(nullable=True)
    sports.c.weight.alter(nullable=True)
    record_equipment.c.equipment_id.alter(nullable=True)
    record_equipment.c.record_id.alter(nullable=True)
    laps.c.record.alter(nullable=True)
    records_sport_index = Index('ix_records_sport', records.c.sport)
    records_sport_index.drop()
    equipment_description_index = Index('ix_equipment_description',
                                            equipment.c.description,
                                            unique=True)
    equipment_description_index.drop()
    equipment.c.description.alter(type=TEXT(200))
    sport_name_index = Index('ix_sports_name',
                                 sports.c.name,
                                 unique=True)
    sport_name_index.drop()
    record_equipment_equipment_index = Index('ix_record_equipment_equipment_id',
                                                 record_equipment.c.equipment_id)
    record_equipment_equipment_index.drop()
    record_equipment_record_index = Index('ix_record_equipment_record_id',
                                              record_equipment.c.record_id)
    record_equipment_record_index.drop()
    laps_record_index = Index('ix_laps_record', laps.c.record)
    laps_record_index.drop()
