from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.utils import timezone
from blog.models import Newsletter, EmailSubscription

class Command(BaseCommand):
    help = 'Send newsletters to all subscribers'

    def handle(self, *args, **kwargs):
        newsletters = Newsletter.objects.filter(is_sent=False)
        for newsletter in newsletters:
            subscribers = EmailSubscription.objects.filter(is_active=True)

            if subscribers.exists():
                messages = []
                for subscriber in subscribers:
                    message = (
                        newsletter.subject,
                        newsletter.content,
                        'noreply@aimlblog.com',
                        [subscriber.email],
                    )
                    messages.append(message)

                try:
                    send_mass_mail(messages)
                    newsletter.is_sent= True
                    newsletter.sent_at = timezone.now()
                    newsletter.sent_count = len(subscribers)
                    newsletter.save()

                    self.stdout.write(self.style.SUCCESS(f'Newsletter "{newsletter.subject}" sent to {len(subscribers)} subscribers'))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error sending newsletter "{newsletter.subject}": {e}'))

            else:
                self.stdout.write(self.style.WARNING(f'No active subscribers found for newsletter "{newsletter.subject}"'))



