from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Standardised pagination used across the entire API.

    Query params:
      ?page=<n>          – page number (default 1)
      ?page_size=<n>     – override default page size (max 100)
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response(
            {
                "pagination": {
                    "count": self.page.paginator.count,
                    "total_pages": self.page.paginator.num_pages,
                    "current_page": self.page.number,
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "results": data,
            }
        )

    def get_paginated_response_schema(self, schema):
        return {
            "type": "object",
            "properties": {
                "pagination": {
                    "type": "object",
                    "properties": {
                        "count":       {"type": "integer"},
                        "total_pages": {"type": "integer"},
                        "current_page":{"type": "integer"},
                        "next":        {"type": "string", "nullable": True},
                        "previous":    {"type": "string", "nullable": True},
                    },
                },
                "results": schema,
            },
        }
