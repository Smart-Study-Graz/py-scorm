
import xml.etree.ElementTree as ET
import os
import pathlib
import shutil

_template_path = os.path.join(__file__, '..', 'data', 'scorm_12')

ET.register_namespace('', 'http://www.imsproject.org/xsd/imscp_rootv1p1p2')
ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

class Resource():
    """Resource class

    """
    def __init__(self, name: str, entry_file: str, dst_path: str | None = None):
        self._name = name
        self._identifier = 'item_' + name.replace(' ', '_')
        self._identifier_ref = 'resource_' + name.replace(' ', '_')

        if dst_path is None:
            dst_path = self._identifier_ref
        self._dst_path = dst_path

        self._is_visible = 'true'

        self._files = [{
          'source': entry_file,
          'target': self.__relative(entry_file),
        }]

    def add_file(self, file: str):
        self._files.append({
          'source': file,
          'target': self.__relative(file),
        })

    def _get_item(self) -> ET.Element:
        item = ET.Element('item', 
            { 'identifier': self._identifier, 'identifierref': self._identifier_ref, 'isvisible': 'true' }
        )

        ET.SubElement(item, 'title').text = self._name

        return item

    def _get_resource(self) -> ET.Element:
        resource = ET.Element('resource', { 
            'identifier': self._identifier_ref, 
            'type': 'webcontent',
            'adlcp:scormtype': 'sco',
            'href': self.__relative(self._files[0]['target'])
        })

        for file in self._files:
            ET.SubElement(resource, 'file', { 'href' : pathlib.Path(file['target']).as_posix()})

        return resource

    def _get_files(self):
        return self._files

    def __relative(self, file):
        path = os.path.basename(file)
        return os.path.join(self._dst_path, path)

    


class Scorm12():

    def __init__(self, name: str):
        self._name = name
        self._organization_name = None
        self._resources = []

    def set_organization(self, name: str) -> None:
        self._organization_name = name

    def add_resource(self, resource: Resource):
        self._resources.append(resource)

    def export(self, target_folder) -> None:
        if not os.path.exists(target_folder):
            raise OSError('Folder %s does not exist' % target_folder)

        self.__write_manifest(target_folder)
        self.__copy_resource_files(target_folder)


    def __write_manifest(self, target_folder):
        ims_manifest = ET.parse(os.path.join(_template_path, 'imsmanifest.xml'))
        ims_manifest_root = ims_manifest.getroot()

        ims_organizations = ims_manifest_root.find('{*}organizations')
        ims_resources = ims_manifest_root.find('{*}resources')

        # set course title
        ims_organizations.find('{*}organization').find('{*}title').text = self._name

        # set organization title
        ims_organizations.attrib['default'] = self._organization_name
        ims_organizations.find('{*}organization').attrib['identifier'] = self._organization_name

        # add resources:
        for resource in self._resources:
            ims_organizations.find('{*}organization').append(resource._get_item())
            ims_resources.append(resource._get_resource())

        ET.indent(ims_manifest, space="\t", level=0)

        ims_manifest.write(os.path.join(target_folder, 'imsmanifest.xml'))

    def __copy_resource_files(self, target_folder: str):
        for resource in self._resources:
            files = resource._get_files()
            for file in files:
                source_path = file['source']
                target_path = os.path.join(target_folder, file['target'])
                
                os.makedirs(os.path.dirname(target_path))

                if not os.path.exists(target_path):    
                    shutil.copy(source_path, target_path)

