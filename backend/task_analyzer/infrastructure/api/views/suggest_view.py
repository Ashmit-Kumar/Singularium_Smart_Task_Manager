"""
HTTP view adapter for suggest endpoint.

Purpose:
- return top suggested tasks to work on today
- uses the same request shape for optional config overrides but only acts on cached
  or immediate payload provided by client

Inputs:
- GET request may include query param 'top_n' and optional JSON body with tasks
- If no body is provided, view will attempt to use last-analyzed tasks kept in-memory

Outputs:
- list of suggested tasks with short reasons and metadata
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import JSONParser

from infrastructure.api.serializers.task_serializer import SingleTaskSerializer
from application.services.suggest_tasks_service import suggest_tasks_service

# simple in-memory cache seeded by analyze endpoint
_LAST_ANALYZED_PAYLOAD = None


class SuggestView(APIView):
    """
    GET handler to produce suggested tasks.

    Behavior:
    - If client provides JSON list of tasks in the request body, analyze those
      and return top suggestions
    - Otherwise, if analyze endpoint was called earlier during runtime, use the
      cached payload to compute suggestions
    - Accepts optional query parameter 'top_n' to control how many suggestions to
      return. Defaults to three.
    """

    parser_classes = [JSONParser]

    def get(self, request):
        global _LAST_ANALYZED_PAYLOAD

        try:
            # try to read JSON body if present
            body = request.data or {}
            tasks_payload = body.get("tasks") if isinstance(body, dict) else None

            if not tasks_payload and _LAST_ANALYZED_PAYLOAD:
                tasks_payload = _LAST_ANALYZED_PAYLOAD

            if not tasks_payload:
                return Response({"results": [], "message": "no_tasks_provided"}, status=status.HTTP_200_OK)

            # read top_n from query params; if missing fall back to default
            try:
                top_n = int(request.query_params.get("top_n") or 3)
            except Exception:
                top_n = 3

            suggestions = suggest_tasks_service(tasks_payload, top_n=top_n)
            return Response({"results": suggestions}, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response({"error": "suggest_failed", "details": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Allow clients to POST tasks to update the in-memory cache used by GET.
        This mirrors analyze but keeps a lightweight contract.
        """
        global _LAST_ANALYZED_PAYLOAD
        serializer = SingleTaskSerializer(data=request.data)
        # allow both single task and list of tasks via flexible handling
        if isinstance(request.data, dict) and "tasks" in request.data:
            tasks = request.data.get("tasks")
            _LAST_ANALYZED_PAYLOAD = tasks
            return Response({"message": "cached"}, status=status.HTTP_200_OK)
        return Response({"error": "invalid_payload"}, status=status.HTTP_400_BAD_REQUEST)
