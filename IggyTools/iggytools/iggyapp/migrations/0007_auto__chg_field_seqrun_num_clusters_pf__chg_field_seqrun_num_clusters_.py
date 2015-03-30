# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):

        # Changing field 'SeqRun.num_clusters_pf'
        db.alter_column(u'seqstats_seqrun', 'num_clusters_pf', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'SeqRun.num_clusters'
        db.alter_column(u'seqstats_seqrun', 'num_clusters', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'Lane.num_clusters_pf'
        db.alter_column(u'seqstats_lane', 'num_clusters_pf', self.gf('django.db.models.fields.BigIntegerField')(null=True))

        # Changing field 'Lane.num_clusters'
        db.alter_column(u'seqstats_lane', 'num_clusters', self.gf('django.db.models.fields.BigIntegerField')(null=True))

    def backwards(self, orm):

        # Changing field 'SeqRun.num_clusters_pf'
        db.alter_column(u'seqstats_seqrun', 'num_clusters_pf', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'SeqRun.num_clusters'
        db.alter_column(u'seqstats_seqrun', 'num_clusters', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Lane.num_clusters_pf'
        db.alter_column(u'seqstats_lane', 'num_clusters_pf', self.gf('django.db.models.fields.IntegerField')(null=True))

        # Changing field 'Lane.num_clusters'
        db.alter_column(u'seqstats_lane', 'num_clusters', self.gf('django.db.models.fields.IntegerField')(null=True))

    models = {
        u'seqstats.lane': {
            'Meta': {'ordering': "['date', 'run_name', 'lane_num']", 'object_name': 'Lane'},
            'cluster_density': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cluster_density_pf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'lane_num': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'num_clusters': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_clusters_pf': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_tiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'perc_q_ge_30': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'percent_pf_clusters': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'run_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'seqrun': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['seqstats.SeqRun']", 'null': 'True', 'blank': 'True'}),
            'sub_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'lane'", 'max_length': '20'})
        },
        u'seqstats.seqrun': {
            'Meta': {'ordering': "['date', 'run_name']", 'object_name': 'SeqRun'},
            'cluster_density': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'cluster_density_pf': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'machine_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'num_clusters': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_clusters_pf': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_lanes': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_reads_per_cluster': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'num_tiles': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'perc_q_ge_30': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'percent_pf_clusters': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'run_name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'specs': ('django.db.models.fields.TextField', [], {}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'run'", 'max_length': '20'})
        }
    }

    complete_apps = ['seqstats']