from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST

from . import brevo


@require_POST
def subscribe(request):
    email = request.POST.get("email", "").strip()
    redirect_to = request.META.get("HTTP_REFERER", "/")

    try:
        validate_email(email)
    except ValidationError:
        messages.error(request, "That doesn't look like a valid email address.")
        return HttpResponseRedirect(redirect_to)

    brevo.handle_new_subscriber(email)
    messages.success(request, "Thank you — your subscription has been recorded.")
    return HttpResponseRedirect(redirect_to)
