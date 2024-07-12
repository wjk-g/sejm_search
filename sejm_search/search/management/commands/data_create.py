
from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = "Create data"

    def handle(self, *args, **options):
        '''
        Call other commands responsible for getting 'foundational' data from API
        '''

        call_command("terms_create")
        call_command("terms_create")
        call_command("mps_get")
        call_command("mps_create")
        call_command("terms_and_mps_link")
        #call_command("committees_get")
        call_command("committees_create")
        call_command("terms_committees_and_members_link")
        call_command("sittings_create")

        self.stdout.write(
            self.style.SUCCESS("Process completed!")
        )
