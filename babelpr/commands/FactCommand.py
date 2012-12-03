from babelpr.commands import RandomDatabaseResponseCommand

class FactCommand(RandomDatabaseResponseCommand):
    triggers = ['fact']
    name = "fact"
    description = "Tells you a random fact."
    syntax = "#fact"
