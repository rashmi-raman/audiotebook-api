from tastypie.resources import ModelResource,ALL
from tastypie.resources import Resource
from audiotebook_api.models import ReportingHistory
from tastypie.authorization import Authorization
import base64
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
import zipfile
import os
import sys
from xml.dom import minidom
import xml

import tempfile
import shutil

import requests
import json
import time

from django.conf import settings

class ReportingHistoryResource(ModelResource):
	class Meta:
		queryset = ReportingHistory.objects.all()
		resource_name = 'reportinghistory'
		authorization= Authorization()	

		filtering = {
            'slug': ALL,
            'contactname':ALL
        }
		ordering = ['reportepoch']

	def obj_create( self, bundle, request = None, **kwargs ):

		print >> sys.stderr, 'inside obj_create'

		try:

			root_dir = tempfile.mkdtemp()
			print >> sys.stderr, 'created root dir'

			cname = bundle.data['cname']
			job = bundle.data['job']
			phone = bundle.data['phone']
			audio = base64.b64decode(bundle.data['audio'])
			noted = bundle.data['noted']
			todayDate = bundle.data['todayDate']
			slug = bundle.data['slug']
			longitude = bundle.data['longitude']
			latitude = bundle.data['latitude']
			image = base64.b64decode(bundle.data['image'])
			contactimage = base64.b64decode(bundle.data['contactimage'])

			query = "http://maps.googleapis.com/maps/api/geocode/json?" + "latlng=" + latitude + "," + longitude + "&sensor=false";
			print >> sys.stderr, query
			response = requests.get(query)
			address = response.json()['results'][0]['formatted_address']

			str = todayDate[0:-4]
			format = '%B %d, %Y, %I:%M:%S %p'

			reportepoch = int(time.mktime(time.strptime(str, format)))

			print >> sys.stderr, 'got db col values'

			top = Element('reportedData')

			child = SubElement(top, 'contact')
			contact_child = SubElement(child, 'contactName')
			contact_child.text = cname
			contact_child = SubElement(child, 'job')
			contact_child.text = job
			contact_child = SubElement(child, 'phone')
			contact_child.text = phone
			print >> sys.stderr, 'added phone'

			contact_child = SubElement(child, 'profileImage')
			strraw = cname + "_" + slug

			picname = ''.join(e for e in strraw if e.isalnum())

			picname = picname + '.jpeg' 
			
			contact_child.text = picname
			print >> sys.stderr, 'added picname'

			
			child = SubElement(top, 'archiveDate')
			child.text = todayDate
			
			child = SubElement(top, 'geoloc')
			loc_child = SubElement(child,'latitude')
			loc_child.text = latitude
			loc_child = SubElement(child,'longitude')
			loc_child.text = longitude
			
			child = SubElement(top, 'slug')
			child.text = slug
			
			child = SubElement(top, 'notes')
			child.text = noted
			
			child = SubElement(top, 'audioFileLocation')
			child.text = 'audio.caf'
			
			child = SubElement(top, 'imageFile')
			child.text = 'image.jpeg'

			rough_string = xml.etree.ElementTree.tostring(top, 'utf-8')

			print >> sys.stderr, 'got rough xml'

			reparsed = minidom.parseString(rough_string)
			xml_str = reparsed.toprettyxml(indent="  ")

			print >> sys.stderr, 'created xml'

			f = tempfile.NamedTemporaryFile(prefix = 'metadata', suffix='.xml',dir = root_dir,delete=False)
			f.write(xml_str)
			f.close()
			print >> sys.stderr, 'wrote xml'

			f1 = tempfile.NamedTemporaryFile(prefix = 'audio', suffix='.caf',dir = root_dir,delete=False)
			f1.write(audio)
			f1.close()
			print >> sys.stderr, 'wrote audio'

			f2 = tempfile.NamedTemporaryFile(prefix = 'image', suffix='.jpeg',dir = root_dir,delete=False)
			f2.write(image)
			f2.close()
			print >> sys.stderr, 'wrote image'

			f3 = tempfile.TemporaryFile()
			f3.write(contactimage)
			f3.seek(0,0)
			print >> sys.stderr, 'wrote contactimage'

			print >> sys.stderr, 'wrote asset files '

			zipfileName = shutil.make_archive(base_name=cname + "_" + slug,format='zip',root_dir=root_dir)
			print >> sys.stderr, 'wrote zip file '

			shutil.rmtree(root_dir)
			print >> sys.stderr, 'removed folder '

		
			import boto
			from boto.s3.key import Key
			
			bucket_name = settings.BUCKET_NAME
			conn = boto.connect_s3(settings.AWS_ACCESS_KEY_ID,
                    settings.AWS_SECRET_ACCESS_KEY)
			bucket = conn.get_bucket(bucket_name)

			strraw = cname + "_" + slug

			fname = ''.join(e for e in strraw if e.isalnum())

			fname = fname + '.zip' 

			k = Key(bucket)
			k.key = fname

			k.set_contents_from_filename(zipfileName)
			k.make_public()
			bucket.set_acl('public-read',fname)

			k = Key(bucket)
			k.key = picname

			k.set_contents_from_file(f3)
			k.make_public()
			bucket.set_acl('public-read',picname)

			f3.close()

			print >> sys.stderr, 'uploaded zip file '

			bundle.obj = ReportingHistory(contactname=cname,job=job,phone=phone,slug=slug,noted=noted,longitude=longitude,latitude=latitude,reportdate=todayDate,reportepoch=reportepoch,address=address,profilepic='https://s3-us-west-2.amazonaws.com/'+ bucket_name + "/" + picname,archive='https://s3-us-west-2.amazonaws.com/'+bucket_name + "/" + fname)

			bundle.obj.save()

			print >> sys.stderr, 'wrote db object '

		except:
			print >> sys.stderr, "Unexpected error:", sys.exc_info()[1]
			raise

		return bundle