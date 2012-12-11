from babelpr.commands import RandomDatabaseResponseExplicitCommand

class SextCommand(RandomDatabaseResponseExplicitCommand):
    triggers = ['sext', 'cyb0r', 'cyber', 'cybor']
    name = "sext"
    description = "Talks dirty to you."
    syntax = "#sext"