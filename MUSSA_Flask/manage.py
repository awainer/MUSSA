"""This file sets up a command line manager.

Use "python manage.py" for a list of available commands.
Use "python manage.py runserver" to start the development web server on localhost:5000.
Use "python manage.py runserver --help" for additional runserver options.
"""

from flask_migrate import MigrateCommand
from flask_script import Manager, commands

from app import create_app
from app.commands import InitDbCommand

# Setup Flask-Script with command line commands
manager = Manager(create_app)
manager.add_command('db', MigrateCommand)
manager.add_command('init_db', InitDbCommand)
manager.add_command('runserver', commands.Server(host="0.0.0.0", port=None, threaded=True))



if __name__ == "__main__":
    # python manage.py                      # shows available commands
    # python manage.py runserver --help     # shows available runserver options
    manager.run()
