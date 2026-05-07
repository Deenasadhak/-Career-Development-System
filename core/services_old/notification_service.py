from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Prefetch, Q
from core.models import Notification, NotificationPreference
from core.models import StudentProfile
from core.models import TestSession
from core.models import CAPRound

class NotificationService:
    def create_notification(
            self,
            recipient,
            notification_type: str,
            title: str,
            message: str,
            link: str = '',
            expires_days: int = None) -> Notification:
        
        pref, _ = NotificationPreference.objects.get_or_create(user=recipient)
        
        pref_field_map = {
            'ADMISSION_DEADLINE': 'admission_deadline',
            'EXAM_DATE': 'exam_date',
            'CUTOFF_RELEASED': 'cutoff_released',
            'SCHOLARSHIP_DEADLINE': 'scholarship_deadline',
            'RECOMMENDATION_READY': 'recommendation_ready',
            'PROFILE_INCOMPLETE': 'profile_incomplete',
            'NEW_COLLEGE': 'new_college',
            'CAP_ROUND_OPENING': 'cap_round_opening',
            'TEST_REMINDER': 'test_reminder',
            'SHORTLIST_REMINDER': 'shortlist_reminder',
        }
        
        field_name = pref_field_map.get(notification_type)
        if field_name and not getattr(pref, field_name, True):
            return None

        expires_at = None
        if expires_days:
            expires_at = timezone.now() + timedelta(days=expires_days)

        return Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            title=title,
            message=message,
            link=link,
            expires_at=expires_at
        )

    def send_bulk_notification(
            self,
            user_queryset,
            notification_type: str,
            title: str,
            message: str,
            link: str = '',
            expires_days: int = None) -> int:
        
        pref_field_map = {
            'ADMISSION_DEADLINE': 'admission_deadline',
            'EXAM_DATE': 'exam_date',
            'CUTOFF_RELEASED': 'cutoff_released',
            'SCHOLARSHIP_DEADLINE': 'scholarship_deadline',
            'RECOMMENDATION_READY': 'recommendation_ready',
            'PROFILE_INCOMPLETE': 'profile_incomplete',
            'NEW_COLLEGE': 'new_college',
            'CAP_ROUND_OPENING': 'cap_round_opening',
            'TEST_REMINDER': 'test_reminder',
            'SHORTLIST_REMINDER': 'shortlist_reminder',
        }
        field_name = pref_field_map.get(notification_type)
        
        # Prefetch preferences
        opted_in_user_ids = set()
        user_ids = list(user_queryset.values_list('id', flat=True))
        
        prefs = NotificationPreference.objects.filter(user_id__in=user_ids).values('user_id', field_name)
        pref_dict = {p['user_id']: p[field_name] for p in prefs}
        
        # Users without explicit preference records default to True (mostly) or False (for new_college)
        default_pref = True
        if notification_type == 'NEW_COLLEGE':
            default_pref = False
            
        for uid in user_ids:
            if pref_dict.get(uid, default_pref):
                opted_in_user_ids.add(uid)

        expires_at = None
        if expires_days:
            expires_at = timezone.now() + timedelta(days=expires_days)

        notifications = [
            Notification(
                recipient_id=uid,
                notification_type=notification_type,
                title=title,
                message=message,
                link=link,
                expires_at=expires_at
            ) for uid in opted_in_user_ids
        ]
        
        created = Notification.objects.bulk_create(notifications)
        return len(created)

    def mark_read(
            self,
            user,
            notification_id: int) -> bool:
        try:
            notif = Notification.objects.get(pk=notification_id, recipient=user)
            if not notif.is_read:
                notif.is_read = True
                notif.read_at = timezone.now()
                notif.save(update_fields=['is_read', 'read_at'])
            return True
        except Notification.DoesNotExist:
            return False

    def mark_all_read(self, user) -> int:
        return Notification.objects.filter(recipient=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )

    def get_unread_count(self, user) -> int:
        now = timezone.now()
        return Notification.objects.filter(
            recipient=user, 
            is_read=False
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        ).count()

    def get_notifications(
            self,
            user,
            include_read: bool = False,
            limit: int = 20) -> list:
        now = timezone.now()
        qs = Notification.objects.filter(recipient=user).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=now)
        )
        if not include_read:
            qs = qs.filter(is_read=False)
            
        return list(qs.order_by('is_read', '-created_at')[:limit])

    def trigger_profile_incomplete_reminders(
            self) -> int:
        week_ago = timezone.now() - timedelta(days=7)

        recent_reminded = Notification.objects.filter(
            notification_type='PROFILE_INCOMPLETE',
            created_at__gte=week_ago,
        ).values_list('recipient_id', flat=True)

        students = StudentProfile.objects.filter(
            is_profile_complete=False,
            user__date_joined__lt=week_ago,
        ).exclude(
            user_id__in=recent_reminded
        ).select_related('user')
        
        count = 0
        for s in students:
            res = self.create_notification(
                recipient=s.user,
                notification_type='PROFILE_INCOMPLETE',
                title='Complete Your Profile',
                message='Please complete your profile to get more accurate career recommendations.',
                link='/profile/edit/',
                expires_days=7
            )
            if res: count += 1
        return count

    def trigger_test_reminders(self) -> int:
        taken_test_ids = TestSession.objects.filter(status='COMPLETED').values_list(
            'student__user_id', flat=True).distinct()

        week_ago = timezone.now() - timedelta(days=7)
        recent_reminded = Notification.objects.filter(
            notification_type='TEST_REMINDER',
            created_at__gte=week_ago,
        ).values_list('recipient_id', flat=True)

        students = StudentProfile.objects.filter(
            is_profile_complete=True,
        ).exclude(
            user_id__in=taken_test_ids
        ).exclude(
            user_id__in=recent_reminded
        ).select_related('user')

        count = 0
        for s in students:
            res = self.create_notification(
                recipient=s.user,
                notification_type='TEST_REMINDER',
                title='Take Your Aptitude Test',
                message='Unlock personalized recommendations by taking our aptitude test.',
                link='/assessment/start/',
                expires_days=7
            )
            if res: count += 1
        return count

    def trigger_cap_round_alerts(self) -> int:
        upcoming = CAPRound.objects.filter(
            is_active=True,
            registration_start__gte=date.today(),
            registration_start__lte=date.today() + timedelta(days=7),
        )

        total_sent = 0
        for round_obj in upcoming:
            students = StudentProfile.objects.filter(
                keam_rank__isnull=False,
            ).select_related('user')
            
            sent = self.send_bulk_notification(
                user_queryset=[s.user for s in students],
                notification_type='CAP_ROUND_OPENING',
                title=f'CAP Round Opening: {round_obj.name}',
                message=f'Registration for {round_obj.name} starts on {round_obj.registration_start}.',
                link='/kerala/cap/',
                expires_days=7
            )
            total_sent += sent
        return total_sent
