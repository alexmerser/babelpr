from babelpr.commands import RandomDatabaseResponseCommand

class JokeCommand(RandomDatabaseResponseCommand):
    triggers = ['joke']
