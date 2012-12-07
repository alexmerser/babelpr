class Message(object):
    
    def __init__(self, medium_alias, medium_type, channel_type, channel_id, sender_id, sender_nick, body):
        self.medium_alias = medium_alias
        self.medium_type = medium_type
        self.channel_type = channel_type
        self.channel_id = channel_id
        self.sender_id = sender_id
        self.sender_nick = sender_nick
        self.body = body