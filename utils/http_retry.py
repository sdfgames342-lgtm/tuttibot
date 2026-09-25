"""
Adaptador HTTP personalizado que respeta la cabecera Retry-After en respuestas 429,
además de los reintentos estándar de urllib3.
"""
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

class RetryAfterAdapter(HTTPAdapter):
    """Adaptador que añade espera según Retry-After antes de reintentar."""

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        response = super().send(request, stream, timeout, verify, cert, proxies)
        if response.status_code == 429:
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                try:
                    sleep_time = int(retry_after)
                except ValueError:
                    sleep_time = 5
                time.sleep(sleep_time)
                response = super().send(request, stream, timeout, verify, cert, proxies)
        return response

def create_optimized_session():
    """Crea una sesión requests con pool y reintentos inteligentes."""
    session = requests.Session()
    retry_strategy = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504], allowed_methods=['GET', 'POST'])
    adapter = RetryAfterAdapter(max_retries=retry_strategy, pool_connections=20, pool_maxsize=20)
    session.mount('https://', adapter)
    return session