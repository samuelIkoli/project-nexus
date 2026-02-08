from django.core.management.base import BaseCommand, CommandError
import logging
import time
import requests

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Ping the hosted Project Nexus endpoint to keep it warm."

    def handle(self, *args, **options):
        url = "https://project-nexus-j3pl.onrender.com/"

        start = time.perf_counter()
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            elapsed_ms = (time.perf_counter() - start) * 1000
            message = f"Pinged {url} -> {resp.status_code} in {elapsed_ms:.1f} ms"
            self.stdout.write(self.style.SUCCESS(message))
            logger.info(message)
        except Exception as exc:
            logger.error("Ping failed: %s", exc)
            raise CommandError(f"Ping failed: {exc}")
