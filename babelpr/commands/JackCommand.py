from babelpr.commands import RandomDatabaseResponseExplicitCommand

class JackCommand(RandomDatabaseResponseExplicitCommand):
    triggers = ['jack']
    name = "jack"
    description = "Tells you a random deep thought."
    syntax = "#jack"