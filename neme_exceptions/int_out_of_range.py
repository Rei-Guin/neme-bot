from neme_exceptions.neme_exception import NemeException


# Number out of range exception
class IntOutOfRange(NemeException):
    def __init__(self, value, msg):
        super().__init__(msg)
        self.value = value
        self.msg = msg

    def __str__(self):
        return f'**{self.value}** {super().__str__()}'
