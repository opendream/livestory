from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required

from account.models import UserProfile, UserInvitation
from notification.models import Notification

@login_required
def view_notifications(request):
	# Update view notification
	try:
		UserProfile.objects.get(user=request.user).update_view_notification()
	except UserProfile.DoesNotExist:
		pass

	last_notification = Notification.objects.all().filter(blog__user=request.user).order_by('-datetime')[:1]
	notifications = []
	if len(last_notification) == 1:
		last_seven_days = last_notification[0].datetime - timedelta(7)
		notifications = Notification.objects.filter(
			datetime__gt=last_seven_days
		).filter(
			blog__user=request.user
		).exclude(
			subject=request.user
		).order_by('-datetime')

	context = {
		'notification7days': notifications
	}
	return render(request, 'notification/notification_view.html', context)

@login_required
def ajax_set_notifications_as_viewed(request):
    request.user.get_profile().update_view_notification()
    return HttpResponse(json.dumps({'status': 200}), mimetype='application/json')

def get_notifications(user):
	notifications = []
	if user.is_authenticated():
		try:
			account_key = UserProfile.objects.get(user=user)
			notifications = Notification.objects.filter(blog__user=user, datetime__gt=account_key.notification_viewed).order_by('-datetime')
		except UserInvitation.DoesNotExist:
			pass
	return notifications
