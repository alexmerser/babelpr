from babelpr.commands import RandomDatabaseResponseCommand

class SextCommand(RandomDatabaseResponseCommand):
    triggers = ['sext', 'cyb0r', 'cyber', 'cybor']
    name = "sext"
    description = "Talks dirty to you."
    syntax = "#sext"