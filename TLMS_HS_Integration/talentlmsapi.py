"""
Contains functions that call TalentLMS API.
"""
import os
import json 
import logging

from datetime import datetime

from requests_toolbelt import sessions
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from dotenv import load_dotenv

from sqlalchemy import insert
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from models import session, Contacts, Courses, StudentCourseInstance, TimeTracking

from unix_time import return_unix_time

load_dotenv()
TALENTLMS_API = os.getenv('TALENTLMS_API')


logger = logging.getLogger()

BASE_URL = 'https://client_name.talentlms.com'
# Lets you fake a browser visit using a python requests or command wget
headers = {
    'Authorization': f'{TALENTLMS_API}'
    }

talentlms_http = sessions.BaseUrlSession(BASE_URL)
talentlms_http.mount(BASE_URL , HTTPAdapter(max_retries=Retry(backoff_factor=1)))
talentlms_http.headers.update(headers)

# Logging Function
def talentlms_log(res):
    res_log = F'"METHOD": {res.request.method}, "STATUS_CODE": {res.status_code}, "URL": {res.url}'
    try:
        if 'does not exit' in res.text:
            logger.debug(F'"LOG": "No results from TalentLMS request.", {res_log}')
            return None
        elif 'error' in res.text:
            logger.error(F'"LOG": "Unable to process TalentLMS request.", {res_log}')
            return None
        else:
            logger.debug(F'"LOG": "Successful TalentLMS request.", {res_log}')
            return res
    except ValueError:
        logger.error(F'"LOG": "Failed TalentLMS request, unknown error.", {res_log}')
        return None

# Request Class
class TalentLMS: # Make this into a Parent Class and create some child classes
    # possibly put a batch limit here

    def __init__(self):
        self.all_students = self.get_all_students()
        self.all_courses = self.get_all_courses()
        self.student_ids_to_gather = set()
        self.course_ids = set()

    # Request Helper Functions
    def get_all_courses(self):
        endpoint = 'api/v1/courses/'
        res = talentlms_http.get(endpoint)
        return talentlms_log(res)

    def get_course(self, course_id):
        endpoint = f'api/v1/courses/id:{course_id}'
        res = talentlms_http.get(endpoint)
        return talentlms_log(res)

    def get_all_students(self):
        endpoint = 'api/v1/users/'
        res = talentlms_http.get(endpoint)
        return talentlms_log(res)

    def get_student(self, user_id):
        endpoint = f'api/v1/users/id:{user_id}'
        res = talentlms_http.get(endpoint)
        return talentlms_log(res)

    # Functions to upload to SQLite1562287464000	courses
    def move_courses_to_sqlite(self):
        order_entries = []
        sql_datetime_courses = session.query(TimeTracking.last_modified_time).filter_by(obj='courses').first()[0]
        sql_datetime_instance = session.query(TimeTracking.last_modified_time).filter_by(obj='student_course_instance').first()[0]
        for course in self.all_courses.json()[30:35]:
            # Potentially error handle here to gather ids not able to be obtained
            course_datetime = return_unix_time(course['last_update_on'])
            if course_datetime > sql_datetime_courses:
                added_courses = Courses(
                                        talentlms_course_id=course['id'],
                                        course_name=course['name'],
                                        code=course['code'],
                                        start_date=return_unix_time(course['custom_field_3']), 
                                        end_date=return_unix_time(course['custom_field_4']),
                                        live_session_datetime=return_unix_time(course['custom_field_5']),
                                        assignment_due_date=return_unix_time(course['custom_field_6']),
                                        cohort_id=course['custom_field_7']
                                        )
                order_entries.append(added_courses)
            if course['custom_field_3'] is None or course['custom_field_4'] is None or (return_unix_time(course['custom_field_3']) <= sql_datetime_instance <= return_unix_time(course['custom_field_4'])):
                self.course_ids.add(course['id'])
                course_json = self.get_course(course['id']).json()
                for user in course_json['users']:
                    self.student_ids_to_gather.add(user['id'])
        session.add_all(order_entries)
        session.commit()
        

    def move_users_to_sqlite(self):
        order_entries = []
        sql_datetime_students = session.query(TimeTracking.last_modified_time).filter_by(obj='contacts').first()[0]
        for student in self.all_students.json()[:5]:
            student_datetime = student['last_updated_timestamp']
            if int(student_datetime) * 1000 > sql_datetime_students:
                added_contact = Contacts(
                                        talentlms_user_id=student['id'],
                                        firstname=student['first_name'],
                                        lastname=student['last_name'],
                                        login=student['login'],
                                        email=student['email']
                                        )
                order_entries.append(added_contact)
        session.add_all(order_entries)
        session.commit()

    def move_instances_to_sqlite(self):
        # own function if a student instance is updated and studen't doesn't. Potentially pull 
        order_entries = []
        for student_id in self.student_ids_to_gather:
            student_class_json = self.get_student(student_id).json() # try-except here
            for course in student_class_json["courses"]:
                if course['id'] in self.course_ids:
                    added_instance = StudentCourseInstance(
                                    talentlms_user_id=student_id,
                                    talentlms_course_id=course['id'],
                                    instance_name=f"{student_class_json['last_name']} {student_class_json['first_name']}: {course['name']}",
                                    firstname=student_class_json['first_name'], # will need to change properties later to add first and last name
                                    lastname=student_class_json['last_name'],
                                    course_name=course['name'],
                                    completed_on=int(course['completed_on_timestamp']) * 1000 if course['completed_on_timestamp'] is not None else course['completed_on_timestamp'],
                                    completion_status=course['completion_status'],
                                    completion_percent=course['completion_percentage'],
                                    total_time=course['total_time'],
                                    total_time_seconds=course['total_time_seconds'],
                                    last_accessed_unit_url=course['last_accessed_unit_url']
                                    )
                    order_entries.append(added_instance) 
        session.add_all(order_entries)
        session.commit()


if __name__ == '__main__':
    test = TalentLMS()
    test.move_courses_to_sqlite()
    test.move_users_to_sqlite()
    test.move_instances_to_sqlite()
    