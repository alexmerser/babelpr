from babelpr.commands import RandomResponseCommand

class EightballCommand(RandomResponseCommand):
    triggers = ['8ball', 'eightball']
    name = '8ball'
    description = "Looks to the magic 8 ball to answer your question."
    syntax = "#8ball [QUESTION]"
    
    _responses =  ["Signs point to yes",
             "Yes",
             "Reply hazy, try again",
             "Without a doubt",
             "My sources say no",
             "As I see it, yes",
             "You may rely on it",
             "Concentrate and ask again",
             "Outlook not so good",
             #"It is decidedly so",
             "It is known",
             "Better not tell you now",
             "Very doubtful",
             "Yes - definitely",
             #"It is certain",
             "It is known",
             "Cannot predict now",
             "Most likely",
             "Ask again later",
             "My reply is no",
             "Outlook good",
             "Don't count on it"
             ]
