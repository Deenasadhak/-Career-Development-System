from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Runs the full seed workflow sequentially'

    def add_arguments(self, parser):
        parser.add_argument('--skip', nargs='+', type=str, help='Commands to skip (e.g. seed_districts)')
        parser.add_argument('--from', type=str, dest='from_command', help='Command to start from')

    def handle(self, *args, **options):
        commands = [
            'seed_districts',
            'seed_universities',
            'seed_streams',
            'migrate_legacy',
        ]
        
        skip_list = options.get('skip') or []
        from_cmd = options.get('from_command')
        
        start_idx = 0
        if from_cmd:
            if from_cmd in commands:
                start_idx = commands.index(from_cmd)
            else:
                raise CommandError(f"Command '{from_cmd}' not found in sequence.")
                
        for cmd in commands[start_idx:]:
            if cmd in skip_list:
                self.stdout.write(self.style.WARNING(f"Skipping {cmd}..."))
                continue
                
            self.stdout.write(self.style.SUCCESS(f"\n--- Running {cmd} ---"))
            call_command(cmd)
            
        self.stdout.write(self.style.SUCCESS("\nFULL SEED WORKFLOW COMPLETED SUCCESSFULLY!"))
