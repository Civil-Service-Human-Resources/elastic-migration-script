import requests

class ElasticClient():

    def __init__(self, elastic_url, elastic_username, elastic_pw) -> None:
        self.elastic_url = elastic_url
        self.elastic_username = elastic_username
        self.elastic_pw = elastic_pw

    def _get_auth(self):
        return (self.elastic_username, self.elastic_pw)

    def get_all_docs(self, doc_index):
        response = requests.get(
            f"{self.elastic_url}/{doc_index}/_search",
            {"size": 10000},
            auth=self._get_auth()
        )
        data = response.json()
        return {
            "total": data['hits']['total'],
            "content": data['hits']['hits']
        }

    def insert_doc(self, doc_index, doc, id):
        response = requests.put(
            f"{self.elastic_url}/{doc_index}/_doc/{id}",
            json=doc,
            auth=self._get_auth()
        )
        if (response.status_code >= 400):
            print(f"Request to add doc {id} failed, response: {response.json()}")
            response.raise_for_status()
        else:
            print(f"Document {id} added")