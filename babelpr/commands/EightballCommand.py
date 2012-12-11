from babelpr.commands import RandomResponseExplicitCommand

class EightballCommand(RandomResponseExplicitCommand):
    
    def __init__(self, chatbot):
        RandomResponseExplicitCommand.__init__(self, chatbot)
    
        self.triggers = ['8ball', 'eightball']
        self.name = '8ball'
        self.description = "Looks to the magic 8 ball to answer your question."
        self.syntax = "#8ball [QUESTION]"
        
        self._responses =  ["Signs point to yes",
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
