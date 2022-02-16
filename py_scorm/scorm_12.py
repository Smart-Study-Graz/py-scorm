from __future__ import annotations
import xml.etree.ElementTree as ET
import os
import pathlib
import shutil



_template_path = os.path.join(__file__, '..', 'data', 'scorm_12')

ET.register_namespace('', 'http://www.imsproject.org/xsd/imscp_rootv1p1p2')
ET.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')


class ResourceBase():
    _is_visible = 'true'
    _scormtype = 'sco'

    def __init__(self, name, dst_path: str | None = None):
        self._name = name
        self._identifier = 'item_' + name.replace(' ', '_')
        self._identifier_ref = 'resource_' + name.replace(' ', '_')
        self._files = []

        if dst_path is None:
            dst_path = self._identifier_ref
        self._dst_path = dst_path

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

    def _get_resource(self):
        resource = ET.Element('resource', { 
            'identifier': self._identifier_ref, 
            'type': 'webcontent',
            'adlcp:scormtype': self._scormtype,
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


class Resource(ResourceBase):
    """Resource class

    """
    def __init__(self, name: str, entry_file: str, dst_path: str | None = None):
        super().__init__(name, dst_path)

        self._dependencies = []
        self.add_file(entry_file)

    def add_dependency(self, resource: SharedResource):
        self._dependencies.append(resource)

    def _get_dependencies(self):
        return self._dependencies
    
    def _get_resource(self) -> ET.Element:
        resource = super()._get_resource()
        for dependency in self._dependencies:
            ET.SubElement(resource, 'dependency', { 'identifierref': dependency._identifier_ref })

        return resource

class SharedResource(ResourceBase):
    _scormtype = 'asset'

    def __init__(self, name: str, dst_path: str | None = None):
        super().__init__(name, dst_path)

    def _get_resource(self):
        resource = super()._get_resource()
        del resource.attrib['href']
        return resource


class Scorm12():

    def __init__(self, name: str):
        self._name = name
        self._organization_name = None
        self._resources = []

        # Create the shared resource:
        self._shared = SharedResource('common', 'common')
        self._shared.add_file(os.path.join(_template_path, 'scorm.js'))

    def set_organization(self, name: str) -> None:
        self._organization_name = name

    def add_resource(self, resource: Resource, add_shared: bool = False):
        if add_shared:
            resource.add_dependency(self._shared)
        self._resources.append(resource)

    def export(self, target_folder) -> None:
        if not os.path.exists(target_folder):
            raise OSError('Folder %s does not exist' % target_folder)

        self.__write_scorm_files(target_folder)
        self.__write_manifest(target_folder)
        self.__copy_resource_files(target_folder)

    def __write_scorm_files(self, target_folder):
        
        shutil.copy(
            os.path.join(_template_path, 'imsmd_rootv1p2p1.xsd'), 
            os.path.join(target_folder, 'imsmd_rootv1p2p1.xsd')
        )

        shutil.copy(
            os.path.join(_template_path, 'imscp_rootv1p1p2.xsd'), 
            os.path.join(target_folder, 'imscp_rootv1p1p2.xsd')
        )

        shutil.copy(
            os.path.join(_template_path, 'ims_xml.xsd'), 
            os.path.join(target_folder, 'ims_xml.xsd')
        )

        shutil.copy(
            os.path.join(_template_path, 'adlcp_rootv1p2.xsd'), 
            os.path.join(target_folder, 'adlcp_rootv1p2.xsd')
        )

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
        dependencies = set()
        for resource in self._resources:
            [dependencies.add(d) for d in resource._get_dependencies()]

            ims_organizations.find('{*}organization').append(resource._get_item())
            ims_resources.append(resource._get_resource())

        for dependency in dependencies:
            ims_resources.append(dependency._get_resource())

        ET.indent(ims_manifest, space="\t", level=0)

        ims_manifest.write(os.path.join(target_folder, 'imsmanifest.xml'))

    def __copy_resource_files(self, target_folder: str):
        for resource in self._resources:
            files = resource._get_files()
            for file in files:
                source_path = file['source']
                target_path = os.path.join(target_folder, file['target'])
                
                if not os.path.exists(os.path.dirname(target_path)):
                    os.makedirs(os.path.dirname(target_path))

                if not os.path.exists(target_path):    
                    shutil.copy(source_path, target_path)

