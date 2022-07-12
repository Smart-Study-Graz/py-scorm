from __future__ import annotations
from lxml import etree
import os
import pathlib
import shutil



_template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'scorm_12')

# ET.register_namespace('', 'http://www.imsproject.org/xsd/imscp_rootv1p1p2')
etree.register_namespace('adlcp', 'http://www.adlnet.org/xsd/adlcp_rootv1p2')
# ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')


class ResourceBase():
    _is_visible = 'true'
    _scormtype = 'sco'

    def __init__(self, name, dst_path: str | None = None):
        self._name = name
        self._identifier = 'item_' + name.replace(' ', '_')
        self.identifier_ref = 'resource_' + name.replace(' ', '_')
        self._files = []

        if dst_path is None:
            dst_path = self.identifier_ref
        self._dst_path = dst_path

    def add_file(self, file: str):
        self._files.append({
          'source': file,
          'target': self.__relative(file),
        })

    def _get_item(self) -> etree.Element:
        item = etree.Element('item', 
            { 'identifier': self._identifier, 'identifierref': self.identifier_ref, 'isvisible': 'true' }
        )

        etree.SubElement(item, 'title').text = self._name

        return item

    def _get_resource(self):
        if len(self._files) == 0:
            raise Exception('Cannot use resource with zero files.')
            
        resource = etree.Element('resource', { 
            'identifier': self.identifier_ref, 
            'type': 'webcontent',
            #'adlcp:scormType': self._scormtype,
            '{http://www.adlnet.org/xsd/adlcp_rootv1p2}scormType': self._scormtype,
            'href': self._files[0]['target']
        })

        for file in self._files:
            etree.SubElement(resource, 'file', { 'href' : pathlib.Path(file['target']).as_posix()})

        return resource

    def _get_files(self):
        return self._files

    def __relative(self, file):
        path = os.path.basename(file)
        return pathlib.Path(os.path.join(self._dst_path, path)).as_posix()


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
    
    def _get_resource(self) -> etree.Element:
        resource = super()._get_resource()
        for dependency in self._dependencies:
            etree.SubElement(resource, 'dependency', { 'identifierref': dependency.identifier_ref })

        return resource

    def _get_files(self):
        files = self._files
        [files.extend(f._get_files()) for f in self._dependencies]
        return files

class SharedResource(ResourceBase):
    _scormtype = 'asset'

    def __init__(self, name: str, dst_path: str | None = None):
        super().__init__(name, dst_path)

    def _get_resource(self):
        resource = super()._get_resource()
        del resource.attrib['href']
        return resource


class Scorm12():

    def __init__(self, path: str = _template_path):
        self._name = None
        self._organization_name = None
        self._resources = []
        self._manifest = os.path.join(path, 'imsmanifest.xml')
        self._path = path

        
        self._shared = SharedResource('common', 'common')
        self._shared.add_file(os.path.join(_template_path, 'scorm.js'))

        if path != _template_path:
            ims_manifest = etree.parse(self._manifest)
            ims_manifest_root = ims_manifest.getroot()
            ims_organizations = ims_manifest_root.find('{*}organizations')
            self._name = ims_organizations.find('{*}organization').find('{*}title').text
        

        # Create the shared resource:
        #self._shared = SharedResource('common', 'common')
        #self._shared.add_file(os.path.join(_template_path, 'scorm.js'))

    # def __init__(self, name: str):
    #     self._name = name
    #     self._organization_name = None
    #     self._resources = []

    #     # Create the shared resource:
         

    def set_name(self, name: str) -> None:
        self._name = name

    def set_organization(self, name: str) -> None:
        self._organization_name = name

    def add_resource(self, resource: Resource, add_shared: bool = False):
        if add_shared:
            resource.add_dependency(self._shared)
        self._resources.append(resource)

    def write(self, target_folder) -> None:
        if not os.path.exists(target_folder):
            raise OSError('Folder %s does not exist' % target_folder)

        
        
        self.__write_scorm_files(target_folder)
        self.__write_manifest(target_folder)
        self.__copy_resource_files(target_folder)
    

    def export(self, target_folder):
        shutil.make_archive(os.path.join(target_folder, self._name), 'zip', self._path)

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
        ims_manifest = etree.parse(self._manifest)
        ims_manifest_root = ims_manifest.getroot()

        ims_organizations = ims_manifest_root.find('{*}organizations')
        ims_resources = ims_manifest_root.find('{*}resources')
        
        # set course title
        if self._name is not None:
            ims_organizations.find('{*}organization').find('{*}title').text = self._name

        # set organization title
        if self._organization_name is not None:
            ims_organizations.attrib['default'] = self._organization_name
            ims_organizations.find('{*}organization').attrib['identifier'] = self._organization_name

        # add resources:
        dependencies = set()
        for resource in self._resources:
            [dependencies.add(d) for d in resource._get_dependencies()]

            ims_organizations.find('{*}organization').append(resource._get_item())
            ims_resources.append(resource._get_resource())

        for dependency in dependencies:
            resource = dependency._get_resource()
            if len(ims_resources.xpath(f'//*[@identifier="{dependency.identifier_ref}"]')) == 0:
                ims_resources.append(resource)

        etree.indent(ims_manifest, space="\t", level=0)

        manifest_target = os.path.join(target_folder, 'imsmanifest.xml')
        if os.path.exists(manifest_target):
            os.remove(manifest_target)
        ims_manifest.write(manifest_target, xml_declaration=True)

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
