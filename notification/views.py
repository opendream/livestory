from account.models import AccountKey
from notification.models import Notification

def get_notifications(user):
	notifications = []
	if user.is_authenticated():
		try:
			account_key = AccountKey.objects.get(user=user)
			notifications = Notification.objects.filter(subject=user, datetime__gt=account_key.view_notification)
		except AccountKey.DoesNotExist:
			pass
	return notifications