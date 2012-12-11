from babelpr.commands import RandomDatabaseResponseExplicitCommand

class FactCommand(RandomDatabaseResponseExplicitCommand):
    triggers = ['fact']
    name = "fact"
    description = "Tells you a random fact."
    syntax = "#fact"
