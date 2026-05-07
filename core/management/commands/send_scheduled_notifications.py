from django.core.management.base import BaseCommand
from core.services.notification_service import NotificationService

class Command(BaseCommand):
    help = 'Triggers scheduled notifications (profile incomplete, test reminders, CAP alerts)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting scheduled notifications...")
        svc = NotificationService()
        
        p_sent = svc.trigger_profile_incomplete_reminders()
        self.stdout.write(f"Profile reminders sent: {p_sent}")
        
        t_sent = svc.trigger_test_reminders()
        self.stdout.write(f"Test reminders sent: {t_sent}")
        
        c_sent = svc.trigger_cap_round_alerts()
        self.stdout.write(f"CAP alerts sent: {c_sent}")
        
        total = p_sent + t_sent + c_sent
        self.stdout.write(self.style.SUCCESS(f"Total notifications created: {total}"))
        
        self.stdout.write("\nSuggested Crontab Line:")
        self.stdout.write("0 9 * * * /path/to/python manage.py send_scheduled_notifications")
