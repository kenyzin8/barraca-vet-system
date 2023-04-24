import re
from django.utils.deprecation import MiddlewareMixin

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
