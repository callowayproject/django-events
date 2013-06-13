from django.db import models


class Quote(models.Model):
    quote = models.TextField()
    author = models.CharField(
        blank=True,
        max_length=255,
        default="Anonymous",
        help_text='The quote\'s author.')
    circa = models.CharField(
        blank=True,
        max_length=100,
        help_text="When was the quote said?")
    source = models.CharField(
        blank=True,
        max_length=100,
        help_text="Name of writing, or situation describing quote.")

    class Meta:
        verbose_name_plural = 'Quotes'

    def __unicode__(self):
        return "%s --%s" % (self.quote, self.author)
