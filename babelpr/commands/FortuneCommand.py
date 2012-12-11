from babelpr.commands import RandomDatabaseResponseExplicitCommand

class FortuneCommand(RandomDatabaseResponseExplicitCommand):
    triggers = ['fortune']
    name = "fortune"
    description = "Tells you your fortune."
    syntax = "#fortune"