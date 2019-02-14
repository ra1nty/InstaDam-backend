"""InstaDam backend custmoized exceptions
"""


class MsgException(Exception):
    """Exception that can be converted to a string.
    """

    def __init__(self, msg):
        super().__init__(msg)
        self.msg = msg

    def __str__(self):
        """Convert the exception to string representation.

        Returns:
            str: Exception message.
        """

        return self.msg
