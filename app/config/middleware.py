"""
middleware.py: the /health/ endpoint for the AWS load balancer.

WHY: the load balancer checks every container by calling /health/.
It uses the container's private IP (like 10.0.1.23) as the Host, which is
not in ALLOWED_HOSTS, so Django would answer 400 and the load balancer
would think every container is broken.

So this middleware answers /health/ BEFORE Django checks the host.
"""

from django.http import HttpResponse


class HealthCheckMiddleware:
    def __init__(self, get_response):
        # GIVEN: Django passes in "the rest of the app" as get_response.
        self.get_response = get_response  # door

    def __call__(self, request):
        if request.path == "/health/":  # for load balancer to TEST and to direct to different ECR
            return HttpResponse("ok")
        else:
            return self.get_response(
                request
            )  # django function to take request after receivin from gunicorn

        # - If request.path is "/health/", return HttpResponse("ok")
        # - Otherwise, pass the request on: return self.get_response(request)
        ...
