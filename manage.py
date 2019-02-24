"""Main entry-point for instadam backend server.

Commands:
    start           Start the server
    initdb          Initialize the database
    cleartable      Clear all the table content
    cleardb         Clear the database

Usage:
    manage.py start [--mode]
    manage.py initdb [--mode]
    manage.py cleardb [--mode]
    manage.py cleartable [--mode]

Options:
    --mode          Start the api on specific mode, one of
                    production, development, testing
                    [default : production]

"""
import click
from instadam.app import create_app, db


@click.group()
def cli():
    pass


@cli.command()
@click.option('--mode', default='development', help='production/development')
def start(mode):
    app = create_app(mode)
    if mode == 'development':
        with app.app_context():
            db.create_all()  # init in-memory Sqlite
    app.run(host='127.0.0.1', port=5432)


@cli.command()
@click.option('--mode', default='development', help='production/development')
def initdb(mode):
    app = create_app(mode)
    with app.app_context():
        db.create_all()


@cli.command()
@click.option('--mode', default='development', help='production/development')
def cleartable(mode):
    app = create_app(mode)
    with app.app_context():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
            print('Clear table %s' % table)
            db.session.execute(table.delete())
            db.session.commit()


@cli.command()
@click.option('--mode', default='development', help='production/development')
def cleardb(mode):
    app = create_app(mode)
    with app.app_context():
        db.reflect()
        db.drop_all()


if __name__ == '__main__':
    cli()  # Execute the function specified by the user.
