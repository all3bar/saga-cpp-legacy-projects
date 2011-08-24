#!/usr/bin/env python

"""Module many_job.

This Module is used to launch a set of bigjobs.

"""

import sys
import getopt
import saga
import time
import pdb
import os
import traceback
import logging


# BigJob implementation can be swapped here by importing another implementation,
# e.g. condor, cloud, azure
import sys

if os.getenv("BIGJOB_HOME")!=None:
    BIGJOB_HOME= os.getenv("BIGJOB_HOME") 
else:
    BIGJOB_HOME= os.getcwd() + "/../"
    os.environ["BIGJOB_HOME"]=BIGJOB_HOME

sys.path.insert(0, BIGJOB_HOME)
from bigjob import *
import many_job

    
NUMBER_JOBS=8

def has_finished(state):
        state = state.lower()
        if state=="done" or state=="failed" or state=="canceled":
            return True
        else:
            return False

""" Test Job Submission via ManyJob abstraction """
if __name__ == "__main__":
    try:
        print "ManyJob load test with " + str(NUMBER_JOBS) + " jobs."
        starttime=time.time()

        # submit via mj abstraction
        #resource_dictionary = {"resource_url" : "fork://localhost/", "number_nodes" : "32", "processes_per_node":"1", "allocation" : None, "queue" : None, "bigjob_agent": (BIGJOB_HOME + "/bigjob_agent_launcher.sh"), "working_directory": (os.getcwd() + "/agent"), "walltime":3600 }
        resource_list = []
        resource_list.append( {"resource_url" : "gram://louie1.loni.org/jobmanager-pbs", "processes_per_node":"4","number_nodes" : "1", "allocation" : None, "queue" : "workq", "bigjob_agent": (BIGJOB_HOME + "/bigjob_agent_launcher.sh"), "working_directory": (os.getcwd() + "/agent"), "walltime":10 })

        #resource_list.append(resource_dictionary)
        #resource_list.append( {"resource_url" : "pbspro://localhost/", "number_nodes" : "2", "processes_per_node":"4", "allocation" : "loni_jhabig12", "queue" : None, "bigjob_agent": (BIGJOB_HOME + "/bigjob_agent_launcher.sh"), 
        #                       "working_directory": (os.getcwd() + "/agent"), "walltime":3600 })

        #Flags for controlling dynamic BigJob
        add_additional_resources=False
        remove_additional_resources=False
        

        print "Create manyjob service "
        mjs = many_job.many_job_service(resource_list, "advert.cct.lsu.edu")
        
        jobs = []
        job_start_times = {}
        job_states = {}
        cwd = os.getcwd()
        for i in range(0, NUMBER_JOBS):
            # create job description
            jd = saga.job.description()
            jd.executable = "/bin/date"
            jd.number_of_processes = "1"
            jd.spmd_variation = "single"
            jd.arguments = [""]
            jd.working_directory = os.getcwd();
            jd.output =  "stdout-" + str(i) + ".txt"
            jd.error = "stderr-" + str(i) + ".txt"
            subjob = mjs.create_job(jd)
            subjob.run()
            print "Submited sub-job " + "%d"%i + "."
            jobs.append(subjob)
            job_start_times[subjob]=time.time()
            job_states[subjob] = subjob.get_state()
        print "************************ All Jobs submitted ************************"
        while 1: 
            finish_counter=0
            result_map = {}
            for i in range(0, NUMBER_JOBS):
                old_state = job_states[jobs[i]]
                state = jobs[i].get_state()
                if result_map.has_key(state) == False:
                    result_map[state]=0
                result_map[state] = result_map[state]+1
                #print "counter: " + str(i) + " job: " + str(jobs[i]) + " state: " + state
                if old_state != state:
                    print "Job " + str(jobs[i]) + " changed from: " + old_state + " to " + state
                if old_state != state and has_finished(state)==True:
                     print "Job: " + str(jobs[i]) + " Runtime: " + str(time.time()-job_start_times[jobs[i]]) + " s."
                if has_finished(state)==True:
                     finish_counter = finish_counter + 1
                job_states[jobs[i]]=state
                
            # Dynamic BigJob add resources at runtime
            # if more than 30 s - add additional resource
            if time.time()-starttime > 10 and add_additional_resources==True:
                print "***add additional resources***"
                mjs.add_resource(resource_dictionary)
                add_additional_resources=False  
                
            # remove resources from dynamic bigjob
            if (time.time()-starttime > 15 and remove_additional_resources==True):
                bj_list = mjs.get_resources()
                if len(bj_list)>0:
                    print "***remove resources: " + str(bj_list[0])
                    mjs.remove_resource(bj_list[0])
                remove_additional_resources=False
                
            print "Current states: " + str(result_map) 
            time.sleep(5)
            if finish_counter == NUMBER_JOBS:
                break

        mjs.cancel()
        runtime = time.time()-starttime
        print "Runtime: " + str(runtime) + " s; Runtime per Job: " + str(runtime/NUMBER_JOBS)
    except:
        traceback.print_exc(file=sys.stdout)
        try:
            mjs.cancel()
        except:
            pass

