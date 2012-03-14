from account.models import AccountKey
from django.http import HttpResponse
from django.shortcuts import redirect, render
from notification.models import Notification

def view(request):
	if not request.user.is_authenticated():
		return render(request, '403.html', status=403)

	return HttpResponse('xxx')

def get_notifications(user):
	notifications = []
	if user.is_authenticated():
		try:
			account_key = AccountKey.objects.get(user=user)
			notifications = Notification.objects.filter(subject=user, datetime__gt=account_key.view_notification)
		except AccountKey.DoesNotExist:
			pass
	return notifications