from django.db import models
from datetime import date

class SeqRun(models.Model):
    class Meta:
        ordering = ['date','run_name']
    run_name = models.CharField(max_length=200)
    machine_name = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    num_clusters = models.BigIntegerField(null=True, blank=True)
    num_clusters_pf = models.BigIntegerField(null=True, blank=True)
    percent_pf_clusters = models.FloatField(null=True, blank=True)
    cluster_density = models.FloatField(null=True, blank=True)
    cluster_density_pf = models.FloatField(null=True, blank=True)
    num_reads_per_cluster = models.IntegerField(null=True, blank=True)
    num_tiles = models.IntegerField(null=True, blank=True)
    num_lanes = models.IntegerField(null=True, blank=True)
    perc_q_ge_30 = models.FloatField(null=True, blank=True)
    specs = models.TextField()
    type = models.CharField(max_length=20, default="run")

    def __unicode__(self):  
        return(self.run_name)

class Lane(models.Model): 
    class Meta:
        ordering = ['date','run_name','lane_num']
    lane_num = models.IntegerField(null=True, blank=True)
    run_name = models.CharField(max_length=200)
    sub_name = models.CharField(max_length=200)
    machine_name = models.CharField(max_length=200)
    date = models.DateField(null=True, blank=True)
    num_clusters = models.BigIntegerField(null=True, blank=True)
    num_clusters_pf = models.BigIntegerField(null=True, blank=True)
    percent_pf_clusters = models.FloatField(null=True, blank=True)
    cluster_density = models.FloatField(null=True, blank=True)
    cluster_density_pf = models.FloatField(null=True, blank=True)
    perc_q_ge_30 = models.FloatField(null=True, blank=True)
    num_tiles = models.IntegerField(null=True, blank=True)
    seqrun = models.ForeignKey('SeqRun',null=True, blank=True)
    type = models.CharField(max_length=20, default="lane")

    def __unicode__(self):  
        try:
            run_name = self.run_name
        except:
            run_name = "No run assigned"
        return(run_name + ", lane " + str(self.lane_num))
