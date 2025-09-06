from django.conf import settings
import requests

class Paystack:
    PAYSTACK_SK = settings.PAYSTACK_SECRET_KEY

    def verify_payment(self, ref, *args, **kwargs):
        path = f'https://api.paystack.co/transaction/verify/{ref}'
        headers = {
            "Authorization": f"Bearer {self.PAYSTACK_SK}",
            "Content-Type": "application/json",
        }


        try:
            response = requests.get(path, headers=headers)
            response.raise_for_status()  # Raise an exception for HTTP errors
            response_data = response.json()

            return response_data['status'], response_data['data']
        except requests.exceptions.RequestException as e:
            # Handle network errors or other exceptions
            return 'error', str(e)
