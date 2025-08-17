from django.core.management.base import BaseCommand
from api.factories import UserFactory

class Command(BaseCommand):
    help = "Popula o banco com usuários fake"

    def add_arguments(self, parser):
        parser.add_argument("total", type=int, help="Quantidade de usuários")

    def handle(self, *args, **options):
        total = options["total"]
        UserFactory.create_batch(total)
        self.stdout.write(self.style.SUCCESS(f"{total} usuários criados com sucesso!"))
