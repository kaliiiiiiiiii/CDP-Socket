class CDPError(Exception):
    def __init__(self, error):
        self.code = error["code"]
        self.message = error["message"]
        super().__init__(error)


class SocketExcitedError(Exception):
    pass
