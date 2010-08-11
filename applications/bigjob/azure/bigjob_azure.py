#!/usr/bin/env python

"""Module bigjob_azure.

This Module is used to launch a set of jobs via a defined set of Azure worker roles. 

Expects configuration file: bigjob_azure.conf in directory of python executable
Use template: bigjob_azure.conf.template for reference
cp bigjob_azure.conf.template bigjob_azure.conf

"""

import sys
sys.path.append("./winazurestorage")

import getopt
import time
import uuid
import pdb
import socket
import os
import traceback
import json
import ConfigParser

# for logging
import logging
logging.basicConfig(level=logging.DEBUG)

# azure storage and service lib
from winazurestorage import *
from winazureservice import *

""" Config parameters (will move to config file in future) """
""" Used as blob storage keys """
APPLICATION_NAME="bigjob"
STATE = "state"
JOB_DESCRIPTION = "jd"
NODE_FILE = "nodefile"

CONFIG_FILE="bigjob_azure.conf"


class bigjob_azure():
    
    def __init__(self, database_host=None):
        
        # read config file
        conf_file =  CONFIG_FILE
        logging.debug("read config file: " + conf_file)
        config = ConfigParser.ConfigParser()
        config.read(conf_file)
        default_dict = config.defaults()
        self.account_name_storage = default_dict["account_name_storage"]
        self.account_name_compute = default_dict["account_name_storage"]
        self.secret_key = default_dict["secret_key"]
        self.user_certificate = default_dict["user_certificate"]
        self.subscription_id = default_dict["subscription_id"]
                
        logging.debug("init azure storage: blob and queue") 
        self.uuid = str(uuid.uuid1())        
        self.app_id = APPLICATION_NAME
        self.blob = BlobStorage(host = "blob.core.windows.net", 
                             account_name = self.account_name_storage, 
                             secret_key = self.secret_key)
        result = self.blob.create_container(self.app_id)
        logging.debug("Result of pilot job blob container creation: " + str(result))
        
        self.queue = QueueStorage(host = "queue.core.windows.net", 
                             account_name = self.account_name_storage, 
                             secret_key = self.secret_key)
        
        result = self.queue.create_queue(self.app_id)
        logging.debug("Result of pilot job queue creation: " + str(result))
        
        self.app_url=self.blob.get_base_url()+"/"+self.app_id
        logging.debug("created azure blob: " + self.app_url)
    
    def start_azure_worker_roles(self, number=1):
        h = HostedService(self.subscription_id, self.user_certificate); 
        requestId = h.createDeployment( self.account_name_compute, APPLICATION_NAME, "staging", 
                       "http://saga.blob.core.windows.net/namd-service/BigJobService.cspkg",
                       "BigJobService/deploy/ServiceConfiguration.cscfg")
        # wait for deployment to be done
        status = h.waitForRequest(requestId);
    
        if status != "Succeeded":
            logging.debug("Deployment Failed")
            return
    
        # change status to running    
        logging.debug("Setting deployment status to Running")
        requestId = h.updateDeploymentStatus(self.account_name_compute, "staging", "Running")
        status = h.waitForRequest(requestId);
        
    def stop_azure_worker_roles(self):
        logging.debug("Deleting deployment")
        requestId = h.updateDeploymentStatus(self.account_name_compute, "staging", "Suspended")
        status = h.waitForRequest(requestId)
    
        requestId = h.deleteDeployment(self.account_name_compute, "staging")    
        status = h.waitForRequest(requestId)     
    
    def start_pilot_job(self, 
                 lrms_url=None,                     # in future version one can specify a URL for a cloud (ec2:// vs. nimbus:// vs. eu://)
                 bigjob_agent_executable=None,      # n/a
                 number_nodes=1,                    # number of images requested    
                 queue=None,                        # n/a
                 project=None,                      # n/a
                 working_directory=None,            # working directory
                 userproxy=None,                    # optional: path to user credential (X509 cert or proxy cert)
                 walltime=None,                     # optional: walltime
                 cloud_type=None,
                 image_name=None):   
     
        self.pilot_url = self.app_url
        #update state blob
        self.blob.put_blob(self.app_id, STATE, str(state.Unknown), "text/plain")
        logging.debug("set pilot state to: " + str(state.Unknown))
 
        # use service management api to spawn azure images
        logging.debug("init azure worker roles") 
        self.start_azure_worker_roles(number_nodes)
     
    def get_state(self):        
        return self.blob.get_blob(self.app_id, STATE)
    
    def get_state_detail(self): 
        return self.blob.get_blob(self.app_id, STATE)
    
    def cancel(self):        
        print "Cancel Pilot Job"        
        self.queue.put_message(self.app_id, "STOP")
        self.blob.delete_container(self.app_id)
        self.stop_azure_worker_roles()
        
        
    def add_subjob(self, jd):
        logging.debug("add subjob to queue")
        job_id = "subjob-" + str(uuid.uuid1())
        json_jd = json.dumps(self.create_jd_json(jd))
        logging.debug(json_jd)
        # create subjob blob
        result1 = self.blob.put_blob(self.app_id, job_id, json_jd, "text/plain")
        # create queue message for subjob
        result2 = self.queue.put_message(self.app_id, job_id)
        logging.debug ("Results: subjob blob creation: " +str(result1) 
                       + " subjob queue message: " + str(result2))
        return job_id 
    
    def get_subjob_state(self, job_id):
        json_jd = self.blob.get_blob(self.app_id, job_id)  
        jd_dict = json.loads(json_jd)
        return jd_dict["state"]
    
    def delete_subjob(self, job_id):
        # winazurestorage currently does not support the deletion of blobs
        pass
    
    def create_jd_json(self, jd):
        jd_dict = {}
        attributes = jd.list_attributes()                
        for i in attributes:          
               if jd.attribute_is_vector(i):
                   jd_dict[i]=jd.get_vector_attribute(i)
               else:
                   logging.debug("Add attribute: " + str(i) + " Value: " + jd.get_attribute(i))
                   jd_dict[i] = jd.get_attribute(i)
        # state should be stored as metadata to avoid that the entire blob must
        # be read (not supported by winazurestorage yet)
        jd_dict["state"] = str(state.Unknown)       
        return jd_dict

    def __repr__(self):
        return self.pilot_url 

    def __del__(self):
        self.cancel()

                   
                    
class subjob():
    
    def __init__(self, 
                 database_host=None,
                 bigjob=None):
        """Constructor"""
        self.bigjob=bigjob
        self.job_url=None
        self.job_id=None
 
    def submit_job(self, jd):
        """ submit job via Azure queue and Azure agent
            dest_url - url reference to advert job or host on which the advert job is going to run"""
        print "submit job: " + str(self.bigjob)
        #queue subjob add bigjob
        self.job_id=self.bigjob.add_subjob(jd)
        self.job_url=self.bigjob.pilot_url + "/"+ str(self.job_id)
        
    def get_state(self):        
        """ duck typing for get_state of saga.cpr.job and saga.job.job  """
        return self.bigjob.get_subjob_state(self.job_id)
    
    def delete_job(self):
        print "delete job: " + self.job_url
        try:
            self.bigjob.delete_subjob(self.job_id)
        except:
            pass

    def __del__(self):
        self.bigjob.delete_subjob(self.job_id)
    
    def __repr__(self):        
        if(self.job_url==None):
            return "None"
        else:
            return self.job_url

class description():
    def __init__(self):
        self.executable = ""
        self.number_of_processes = ""
        self.spmd_variation = ""
        self.arguments = []
        self.working_directory = ""
        self.output = ""
        self.error = ""
                    
class state():
   Unknown = "Unknown"
    
        