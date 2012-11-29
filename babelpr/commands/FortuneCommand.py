from babelpr.commands import RandomDatabaseResponseCommand

class FortuneCommand(RandomDatabaseResponseCommand):
    triggers = ['fortune']
