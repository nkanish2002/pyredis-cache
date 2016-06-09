class LengthError(Exception):
    def __init__(self, message, errors=None):
        super(LengthError, self).__init__(message)
        self.errors = errors


def key_generator(op_name: str, ID: int):
    """
    Generates Unique Key for Redis in the following format:
        "0000OPNAME#0000000012"
    :param op_name: OPNAME of the key
    :param ID: ID of the key
    :return: Key
    """
    if len(op_name) <= 2:
        raise LengthError("String length should be more than 2")
    return "%s#%010d" % (op_name.zfill(10).upper(), ID)


def default_passage(data):
    return data