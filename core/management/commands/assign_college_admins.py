from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import College

User = get_user_model()

class Command(BaseCommand):
    help = 'Assigns a COLLEGE_ADMIN user to a specific College.'

    def add_arguments(self, parser):
        parser.add_argument('--user_id', type=int, help='ID of the User to assign')
        parser.add_argument('--college_id', type=int, help='ID of the College')

    def handle(self, *args, **options):
        user_id = options.get('user_id')
        college_id = options.get('college_id')

        # If no arguments are provided, list unassigned admins
        if not user_id and not college_id:
            msg = "Unassigned COLLEGE_ADMIN Users:\n"
            unassigned = User.objects.filter(role='COLLEGE_ADMIN', administered_college__isnull=True)
            if unassigned.exists():
                for u in unassigned:
                    msg += f"- ID: {u.id} | Email: {u.email} | Name: {u.first_name} {u.last_name}\n"
            else:
                msg += "No unassigned COLLEGE_ADMIN users found.\n"
            self.stdout.write(msg)
            return

        if not user_id or not college_id:
            self.stdout.write(self.style.ERROR("Please provide both --user_id and --college_id"))
            return

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"User with ID {user_id} does not exist."))
            return

        if getattr(user, 'role', '') != 'COLLEGE_ADMIN':
            self.stdout.write(self.style.ERROR(f"User {user.email} does not have the COLLEGE_ADMIN role."))
            return

        if hasattr(user, 'administered_college') and user.administered_college is not None:
             self.stdout.write(self.style.ERROR(f"User {user.email} is already administering {user.administered_college.name}."))
             return

        try:
            college = College.objects.get(id=college_id)
        except College.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"College with ID {college_id} does not exist."))
            return

        if college.admin_user is not None:
            if college.admin_user == user:
                 self.stdout.write(self.style.WARNING(f"User already assigned to this college."))
                 return
            self.stdout.write(self.style.ERROR(f"College {college.name} already has an admin user assigned (ID: {college.admin_user.id})."))
            return

        college.admin_user = user
        college.save(update_fields=['admin_user'])

        self.stdout.write(self.style.SUCCESS(f"Assigned {user.email} as admin for {college.name}"))
