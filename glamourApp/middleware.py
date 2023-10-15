class DefaultCurrencyMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'currency_preference' not in request.session:
            request.session['currency_preference'] = 'NGN'
        response = self.get_response(request)
        return response
