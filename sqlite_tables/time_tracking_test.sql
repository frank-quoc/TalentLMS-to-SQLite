-- SQLite
-- INSERT INTO altaclaro (last_modified_time, obj)
-- VALUES 
--     (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime'), 'contacts'),
--     (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime'), 'companies'),
--     (strftime('%Y-%m-%d %H:%M:%S','now', 'localtime'), 'student_course_instance');

-- SQLite
-- INSERT INTO time_tracking (last_modified_time, obj)
-- VALUES 
--     (STRFTIME('%s'), 'contacts'),
--     (STRFTIME('%s'), 'courses'),
--     (STRFTIME('%s'), 'student_course_instance')

INSERT INTO time_tracking (last_modified_time, obj)
VALUES 
    (1562287464000, 'contacts'),
    (1562287464000, 'courses'),
    (1562287464000, 'student_course_instance');