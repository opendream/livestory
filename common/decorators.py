from functools import wraps

from django.shortcuts import render
from django.utils.decorators import available_attrs

def user_is_staff(function=None):
    def decorator(view_func):
        @wraps(view_func, assigned=available_attrs(view_func))
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_staff:
                return render(request, '403.html', status=403)

            return view_func(request, *args, **kwargs)

        return _wrapped_view
    return decorator(function)