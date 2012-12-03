from babelpr.commands import RandomDatabaseResponseCommand

class FortuneCommand(RandomDatabaseResponseCommand):
    triggers = ['fortune']
    name = "fortune"
    description = "Tells you your fortune."
    syntax = "#fortune"