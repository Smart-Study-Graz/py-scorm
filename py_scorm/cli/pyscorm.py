import click
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..', '..', ))


from py_scorm.scorm_12 import *


@click.group()
def cli():
    pass

@cli.command()
@click.option('-o', '--org_name', default='None')
@click.option('-n', '--name', default='course')
@click.option('-t', '--target_dir', default='.')
def create(org_name, name, target_dir):
    click.echo('Creating course')

    course = Scorm12()
    course.set_name(name)
    course.set_organization(org_name)
    course.write(target_dir)


@cli.command()
@click.option('-p', '--path', default='.')
@click.option('-t', '--target_dir', default=None)
@click.option('-n', '--name', required=True)
@click.argument('files', nargs=-1, type=click.Path(), required=True)
def append(path, target_dir, name, files):
    click.echo('Appending resource to course')

    if target_dir is None:
        target_dir = path

    course = Scorm12(path)

    module = Resource(name, files[0])
    for f in files[1:]:
        module.add_file(f)

    course.add_resource(module, True)
    
    course.write(target_dir)

@cli.command()
@click.option('-p', '--path', default='.')
@click.option('-t', '--target_dir', default=None)
def export(path, target_dir):
    click.echo('Appending resource to course')

    if target_dir is None:
        target_dir = path

    course = Scorm12(path)   
    course.export(target_dir)

if __name__ == '__main__':
    cli()
