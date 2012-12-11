from babelpr.commands import RandomResponseExplicitCommand

class TittiesCommand(RandomResponseExplicitCommand):
    triggers = ['titties']
    _responses = ["Syntax error: when refering to 'the titties command', command is a verb"]
    name = "titties"
    description = "Do you really need help with them?"
    syntax = "#titties"
