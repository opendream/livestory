from account.models import AccountKey
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson as json
from notification.models import Notification

from datetime import datetime, timedelta

def view(request):
	if not request.user.is_authenticated():
		return render(request, '403.html', status=403)

	# Update view notification
	AccountKey.objects.get(user=request.user).update_view_notification()

	# If request is ajax
	if request.is_ajax():
		print json.dumps({'status': 200})
		return HttpResponse(json.dumps({'status': 200}), mimetype='application/json')

	last_notification = Notification.objects.all().order_by('-datetime')[:1]
	last_seven_days = last_notification[0].datetime - timedelta(7)
	print 'last 7 days = ', last_seven_days
	notifications = Notification.objects.filter(datetime__gt=last_seven_days)
	for notification in notifications:
		print notification.subject.get_profile().get_fullname(), notification.datetime

	context = {
		'notification7days': notifications
	}
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
