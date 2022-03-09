from operator import mod
import click


from py_scorm.scorm_12 import *


@click.command()
@click.option('-o', '--org_name', default='None')
@click.option('-n', '--name', default='course')
@click.option('-t', '--target_dir', default='.')
@click.argument('files', nargs=-1, type=click.Path(), required=True)
def cli(org_name, name, files, target_dir):
    course = Scorm12(name)
    course.set_organization(org_name)

    module = Resource(name, files[0])
    for f in files[0:]:
        module.add_file(f)

    course.add_resource(module)

    course.export(target_dir, True)

if __name__ == '__main__':
    cli()