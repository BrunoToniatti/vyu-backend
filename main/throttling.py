from rest_framework.throttling import SimpleRateThrottle


class LoginRateThrottle(SimpleRateThrottle):
    """
    Dedicated and strict rate throttle for login endpoints
    to protect against brute force and credential stuffing attacks.
    """
    scope = 'login'

    def get_cache_key(self, request, view):
        # Throttle by client IP address
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
