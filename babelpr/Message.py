class Message(object):
    medium_alias = None
    medium_type = None
    channel_type = None
    channel_id = None
    sender = None 
    body = None
    
    def __init__(self, medium_alias, medium_type, channel_type, channel_id, sender, body):
        self.medium_alias = medium_alias
        self.medium_type = medium_type
        self.channel_type = channel_type
        self.channel_id = channel_id
        self.sender = sender
        self.body = body