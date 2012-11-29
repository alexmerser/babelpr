class Message(object):
    medium = None
    channel_type = None
    channel_id = None
    sender = None 
    body = None
    
    def __init__(self, medium, channel_type, channel_id, sender, body):
        self.medium = medium
        self.channel_type = channel_type
        self.channel_id = channel_id
        self.sender = sender
        self.body = body