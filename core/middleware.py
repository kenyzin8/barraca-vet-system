import re
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

class MinifyHTMLMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if response['Content-Type'].startswith('text/html'):
            response.content = self.minify_html(response.content.decode())
            response['Content-Length'] = str(len(response.content))
        return response

    def minify_html(self, html_content):
        html_content = re.sub(r'\s+', ' ', html_content)
        html_content = re.sub(r'>\s+<', '><', html_content)
        return html_content

class SessionDisplayMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            for key, value in request.session.items():
                print(f'{key} => {value}')
            
            response = self.get_response(request)
            return response
        else:
            pass