import click



@click.group('power')
def power():
    """Commands for power mananegement"""

@power.command('up')
def up():
    """ Powering Up """
    print("Powering Up")

@power.command('down')
def down():
    """ Powering Down """
    print("Powering Down")


if __name__ == '__main__':
    print("Cannot run this file directly")