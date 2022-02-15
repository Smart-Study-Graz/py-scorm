
import os
import xml.etree.ElementTree as ET

_template_path = os.path.join(__file__, '..', 'data', 'scorm_12')

ET.register_namespace('', 'http://www.imsproject.org/xsd/imscp_rootv1p1p2')
ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

class Scorm12():

    def __init__(self, name):
        self.name = name
        self.ims_manifest = ET.parse(os.path.join(_template_path, 'imsmanifest.xml'))


    def set_organization(self, name):
        pass

    def export(self, target_folder):

        if not os.path.exists(target_folder):
            raise OSError('Folder %s does not exist' % target_folder)

        # write manifest:
        self.ims_manifest.write(os.path.join(target_folder, 'imsmanifest.xml'))
