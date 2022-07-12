# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker


# class RunSQLite:
#     def __init__(self, db_file):
# engine = create_engine("sqlite:///altaclaro.db", future=True)
# Session = sessionmaker(bind=engine, future=True) 
# # The purpose of sessionmaker is to provide a factory for Session objects with a fixed configuration. 
# # As it is typical that an application will have an Engine object in module scope, the sessionmaker 
# # can provide a factory for Session objects that are against this engine

#     def create_connection(self):
#     """Create a database connection to the SQLite database
#     :return: Connection Object or NO

from sqlalchemy import create_engine, ForeignKey, Column, Date, Integer, Text, PrimaryKeyConstraint, CheckConstraint, text, MetaData
from sqlalchemy.orm import relationship, backref, sessionmaker, deferred
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import exists
import json
import time


# If echo is True, the Engine will log all statements as well as a repr() of their parameter lists to the default 
# log handler, which defaults to sys.stdout for output. If set to the string "debug", result rows will be 
# printed to the standard output as well. The echo attribute of Engine can be modified at any time to turn 
#logging on and off; direct control of logging is also available using the standard Python logging module.
# Engine is the homebase for the actual db. Program that performs a core or essential function for
engine = create_engine("sqlite:///client_name.db", echo=True) 
# imports the declarative_base object, which connects the database engine to the SQLAlchemy functionality of 
# the models
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()
# metadata = MetaData(bind=engine)

class Contacts(Base):

    __tablename__ = "contacts"

    talentlms_user_id  = Column(Integer, primary_key=True)
    firstname = Column(Text)
    lastname = Column(Text)
    login = Column(Text) 
    email = Column(Text)
    most_recent_linkedin_badge = Column(Text)

    # Relationships
    student_course_instances = relationship("StudentCourseInstance", backref=backref("contacts"))
    contact_hs_histories = relationship("ContactHSHistory", backref=backref("contact_hs_history"), uselist=False)


    # def __init__(self, name):

    #     self.name = name    

class Courses(Base):

    __tablename__ = "courses"

    talentlms_course_id = Column(Integer, primary_key=True)
    course_name = Column(Text)
    code = Column(Text)
    start_date = Column(Integer) 
    end_date = Column(Integer) 
    live_session_datetime = Column(Integer) 
    assignment_due_date = Column(Integer) 
    cohort_id = Column(Text)

    # Relationships
    student_course_instances = relationship("StudentCourseInstance", backref=backref("courses"))
    course_hs_histories = relationship("CourseHSHistory", backref=backref("course_hs_history"), uselist=False)

class StudentCourseInstance(Base):

    __tablename__ = "student_course_instance"

    talentlms_user_id = Column(Integer, ForeignKey('contacts.talentlms_user_id'), primary_key=True) 
    talentlms_course_id = Column(Integer, ForeignKey('courses.talentlms_course_id'), primary_key=True)
    firstname = Column(Text)
    lastname = Column(Text)
    class_name = Column(Text)
    completed_on = Column(Integer) 
    completion_status = Column(Text)
    completion_percent = Column(Integer) 
    total_time = Column(Text)
    total_time_seconds = Column(Integer) 
    last_accessed_unit_url = Column(Text)
    linkedin_badge = Column(Text)
    # __table_args__ = (PrimaryKeyConstraint(talentlms_user_id, talentlms_course_id, name='user_course_compound_id'),)
    # Relationships
    # student_course_instance_histories = relationship("StudentCourseInstanceHistory", backref=backref("student_course_instance"))


class ContactHSHistory(Base):
    __tablename__ = "contact_hs_history"

    talentlms_user_id = Column(Integer, ForeignKey('contacts.talentlms_user_id'), primary_key=True) 
    hs_contact_id = Column(Integer, unique=True)


class CourseHSHistory(Base):
    __tablename__ = "course_hs_history"

    talentlms_course_id = Column(Integer, ForeignKey('courses.talentlms_course_id'), primary_key=True) 
    hs_course_id = Column(Integer, unique=True)


class StudentCourseInstanceHistory(Base):
    __tablename__ = "student_course_instance_history"

    talentlms_user_id = Column(Integer, ForeignKey('student_course_instance.talentlms_user_id')) 
    talentlms_course_id = Column(Integer, ForeignKey('student_course_instance.talentlms_course_id')) 
    hs_association_id = Column(Integer, unique=True)
    __table_args__ = (PrimaryKeyConstraint(talentlms_user_id, talentlms_course_id, name='user_course_compound_id'),)

class TimeTracking(Base):
    __tablename__ = 'time_tracking'

    last_modified_time = Column(Integer)
    obj = Column(Text, primary_key=True)
    __table_args__ = (CheckConstraint(obj.in_(['contacts', 'courses', 'student_course_instance'])),)


def get_sql_datetime(datetime_sql_file):
    with engine.connect() as con:
        with open(datetime_sql_file) as file:
            query = text(file.read())
            results = con.execute(query)
            return results.first()[0]

def create_payload(outer_join_file):
    with engine.connect() as con:
        with open(outer_join_file) as file:
            query = text(file.read())
            results = con.execute(query)
            return {'inputs': [{'properties': dict(result)} for result in results]}

def update_payload(inner_join_file, obj):
    payload = {'inputs': []}
    with engine.connect() as con:
        with open(inner_join_file) as file:
            query = text(file.read())
            results = con.execute(query)
            for result in results:
                record = dict(result)
                print(record)
                if obj == 'contacts':
                    payload['inputs'].append({'id': record.pop('hs_contact_id'), 'properties': record})
                elif obj == 'courses':
                    payload['inputs'].append({'id': record.pop('hs_course_id'), 'properties': record})
    print(payload)
    return payload

def gather_batch_hs_id(objectType, res):
    print(res.json())
    for r in res.json()['results']:
        if objectType == 'contacts':
            session.add(ContactHSHistory(hs_contact_id=r['id'], talentlms_user_id=r['properties']['talentlms_user_id']))
        elif objectType == 'courses':
            session.add(CourseHSHistory(hs_course_id=r['id'], talentlms_course_id=r['properties']['talentlms_course_id']))
    session.commit()

def gather_unit_hs_id(objectType, res):
    r = res.json()
    if objectType == 'contacts':
        session.add(ContactHSHistory(hs_contact_id=r['id'], talentlms_user_id=r['properties']['talentlms_user_id']))
    elif objectType == 'courses':
            session.add(CourseHSHistory(hs_course_id=r['id'], talentlms_course_id=r['properties']['talentlms_course_id']))
    session.commit()

def update_time_tracking(objectType):
    session.query(TimeTracking).filter(TimeTracking.obj==objectType).update({'last_modified_time':int(time.time()*1000)})
    session.commit()

        
Base.metadata.create_all(engine)
