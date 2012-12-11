from babelpr.commands import RandomDatabaseResponseExplicitCommand

class JokeCommand(RandomDatabaseResponseExplicitCommand):
    triggers = ['joke']
    name = "joke"
    description = "Tells you a joke"
    syntax = "#jack"