from django.http import HttpResponseForbidden
from django.template.loader import render_to_string

def csrf_failure(request, reason=""):
    context = {'reason': reason}
    return HttpResponseForbidden(
        render_to_string('403_csrf.html', context, request),
        content_type='text/html'
    ) 