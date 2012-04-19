from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import simplejson as json
from django.contrib.auth.decorators import login_required

from account.models import UserProfile, UserInvitation
from notification.models import Notification

@login_required
def view(request):
	# Update view notification
	try:
		UserInvitation.objects.get(invited_by=request.user).update_view_notification()
	except UserInvitation.DoesNotExist:
		pass

	# If request is ajax
	if request.is_ajax():
		return HttpResponse(json.dumps({'status': 200}), mimetype='application/json')

	last_notification = Notification.objects.all().order_by('-datetime')[:1]
	notifications = []
	if len(last_notification) == 1:
		last_seven_days = last_notification[0].datetime - timedelta(7)
		notifications = Notification.objects.filter(
			datetime__gt=last_seven_days
		).exclude(
			subject=request.user
		).order_by('-datetime')

	context = {
		'notification7days': notifications
	}
	return render(request, 'notification/notification_view.html', context)

def get_notifications(user):
	notifications = []
	if user.is_authenticated():
		try:
			account_key = UserProfile.objects.get(user=user)
			notifications = Notification.objects.filter(blog__user=user, datetime__gt=account_key.notification_viewed).order_by('-datetime')
		except UserInvitation.DoesNotExist:
			pass
	return notifications
