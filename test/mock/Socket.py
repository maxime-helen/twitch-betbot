class Socket:
    def __init__(self, messageBuffer, onsend):
        self.index = 0
        self.messageBuffer = messageBuffer
        self.onsend = onsend

    def socket(self):
        return self

    def send(self, msg):
        self.onsend(msg)

    def connect(self, input):
        pass

    def recv(self, buffer):
        if self.index < len(self.messageBuffer):
            value = self.messageBuffer[self.index]
        else:
            value = ''
        self.index = self.index + 1
        return value
