from scorm_12 import Scorm12
from scorm_12 import Resource


course = Scorm12('Test Course 1')

res = Resource('Test SCO', 'D:\\course_source\\Playing.html', 'Test_SCO')

course.set_organization('Smart Study Gmbh')
course.add_resource(res, True)

course.export('D:\\course')