from account.models import AccountKey
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson as json
from notification.models import Notification

def view(request):
	if not request.user.is_authenticated():
		return render(request, '403.html', status=403)

	# Update view notification
	AccountKey.objects.get(user=request.user).update_view_notification()

	# If request is ajax
	if request.is_ajax():
		print json.dumps({'status': 200})
		return HttpResponse(json.dumps({'status': 200}), mimetype='application/json')

	context = {}
	return render(request, 'notification/notification_view.html', context)

def get_notifications(user):
	notifications = []
	if user.is_authenticated():
		try:
			account_key = AccountKey.objects.get(user=user)
			notifications = Notification.objects.filter(blog__user=user, datetime__gt=account_key.view_notification)
		except AccountKey.DoesNotExist:
			pass
	return notifications
