import click
import sys
import os
sys.path.append(os.path.join(os.getcwd(), '..', '..', ))


from py_scorm.scorm_12 import *


@click.group()
#@click.option('--debug/--no-debug', default=False)
def cli():
    pass
    #click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command()  # @cli, not @click!
@click.option('-o', '--org_name', default='None')
@click.option('-n', '--name', default='course')
@click.option('-t', '--target_dir', default='.')
def create(org_name, name, target_dir):
    click.echo('Creating course')

    course = Scorm12()
    course.set_name(name)
    course.set_organization(org_name)
    course.export(target_dir, False)


@cli.command()  # @cli, not @click!
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

#     course.add_resource(module)
    # course.set_name(name)
    # course.set_organization(org_name)

    
    course.export(path, False)

if __name__ == '__main__':
    cli()

# @click.command()
# @click.option('-o', '--org_name', default='None')
# @click.option('-n', '--name', default='course')
# @click.option('-t', '--target_dir', default='.')
# @click.argument('files', nargs=-1, type=click.Path(), required=True)
# def cli(org_name, name, files, target_dir):
#     course = Scorm12(name)
#     course.set_organization(org_name)

#     module = Resource(name, files[0])
#     for f in files[0:]:
#         module.add_file(f)

#     course.add_resource(module)

#     course.export(target_dir, True)

# if __name__ == '__main__':
#     cli()


# @click.group()
# @click.option('--debug/--no-debug', default=False)
# def cli(debug):
#     click.echo(f"Debug mode is {'on' if debug else 'off'}")



# @cli.command()  
# @click.option('-m', '--module', multiple=True)
# def test(module):
#     click.echo('Syncing')
#     print(module)


# if __name__ == '__main__':
#     cli()