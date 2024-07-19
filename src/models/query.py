class Query:
    def __init__(
        self,
        type: str,
        credentials: dict,
        variables: dict,
        method: str,
        parameters: dict,
        path: str,
        headers: dict,
        body: dict,
    ):
        self.type = type
        self.credentials = credentials
        self.variables = variables
        self.method = method
        self.parameters = parameters
        self.path = path
        self.headers = headers
        self.body = body
