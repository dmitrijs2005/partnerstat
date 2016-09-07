from django.db import models

# Create your models here.

STREAM_TYPE_CHOICES = (
    ('all', 'All'),
    ('live', 'Live'),
    ('vod', 'VOD'),
)

ZERO_MINUTES = 0
ONE_MINUTE = 60
TWO_MINUTES = 120
FIVE_MINUTES = 300

THRESHOLD_CHOICES = (
    (ZERO_MINUTES, 'Any'),
    (ONE_MINUTE, '1 minute'),
    (TWO_MINUTES, '2 minutes'),
    (FIVE_MINUTES, '5 minutes'),
)


class Viewing(models.Model):
    date = models.DateField('date')
    threshold = models.IntegerField(
        default=ZERO_MINUTES,
        choices=THRESHOLD_CHOICES
    )
    user_qty = models.IntegerField(default=0)
    ips_qty = models.IntegerField(default=0)
    stream_type = models.CharField(
        max_length=10,
        choices=STREAM_TYPE_CHOICES,
        default='all',
    )
    total_streams = models.IntegerField(default=0)
    avg_played_seconds = models.IntegerField(default=0)
    total_played_seconds = models.IntegerField(default=0)
    max_played_seconds = models.IntegerField(default=0)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{date} - {stream_type} - {threshold}'.format(date=self.date, stream_type=self.stream_type, threshold=self.threshold)

