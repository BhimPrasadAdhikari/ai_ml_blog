from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

class SearchAnalytics(models.Model):
    query = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    results_count = models.IntegerField()
    filters_used = models.JSONField(default=dict)
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        verbose_name = 'Search Analytics'
        verbose_name_plural = 'Search Analytics'
        ordering = ['-timestamp']

    @classmethod
    def log_search(cls, request, query, results_count, filters=None):
        """
        Log a search query for analytics
        """
        if not query:  # Don't log empty searches
            return

        cls.objects.create(
            query=query,
            results_count=results_count,
            filters_used=filters or {},
            user=request.user if request.user.is_authenticated else None,
            ip_address=request.META.get('REMOTE_ADDR')
        )

    @classmethod
    def get_popular_searches(cls, days=7):
        """
        Get the most popular search queries in the last n days
        """
        cutoff_date = timezone.now() - timezone.timedelta(days=days)
        return cls.objects.filter(
            timestamp__gte=cutoff_date
        ).values('query').annotate(
            count=models.Count('id')
        ).order_by('-count')[:10] 