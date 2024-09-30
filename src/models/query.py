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
        credentials: dict,
        variables: dict,
        parameters: dict,
        method: str,
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


class VectorSearchQuery(Query):
    def __init__(
        self,
        type: str,
        credentials: dict,
        variables: dict,
        parameters: dict,
        method: str,
        collection: str,
        index_created: bool,
        embeddings_created: bool,
        query: str,
        limit: int,
        num_candidates: int,
    ):
        super().__init__(type, credentials, variables, parameters)
        self.method = method
        self.collection = collection
        self.index_created = index_created
        self.embeddings_created = embeddings_created
        self.query = query
        self.limit = limit
        self.num_candidates = num_candidates
