#!/usr/bin/env python

"""Module bigjob_condor.

This Module is used to launch a set of jobs via a local Condor pool created using the glidein technique

"""

import saga
import time
import uuid
import socket
import os

CONDOR_BIN = "/home/latin/saga/condor_bin"		# local directory with condor_submit wrapper
CONDOR_LOCATION = "/home/lukas/packages/condor-7.3.2"	# CONDOR_LOCATION on the remote site

class bigjob_condor():

	def __init__(self, database_host=None):
		self.uuid = uuid.uuid1()
		self.state=saga.job.Unknown
		self.pilot_url=""

	"""Create a local Condor pool - glidein condor_master on remote
	   resources via Condor-G -> GRAM2
	"""
	def start_pilot_job(self,
		lrms_url=None,
		bigjob_agent_executable=None,
		number_nodes=1,
		queue=None,
		project=None,
		working_directory="/tmp",
		userproxy=None,
		walltime=60,
		cloud_type=None,
		image_name=None):

		print "Working directory: " + working_directory
		if not os.path.isdir(working_directory):
			os.mkdir(working_directory)
		self.lrms_url = lrms_url
		self.subjobs = {}

		self.js_url = saga.url("condor://localhost/")
		self.job_service = saga.job.service(self.js_url)
		self.pilot_url = "condor://" + socket.getfqdn()

		condor_glidein_desc = saga.job.description()
		condor_glidein_desc.executable = working_directory + "/condor_glidein.sh"
		condor_glidein_desc.output = "condor_glidein.$(CLUSTER).$(PROCESS).out"
		condor_glidein_desc.error = "condor_glidein.$(CLUSTER).$(PROCESS).err"

		condor_glidein = open(condor_glidein_desc.executable, "w")
		condor_glidein.write("#!/bin/bash -l\n")
		condor_glidein.write("/bin/date\n")
		condor_glidein.write("NODES=`uniq $PBS_NODEFILE`\n")
		condor_glidein.write("for i in $NODES; do\n")
		condor_glidein.write("ssh $i \"export CONDOR_LOCATION=" + CONDOR_LOCATION + ";")
		condor_glidein.write("source " + CONDOR_LOCATION + "/condor.sh;")
		condor_glidein.write("condor_master\"\n")
		condor_glidein.write("done\n")
		condor_glidein.write("sleep " + str(60*walltime) + "\n")
		condor_glidein.close()

		attr = open(CONDOR_BIN + "/condor_attr", "w")
		attr.write("universe = grid\n")
		attr.write("grid_resource = gt2 " + lrms_url + "\n")
		attr.write("globus_rsl = (project=" + project + ")(maxWallTime=" + str(walltime) + ")(hostCount=" + str(number_nodes) + ")(jobType=single)(queue=" + queue + ")\n")
		attr.write("x509userproxy = " + userproxy + "\n")
		attr.close()

		self.condor_glidein_job = self.job_service.create_job(condor_glidein_desc)
		self.condor_glidein_job.run()

	def get_state(self):
		return self.condor_glidein_job.get_state()

	def add_subjob(self, jd):
		print "add subjob to list"
		job_id = uuid.uuid1()
		sj = self.job_service.create_job(jd)
		job_dict = {}
		job_dict["job_description"] = jd
		job_dict["state"] = saga.job.New
		job_dict["saga_job"] = sj
		self.subjobs[str(job_id)] = job_dict
		sj.run()
		return job_id

	def get_state_of_subjob(self, job_id):
		""" returns state of specified subjob"""
		if self.subjobs.has_key(str(job_id)):
			job_dict = self.subjobs[str(job_id)]
			saga_job = job_dict["saga_job"]
			return saga_job.get_state()
		return None

	def cancel_subjob(self, job_id):
		if self.subjobs.has_key(str(job_id)):
			job_dict = self.subjobs[str(job_id)]
			saga_job = job_dict["saga_job"]
			return saga_job.cancel()
		return None

	""" Release the local Condor pool"""

	def cancel(self):
		self.condor_glidein_job.cancel()
    

class subjob():

	def __init__(self,
		database_host=None,
		bigjob=None):
		""" Constructor"""
		self.bigjob = bigjob
		self.job_url = None
		self.job_id = None

	def submit_job(self, jd):
		""" submit job via condor adaptor to the local Condor pool"""
		print "submit job to " + str(self.bigjob.pilot_url)

		self.job_id = self.bigjob.add_subjob(jd)
		self.job_url = self.bigjob.pilot_url + "/compute/"+ str(self.job_id)

	def get_state(self):
		return self.bigjob.get_state_of_subjob(self.job_id)

	def delete_job(self):
		print "delete subjob: " + self.job_url
		return self.bigjob.cancel_subjob(self.job_id)

	def __del__(self):
		self.delete_job()

	def __repr__(self):
		if self.job_url==None:
			return "None"
		else:
			return self.job_id

















