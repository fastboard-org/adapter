class Query:
    def __init__(self, type: str, credentials: dict, variables: dict, parameters: dict):
        self.type = type
        self.credentials = credentials
        self.variables = variables
        self.parameters = parameters


class ApiQuery(Query):
    def __init__(
        self,
        type: str,
        variables: dict,
        parameters: dict,
        method: str,
        credentials: dict,
        path: str,
        headers: dict,
        body: dict,
    ):
        super().__init__(type, credentials, variables, parameters)
        self.method = method
        self.path = path
        self.headers = headers
        self.body = body


class MongoQuery(Query):
    def __init__(
        self,
        type: str,
        credentials: dict,
        variables: dict,
        parameters: dict,
        method: str,
        collection: str,
        filter_body: dict,
        update_body: dict,
    ):
        super().__init__(type, credentials, variables, parameters)
        self.method = method
        self.collection = collection
        self.filter_body = filter_body
        self.update_body = update_body
