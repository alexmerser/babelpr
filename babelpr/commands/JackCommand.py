from babelpr.commands import RandomDatabaseResponseCommand

class JackCommand(RandomDatabaseResponseCommand):
    triggers = ['jack']
    name = "jack"
    description = "Tells you a random deep thought."
    syntax = "#jack"