from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from dyte_project.settings import (
    elasticsearch_instance,
    pika_parameters,
    LOG_MESSAGES_QUEUE_NAME,
    ELASTICSEARCH_INDEX_NAME
)
from enum import Enum
import pika
import json
class QueryKeywords(Enum):
    EQUALS = 'match'
    CONTAINS = 'wildcard'
    RANGE = 'range'
    TERM = 'term'
    KEYWORD = 'keyword'

DEFAULT_SIZE = 10000
class FetchLogs(APIView):
    schema = None

    def query_builder(self, key, value, operation, size):
        query = {}
        if key == "metadata.parentResourceId":
            search_key = f'{key}.{QueryKeywords.KEYWORD.value}'
            query = {
                "query": {
                    QueryKeywords.TERM.value : {
                        search_key: {
                            "value": value
                        }
                    }
                }
            }
        else:
            if operation == "equals":
                query = {
                    "size": size,
                    "query": {
                        QueryKeywords.EQUALS.value: {
                            key: value
                        }
                    }
                }
            elif operation == "contains":
                query = {
                    "size": size,
                    "query": {
                        QueryKeywords.CONTAINS.value: {
                            key: f"*{value}*"
                        }
                    }
                }
            elif operation == "range":
                query = {
                    "size": size,
                    "query": {
                        QueryKeywords.RANGE.value : {
                        key: {
                            "gte": value['lower_range'],
                            "lte": value['upper_range'],
                            "format": "yyyy-MM-dd'T'HH:mm:ss'Z'"
                        }
                        }
                    }
                }
            else:
                raise Exception
        return query
    
    def query_processor(self, query, index_name):
        query_results = []
        result = elasticsearch_instance.search(index=index_name, body=query)
        hits = result['hits']['hits']
        for hit in hits:
            query_results.append(hit['_source'])
        return query_results


    def post(self, request):
        request_payload = request.data
        key = request_payload['key']
        value = request_payload['value']
        operation = request_payload['operation']
        try:
            if not elasticsearch_instance.indices.exists(index=ELASTICSEARCH_INDEX_NAME):
                return Response(
                    {
                        "status": True,
                        "results": []
                    },
                    status=200
                )
            size = request_payload.get('size', DEFAULT_SIZE)
            search_query = self.query_builder(key, value, operation, size)
            search_results = self.query_processor(search_query, ELASTICSEARCH_INDEX_NAME)
            return Response(
                {
                    "status": True,
                    "results": search_results
                },
                status=200
            )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "something went wrong",
                },
                status=500
            )

class IngestLogs(APIView):
    schema = None

    def post(self, request):
        try:
            request_payload = request.data
            connection = pika.BlockingConnection(pika_parameters)
            channel = connection.channel()
            channel.queue_declare(LOG_MESSAGES_QUEUE_NAME)
            channel.basic_publish(
                '',
                LOG_MESSAGES_QUEUE_NAME,
                json.dumps(request_payload),
                pika.BasicProperties(
                    content_type='text/plain',
                    delivery_mode=pika.DeliveryMode.Transient
                )
            )
            connection.close()
            return Response(
                    {
                        "status": True,
                        "message": "Data updated"
                    },
                    status=200
                )
        except Exception as e:
            return Response(
                {
                    "status": False,
                    "message": "something went wrong",
                },
                status=500
            )

