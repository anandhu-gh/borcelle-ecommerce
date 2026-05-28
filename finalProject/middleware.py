from django.shortcuts import redirect
from django.http import HttpResponse


class SessionCheckMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        protected_urls = [

            '/admin/',
            '/customer/',
            '/delivery/',

        ]

        # allow static files
        if request.path.startswith('/static/'):
            return self.get_response(request)

        # check protected routes
        for url in protected_urls:

            if request.path.startswith(url):

                # if session missing
                if 'loginId' not in request.session:

                   return HttpResponse(
                        "<script>alert('Session ended! Login again to continue.');window.location='/login/'</script>"
                    )

        response = self.get_response(request)

        # prevent browser back cache
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'

        return response