class ApiCallPerAccountLimitedError(Exception):
    def __init__(self):
        pass

    def __str__(self):
        return "api call per account limited. It should be tried again the next day."