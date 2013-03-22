from django.db import models

# Create your models here.
class ReportingHistory(models.Model):
	#id = models.IntegerField(primary_key=True)
	contactname = models.TextField()
	slug = models.TextField(blank=True)
	noted = models.TextField(blank=True)
	job = models.TextField(blank=True)
	phone = models.TextField(blank=True)
	longitude = models.TextField()
	latitude = models.TextField()
	archive = models.TextField()
	profilepic = models.TextField(blank=True)
	reportdate = models.TextField()
	reportepoch = models.IntegerField(null=True, blank=True)
	address = models.TextField(blank=True)
	def __unicode__(self):
		return self.contactname + ' ' + self.slug

	class Meta:
		db_table = u'reporting_history'
