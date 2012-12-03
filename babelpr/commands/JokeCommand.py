from babelpr.commands import RandomDatabaseResponseCommand

class JokeCommand(RandomDatabaseResponseCommand):
    triggers = ['joke']
    name = "joke"
    description = "Tells you a joke"
    syntax = "#jack"