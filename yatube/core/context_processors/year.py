import datetime

from django.http import HttpRequest


def year(request: HttpRequest) -> dict:
    """Context processor that adds filter 'year'
    which set date on now.
    """
    return {
        'year': datetime.datetime.now().year
    }
