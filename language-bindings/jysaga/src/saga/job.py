# Package: pysaga
# Module: job 
# Description: The module which specifies the classes needed for running jobs
# Specification and documentation can be found in section 3.2, page 164-194 
#    of the GFD-R-P.90 document
# Author: P.F.A. van Zoolingen, Computer Systems Section, Faculty of 
#    Exact Science (FEW), Vrije Universiteit, Amsterdam, The Netherlands.

from saga.object import Object, ObjectType
from saga.attributes import Attributes
from saga.task import Async, Task, TaskType
from saga.monitoring import Steerable
from saga.permissions import Permissions
from saga.error import NotImplemented, PermissionDenied
from saga.url import URL
from saga.session import Session

import org.ogf.saga.error.AlreadyExistsException
import org.ogf.saga.error.AuthenticationFailedException 
import org.ogf.saga.error.AuthorizationFailedException
import org.ogf.saga.error.BadParameterException 
import org.ogf.saga.error.DoesNotExistException
import org.ogf.saga.error.IncorrectStateException
import org.ogf.saga.error.IncorrectURLException 
import org.ogf.saga.error.NoSuccessException 
import org.ogf.saga.error.NotImplementedException
import org.ogf.saga.error.PermissionDeniedException
import org.ogf.saga.error.SagaException 
import org.ogf.saga.error.SagaIOException 
import org.ogf.saga.error.TimeoutException
import java.io.InputStream
import java.io.OutputStream
import java.io.IOException
import java.lang.String

import array.array

from org.ogf.saga.job import JobFactory
import org.ogf.saga.job.JobService
import org.ogf.saga.job.JobDescription
import org.ogf.saga.job.Job
import org.ogf.saga.job.JobSelf



class State(object):
    """
    The state is equivalent to task.State, but adds the SUSPENDED state:
    
    @version: 1.0, designed for Python 2.x
    
    """
   
    NEW = 1
    """
        @summary: this state identifies a newly constructed Task instance which 
        has not yet run. This state corresponds to the BES state 'Pending'. 
        This state is initial.
    """
    
    RUNNING = 2
    """
    @summary: the run() method has been invoked on the Task, either explicitly 
        or implicitly. This state corresponds to the BES state 'Running'. This
        state is initial
    """
        
    DONE = 3
    """
    @summary: the synchronous or asynchronous operation has finished 
        successfully. It corresponds to the BES state 'Finished'. This state is 
        final.
    """
        
    CANCELED = 4
    """
    @summary: the asynchronous operation has been canceled, i.e. cancel() has 
        been called on the Task instance. It corresponds to the BES state 
        'Canceled'. This state is final.
    """
        
    FAILED = 5
    """
    @summary: the synchronous or asynchronous operation has finished 
        unsuccessfully. It corresponds to the BES state 'Failed'. This state is 
        final.
    """
        
    SUSPENDED = 6
    """
    @summary: This state identifies a job instance which has been suspended.
        This state corresponds to the BES state 'Suspend'.
    """


class JobDescription(Object,Attributes):
    """
    This object encapsulates all the attributes which define a job to be run.
    It has no methods of its own, but implements the L{Attributes}
    interface in order to provide access to the job properties, 
    which are expressed as JSDL keywords.
    
    B{Attributes:}
    
        - B{Executable}
            - name: Executable
            - desc: command to execute.
            - type: String
            - mode: ReadWrite
            - value: ""
            - notes: 
                - this is the only required attribute.
                - can be a full pathname, or a pathname relative to the 
                    'WorkingDirectory' as evaluated on the execution host.
                - semantics as defined in JSDL
                - available in JSDL, DRMAA
        - B{Arguments}
            - name:  Arguments
            - desc:  positional parameters for the command.
            - mode:  ReadWrite, optional
            - type:  List of Strings
            - value: -
            - notes: 
               - semantics as specified by JSDL
               - available in JSDL, DRMAA
        - B{SPMDVariation}
            - name:  SPMDVariation
            - desc:  SPMD job type and startup mechanism
            - mode:  ReadWrite, optional
            - type:  String
            - value: -
            - notes: 
                - the SPMD JSDL extension defines the value to be an URI. For 
                    simplicity, SAGA allows the following strings, which map 
                    into the respective URIs: MPI, GridMPI, IntelMPI, LAM-MPI, 
                    MPICH1, MPICH2, MPICH-GM, MPICH-MX, MVAPICH, MVAPICH2, 
                    OpenMP, POE, PVM, None
            - the value '' (no value, default) indicates that the application is
                not a SPMD application.
            - as JSDL, SAGA allows other arbitrary values.
        - B{TotalCPUCount}
            - name:  TotalCPUCount
            - desc:  total number of cpus requested for this job 
            - mode:  ReadWrite, optional
            - type:  Int
            - value: '1'
            - notes: 
                - semantics as defined in JSDL.
                - available in JSDL, DRMAA
        - B{NumberOfProcesses}
            - name:  NumberOfProcesses
            - desc:  total number of processes to be started
            - mode:  ReadWrite, optional
            - type:  Int
            - value: '1'
            - notes: 
               - semantics as defined in JSDL
               - available in JSDL, SPMD extension
        - B{ProcessesPerHost}
            - name:  ProcessesPerHost
            - desc:  number of processes to be started per host
            - mode:  ReadWrite, optional
            - type:  Int
            - value: '1'
            - notes: 
                - semantics as defined in JSDL
                - available in JSDL, SPMD extension
        - B{ThreadsPerProcess}
            - name:  ThreadsPerProcess
            - desc:  number of threads to start per process
            - mode:  ReadWrite, optional
            - type:  Int
            - value: '1'
            - notes: 
                - semantics as defined in JSDL
                - available in JSDL, SPMD extension
        - B{Environment}
            - name:  Environment
            - desc:  set of environment variables for the job
            - mode:  ReadWrite, optional
            - type:  List of Strings
            - value: -
            - notes: 
                - exported into the job environment
                - format: 'key=value'
                - semantics as specified by JSDL
                - available in JSDL, DRMAA
        - B{WorkingDirectory}
            - name:  WorkingDirectory
            - desc:  working directory for the job
            - mode:  ReadWrite, optional
            - type:  String
            - value: '.'
            - note: semantics as specified by JSDL
            - available in JSDL, DRMAA
        - B{Interactive}
            - name:  Interactive
            - desc:  run the job in interactive mode
            - mode:  ReadWrite, optional
            - type:  Bool
            - value: 'False'
            - notes: 
                - this implies that stdio streams will stay connected to the 
                    submitter after job submission, and during job execution.
                - if an implementation cannot handle interactive jobs, and this 
                    attribute is present, and 'True', the job creation 
                    raises an 'IncorrectParameter' error with a descriptive error 
                    message.
                - not supported by JSDL, DRMAA
        - B{Input}
            - name:  Input
            - desc:  pathname of the standard input file
            - mode:  ReadWrite, optional
            - type:  String
            - value: -
            - notes: 
                - semantics as specified by JSDL
                - available in JSDL, DRMAA
                - will not be used if 'Interactive' is 'True'
        - B{Output}
            - name:  Output
            - desc:  pathname of the standard output file
            - mode:  ReadWrite, optional
            - type:  String
            - value: -
            - notes: 
                - semantics as specified by JSDL
                - available in JSDL, DRMAA
                - will not be used if 'Interactive' is 'True'
        - B{Error}
            - name:  Error
            - desc:  pathname of the standard error file
            - mode:  ReadWrite, optional
            - type:  String
            - value: -
            - notes: 
                - semantics as specified by JSDL
                - available in JSDL, DRMAA
                - will not be used if 'Interactive' is 'True'
        - B{FileTransfer}
            - name:  FileTransfer
            - desc:  a list of file transfer directives
            - mode:  ReadWrite, optional
            - type:  List of Strings
            - value: -
            - notes: 
                - translates into jsdl:DataStaging
                - used to specify pre- and post-staging
                - semantics as specified in JSDL
                - staging is part of the 'Running' state
                - syntax similar to LSF (see earlier notes)
                - available in JSDL, DRMAA
        - B{Cleanup}
            - name: Cleanup
            - desc: defines if output files get removed after the job finishes
            - mode: ReadWrite, optional
            - type: String
            - value: 'Default'
            - notes: 
                - can have the Values 'True', 'False', and 'Default'
                - On 'False', output files are kept after job the finishes
                - On 'True', output files are deleted after job the finishes
                - On 'Default', the behaviour is defined by the implementation 
                    or the backend.
                - translates into 'DeleteOnTermination' elements in JSDL
        - B{JobStartTime}
            - name:  JobStartTime
            - desc:  time at which a job should be scheduled
            - mode:  ReadWrite, optional
            - type:  Int
            - value: -
            - notes: 
                - Could be viewed as a desired job start time, but that is up to 
                    the resource manager.
                - format: number of seconds since epoch
                - available in DRMAA
                - not supported by JSDL
        - B{TotalCPUTime}
            - name:  TotalCPUTime
            - desc:  estimate total number of CPU seconds which the job will 
                require.
            - mode: ReadWrite, optional
            - type: Int
            - value: -
            - notes: 
                - intended to provide hints to the scheduler for scheduling
                    policies.
                - available in JSDL, DRMAA
                - semantics as defined in JSDL
        - B{TotalPhysicalMemory}
            - name:  TotalPhysicalMemory
            - desc:  Estimated amount of memory the job requires
            - mode:  ReadWrite, optional
            - type: Float
            - value: -
            - notes: 
                - unit is in MegaByte
                - memory usage of the job is aggregated across all processes 
                    of the job
                - semantics as defined by JSDL
                - available in JSDL
        - B{CPUArchitecture}
            - name:  CPUArchitecture
            - desc:  compatible processor for job submission
            - mode:  ReadWrite, optional
            - type:  List of Strings
            - value: -
            - notes: 
                - allowed values as specified in JSDL
                - semantics as defined by JSDL
                - available in JSDL
        - B{OperatingSystemType}
            - name:  OperatingSystemType
            - desc:  compatible operating system for job submission
            - mode:  ReadWrite, optional
            - type:  List of strings
            - value: -
            - notes: 
                - allowed values as specified in JSDL
                - semantics as defined by JSDL
                - available in JSDL
        - B{CandidateHosts}
            - name:  CandidateHosts
            - desc:  list of host names which are to be considered by the 
                resource manager as candidate targets
            - mode: ReadWrite, optional
            - type: List of strings
            - value: -
            - notes: 
                - semantics as defined by JSDL
                - available in JSDL
        - B{Queue}
            - name:  Queue
            - desc:  name of a queue to place the job into
            - mode:  ReadWrite, optional
            - type:  String
            - value: -
            - notes: 
                - While SAGA itself does not define the semantics of a "queue", 
                    many backend systems can make use of this attribute.
                - not supported by JSDL
        - B{JobContact}
            - name: JobContact
            - desc: set of endpoints describing where to report job state 
                transitions.
            - mode: ReadWrite, optional
            - type: List of Strings 
            - value: -
            - notes: 
                - format: URI (e.g. fax:+123456789, sms:+123456789, 
                    mailto:joe@doe.net).
                - available in DRMAA
                - not supported by JSDL    
     
    @summary: This object encapsulates all the attributes which define a job 
        to be run.            
    @version: 1.0, designed for Python 2.x

    @undocumented: get_Executable
    @undocumented: set_Executable
    @undocumented: del_Executable
    
    @undocumented: get_Arguments
    @undocumented: set_Arguments
    @undocumented: del_Arguments
    
    @undocumented: get_SPMDVariation
    @undocumented: set_SPMDVariation
    @undocumented: del_SPMDVariation
    
    @undocumented: get_TotalCPUCount
    @undocumented: set_TotalCPUCount
    @undocumented: del_TotalCPUCount
    
    @undocumented: get_NumberOfProcesses
    @undocumented: set_NumberOfProcesses
    @undocumented: del_NumberOfProcesses
    
    @undocumented: get_ProcessesPerHost
    @undocumented: set_ProcessesPerHost
    @undocumented: del_ProcessesPerHost
    
    @undocumented: get_ThreadsPerProcess
    @undocumented: set_ThreadsPerProcess
    @undocumented: del_ThreadsPerProcess
    
    @undocumented: get_Environment
    @undocumented: set_Environment
    @undocumented: del_Environment
    
    @undocumented: get_WorkingDirectory
    @undocumented: set_WorkingDirectory
    @undocumented: del_WorkingDirectory
    
    @undocumented: get_Interactive
    @undocumented: set_Interactive
    @undocumented: del_Interactive
    
    @undocumented: get_Input
    @undocumented: set_Input
    @undocumented: del_Input
    
    @undocumented: get_Output
    @undocumented: set_Output
    @undocumented: del_Output
    
    @undocumented: get_Error
    @undocumented: set_Error
    @undocumented: del_Error
    
    @undocumented: get_FileTransfer
    @undocumented: set_FileTransfer
    @undocumented: del_FileTransfer
    
    @undocumented: get_Cleanup
    @undocumented: set_Cleanup
    @undocumented: del_Cleanup
    
    @undocumented: get_JobStartTime
    @undocumented: set_JobStartTime
    @undocumented: del_JobStartTime
    
    @undocumented: get_TotalCPUTime
    @undocumented: set_TotalCPUTime
    @undocumented: del_TotalCPUTime
    
    @undocumented: get_TotalPhysicalMemory
    @undocumented: set_TotalPhysicalMemory
    @undocumented: del_TotalPhysicalMemory
    
    @undocumented: get_CPUArchitecture
    @undocumented: set_CPUArchitecture
    @undocumented: del_CPUArchitecture
    
    @undocumented: get_OperatingSystemType
    @undocumented: set_OperatingSystemType
    @undocumented: del_OperatingSystemType
    
    @undocumented: get_CandidateHosts
    @undocumented: set_CandidateHosts
    @undocumented: del_CandidateHosts
    
    @undocumented: get_Queue
    @undocumented: set_Queue
    @undocumented: del_Queue
    
    @undocumented: get_JobContact
    @undocumented: set_JobContact
    @undocumented: del_JobContact
    """


    def __init__(self, **impl):
        """Initialize the object.
        
        @summary: initialize the object.
        @Raise NotImplemented:
        @raise NoSuccess:
        @Note:    a JobDescription is not associated with a Session, 
            but can be used for JobServices from different sessions.
        
        """
		
        self.delegateObject = None
        if "delegateObject" in impl:
            if not isinstance(impl["delegateObject"], org.ogf.saga.job.JobDescription):
                raise BadParameter,"Parameter impl[\"delegateObject\"] is not" \
                    + " a org.ogf.saga.job.JobDescription. Type: " \
                    + str(impl["delegateObject"].__class__)
            self.delegateObject = impl["delegateObject"]
            return
        else:
            try:
                self.delegateObject = JobFactory.createJobDescription()
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)
          

    def __set_Executable(self, value):
        self.set_attribute("Executable", value)
        
    def __get_Executable(self):
        return self.get_attribute("Executable")  
    
    def __del_Executable(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("Executable", "")            

    Executable = property(__get_Executable, __set_Executable, __del_Executable, 
            doc="""The Executable attribute. 
                @type:string""")

    def __set_Arguments(self, value):
        self.set_vector_attribute("Arguments", value)
        
    def __get_Arguments(self):
        return self.get_vector_attribute("Arguments")  
    
    def __del_Arguments(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_vector_attribute("Arguments", [])            

    Arguments = property(__get_Arguments, __set_Arguments, __del_Arguments, 
            doc="""The Arguments attribute. 
                @type:List of strings""")
     
    def __set_SPMDVariation(self, value):
        self.set_attribute("SPMDVariation", value)
        
    def __get_SPMDVariation(self):
        return self.get_attribute("SPMDVariation")  
    
    def __del_SPMDVariation(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("SPMDVariation", "")            

    SPMDVariation = property(__get_SPMDVariation, __set_SPMDVariation,
                             __del_SPMDVariation,
                             """The SPMDVariation attribute. 
                             @type: string""")
     
    def __set_TotalCPUCount(self, value):
        self.set_attribute("TotalCPUCount", value)
        
    def __get_TotalCPUCount(self):
        return self.get_attribute("TotalCPUCount")  
    
    def __del_TotalCPUCount(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("TotalCPUCount", "1")            

    TotalCPUCount = property(__get_TotalCPUCount, __set_TotalCPUCount,
                             __del_TotalCPUCount, 
                             """The TotalCPUCount attribute. \n@type: string""")

    def __set_NumberOfProcesses(self, value):
        self.set_attribute("NumberOfProcesses", value)
        
    def __get_NumberOfProcesses(self):
        return self.get_attribute("NumberOfProcesses")  
    
    def __del_NumberOfProcesses(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("NumberOfProcesses", "1")            

    NumberOfProcesses = property(__get_NumberOfProcesses,
                                 __set_NumberOfProcesses, 
                                 __del_NumberOfProcesses, 
                                 """The NumberOfProcesses attribute. 
                                 \n@type: string""")
     
    def __set_ProcessesPerHost(self, value):
        self.set_attribute("ProcessesPerHost", value)
        
    def __get_ProcessesPerHost(self):
        return self.get_attribute("ProcessesPerHost")  
    
    def __del_ProcessesPerHost(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("ProcessesPerHost", "1")            

    ProcessesPerHost = property(__get_ProcessesPerHost, __set_ProcessesPerHost,
                                __del_ProcessesPerHost, 
                                """The ProcessesPerHost attribute. 
                                \n@type: string""")


    def __set_ThreadsPerProcess(self, value):
        self.set_attribute("ThreadsPerProcess", value)
        
    def __get_ThreadsPerProcess(self):
        return self.get_attribute("ThreadsPerProcess")  
    
    def __del_ThreadsPerProcess(self):
        raise NotImplemented("Attribute cannot be deleted")        
        #self.set_attribute("ThreadsPerProcess", "1")            

    ThreadsPerProcess = property(__get_ThreadsPerProcess, 
                                 __set_ThreadsPerProcess, 
                                 __del_ThreadsPerProcess, 
                                 """The ThreadsPerProcess attribute. 
                                 \n@type: string""")
     
    def __set_Environment(self, value):
        self.set_vector_attribute("Environment", value)
        
    def __get_Environment(self):
        return self.get_vector_attribute("Environment")  
    
    def __del_Environment(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_vector_attribute("Environment", [])            

    Environment = property(__get_Environment, __set_Environment, 
                           __del_Environment,
                           """The Environment attribute. 
                           \n@type:List of strings""")

    def __set_WorkingDirectory(self, value):
        self.set_attribute("WorkingDirectory", value)
        
    def __get_WorkingDirectory(self):
        return self.get_attribute("WorkingDirectory")  
    
    def __del_WorkingDirectory(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("WorkingDirectory", "")            

    WorkingDirectory = property(__get_WorkingDirectory, __set_WorkingDirectory, 
                                __del_WorkingDirectory, 
                                """The WorkingDirectory attribute. 
                                \n@type: string""")

    def __set_Interactive(self, value):
        self.set_attribute("Interactive", value)
        
    def __get_Interactive(self):
        return self.get_attribute("Interactive")  
    
    def __del_Interactive(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("Interactive", "False")            

    Interactive = property(__get_Interactive, __set_Interactive, 
                           __del_Interactive, 
                           """The Interactive attribute. \n@type: string""")

    def __set_Input(self, value):
        self.set_attribute("Input", value)
        
    def __get_Input(self):
        return self.get_attribute("Input")  
    
    def __del_Input(self):
        raise NotImplemented("Attribute cannot be deleted")        
        #self.set_attribute("Input", "")            

    Input = property(__get_Input, __set_Input, __del_Input, 
            """The Input attribute. \n@type: string""")
     
    def __set_Output(self, value):
        self.set_attribute("Output", value)
        
    def __get_Output(self):
        return self.get_attribute("Output")  
    
    def __del_Output(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("Output", "")            

    Output = property(__get_Output, __set_Output, __del_Output, 
            doc="""The Output attribute. \n@type: string""")

    def __set_Error(self, value):
        self.set_attribute("Error", value)
        
    def __get_Error(self):
        return self.get_attribute("Error")  
    
    def __del_Error(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("Error", "")            

    Error = property(__get_Error, __set_Error, __del_Error, 
            doc="""The Error attribute. \n@type: string""")
     
    def __set_FileTransfer(self, value):
        self.set_vector_attribute("FileTransfer", value)
        
    def __get_FileTransfer(self):
        return self.get_vector_attribute("FileTransfer")  
    
    def __del_FileTransfer(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_vector_attribute("FileTransfer", [])            

    FileTransfer = property(__get_FileTransfer, __set_FileTransfer, 
                            __del_FileTransfer, 
                            """The FileTransfer attribute. 
                                @type: list ofstring""")
    
    def __set_Cleanup(self, value):
        self.set_attribute("Cleanup", value)
        
    def __get_Cleanup(self):
        return self.get_attribute("Cleanup")  
    
    def __del_Cleanup(self):
        raise NotImplemented("Attribute cannot be deleted")        
        #self.set_attribute("Cleanup", "Default")            

    Cleanup = property(__get_Cleanup, __set_Cleanup, __del_Cleanup, 
            doc="""The Cleanup attribute. \n@type: string""")
     
    def __set_JobStartTime(self, value):
        self.set_attribute("JobStartTime", value)
        
    def __get_JobStartTime(self):
        return self.get_attribute("JobStartTime")  
    
    def __del_JobStartTime(self):
        raise NotImplemented("Attribute cannot be deleted")       
        #self.set_attribute("JobStartTime", "0")            

    JobStartTime = property(__get_JobStartTime, __set_JobStartTime, 
                            __del_JobStartTime, 
                            """The JobStartTime attribute. \n@type: string""")

    def __set_TotalCPUTime(self, value):
        self.set_attribute("TotalCPUTime", value)
        
    def __get_TotalCPUTime(self):
        return self.get_attribute("TotalCPUTime")  
    
    def __del_TotalCPUTime(self):
        raise NotImplemented("Attribute cannot be deleted")        
        #self.set_attribute("TotalCPUTime", "0")            

    TotalCPUTime = property(__get_TotalCPUTime, __set_TotalCPUTime, 
                            __del_TotalCPUTime, 
                            """The TotalCPUTime attribute. \n@type: string""")
    def __set_TotalPhysicalMemory(self, value):
        self.set_attribute("TotalPhysicalMemory", value)
        
    def __get_TotalPhysicalMemory(self):
        return self.get_attribute("TotalPhysicalMemory")  
    
    def __del_TotalPhysicalMemory(self):
        raise NotImplemented("Attribute cannot be deleted")        
        #self.set_attribute("TotalPhysicalMemory", "0")            

    TotalPhysicalMemory = property(__get_TotalPhysicalMemory, 
                                   __set_TotalPhysicalMemory, 
                                   __del_TotalPhysicalMemory, 
                                   """The TotalPhysicalMemory attribute. \n
                                   @type: string""")
     
               
    def __set_CPUArchitecture(self, value):
        self. set_vector_attribute("CPUArchitecture", value)
        
    def __get_CPUArchitecture(self):
        return self.get_vector_attribute("CPUArchitecture")  
    
    def __del_CPUArchitecture(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_vector_attribute("CPUArchitecture", [])

    CPUArchitecture = property(__get_CPUArchitecture, __set_CPUArchitecture, 
                               __del_CPUArchitecture, 
                               """The CPUArchitecture attribute. \n
                               @type:List of strings""")
     
    def __set_OperatingSystemType(self, value):
        self.set_vector_attribute("OperatingSystemType", value)
        
    def __get_OperatingSystemType(self):
        return self.get_vector_attribute("OperatingSystemType")  
    
    def __del_OperatingSystemType(self):
        raise NotImplemented("Attribute cannot be deleted")       
        #self.set_vector_attribute("OperatingSystemType", [])

    OperatingSystemType = property(__get_OperatingSystemType, 
                                   __set_OperatingSystemType, 
                                   __del_OperatingSystemType, 
                                   """The OperatingSystemType attribute. \n
                                   @type:List of strings""")
     
    def __set_CandidateHosts(self, value):
        self.set_vector_attribute("CandidateHosts", value)
        
    def __get_CandidateHosts(self):
        return self.get_vector_attribute("CandidateHosts")  
    
    def __del_CandidateHosts(self):
        raise NotImplemented("Attribute cannot be deleted")       
        #self.set_vector_attribute("CandidateHosts", [])            

    CandidateHosts = property(__get_CandidateHosts, __set_CandidateHosts,
                               __del_CandidateHosts, 
                               """The CandidateHosts attribute. \n
                               @type:List of strings""")

    def __set_Queue(self, value):
        self.set_attribute("Queue", value)
        
    def __get_Queue(self):
        return self.get_attribute("Queue")  
    
    def __del_Queue(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_attribute("Queue", "")            

    Queue= property(__get_Queue, __set_Queue, __del_Queue, 
                     """The Queue attribute. \n@type: string""")
     
    def __set_JobContact(self, value):
        self.set_vector_attribute("JobContact", value)
        
    def __get_JobContact(self):
        return self.get_vector_attribute("JobContact")  
    
    def __del_JobContact(self):
        raise NotImplemented("Attribute cannot be deleted")
        #self.set_vector_attribute("JobContact", [])            

    JobContact = property(__get_JobContact, __set_JobContact, __del_JobContact, 
                          """The JobContact attribute. \n
                          @type:List of strings""")

class JobService(Object, Async):
    """
    The job_service represents a resource management backend, and as such allows 
    to create and submit jobs, and to discover jobs.
    """

#TODO: look for more session/url parameter sets. change them.
#TODO: create ASYNC object creation

    def __init__(self, url="", session=Session(), tasktype=TaskType.NORMAL, **impl):
        """
        Initialize the object
        @summary: Initialize the object
        @param session: session to associate with the object
        @type session: L{Session} 
        @param url: contact url for resource manager
        @type url: L{URL} or string
        @param tasktype: return a normal JobService object or a Task object in a 
            final, RUNNING or NEW state that creates a JobService object.
            By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType} 
        @raise NotImplemented:
        @raise IncorrectURL:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: 'url' defaults to an empty string - in that case, the 
         implementation performs a  resource discovery, or fall back to a 
         fixed value, or find a valid rm contact in any other way. If that is 
         not possible, a BadParameter exception is raised, and indicates 
         that a rm contact string is needed.
        @Note: if the rm identified by the url cannot be contacted (i.e. does 
         not exist), a BadParameter exception is raised.

        """
        if "delegateObject" in impl:
            if not isinstance(impl["delegateObject"], org.ogf.saga.job.JobService):
                raise BadParameter,"Parameter impl[\"delegateObject\"] is not" \
                    + " a org.ogf.saga.job.JobService. Type: " \
                    + str(impl["delegateObject"].__class__)
            self.delegateObject = impl["delegateObject"]
            return
        else:
            if type(url) is not str and not isinstance(url, URL): 
                raise BadParameter, "Parameter url is not string or a URL but" \
                    + " a" + str(url.__class__)
            if not isinstance(session, Session):
                raise BadParameter, "Parameter session is not a Session but a "\
                    + str(session.__class__)
            try:
                if url == "": 
                    self.delegateObject = JobFactory.createJobService(session.delegateObject)
                elif isinstance(url,URL):
                    self.delegateObject = JobFactory.createJobService(session.delegateObject, url.delegateObject)
                else:
                    urlObject = URL(url)
                    self.delegateObject = JobFactory.createJobService(session.delegateObject, urlObject.delegateObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)

    def create_job(self, jd, tasktype=TaskType.NORMAL):
        #in JobDescription jd, out job job
        """
        Create a job instance
        @summary: Create a job instance
        @param jd: description of job to be submitted
        @type jd: L{JobDescription} 
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType} 
        @return: a job object representing the submitted job instance
        @rtype: L{Job}
        @PreCondition: jd has an 'Executable' attribute.
        @PostCondition: job is in 'New' state
        @PostCondition: jd is deep copied (no state is shared after method 
            invocation)
        @PostCondition: 'Owner' of the job is the id of the context used for 
            creating the job.
        @raise NotImplemented:
        @raise BadParameter:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: calling run() on the job will submit it to the resource, and 
            advance its state.
        @Note: if the job description does not have a valid 'Executable' 
            attribute, a BadParameter exception is raised.
        @Note: if the job description contains values which are outside of 
            the allowed range, or cannot be parsed, or are otherwise invalid 
            and not usable for creating a job instance, a BadParameter exception 
            is raised, which indicates which attribute(s) caused this 
            exception, and why.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
        
        #Normal, synchronous create_job()
        if tasktype == TaskType.NORMAL:
            if not isinstance(jd, JobDescription):
                raise BadParameter, "Parameter jd is not a JobDescription, but"\
                " a" + str(jd.__class__)
            try:
                javaObject = self.delegateObject.createJob(jd.delegateObject)
                return Job(delegateObject=javaObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)
        
        #Asynchronous create_job()
        else:
            if not isinstance(jd, JobDescription):
                bp = BadParameter("Parameter jd is not a JobDescription, but"\
                " a" + str(jd.__class__))
                return Task(error = bp)
            try:
                if tasktype is TaskType.ASYNC:
                    javaObject = self.delegateObject.createJob(TaskMode.ASYNC, jd.delegateObject)
                if tasktype is TaskType.SYNC:
                    javaObject = self.delegateObject.createJob(TaskMode.SYNC, jd.delegateObject)
                if tasktype is TaskType.TASK:
                    javaObject = self.delegateObject.createJob(TaskMode.TASK, jd.delegateObject)
                return Task(delegateObject=javaObject)                
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)    
                
        
        
    def run_job(self, commandline, host = "", tasktype=TaskType.NORMAL):
        #in string commandline, in string host = "", out job job, 
        #out opaque stdin, out opaque stdout, out opaque stderr
        """
        Run a command synchronously.
        @summary: Run a command synchronously.
        @param commandline: the command and arguments to be run
        @type commandline: string  
        @param host: hostname to be used by rm for submission
        @type host: string
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: tuple of 4 elements: job (L{Job}, a job object representing 
            the submitted job instance), stdin (L{StdIO}, IO handle for the 
            running job's standard input stream), stdout (L{StdIO}, IO handle 
            for the running job's standard output) and stderr (L{StdIO}, IO 
            handle for the running job's standard error
        @rtype: L{Job}, L{StdIO},L{StdIO},L{StdIO}
        @PostCondition: job is in 'Running', 'Done' or 'Failed' state.
        @PostCondition: 'Owner' of the job is the id of the context used for 
            creating the job.
        @raise NotImplemented:
        @raise BadParameter:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: This is a convenience routine built on the create_job method, 
            and is intended to simplify the steps of creating a job_description, 
            creating and running the job, and then querying the standard I/O 
            streams.
        @Note:  the job is guaranteed to run on the given host, or not at all.
        @Note:  the method is exactly equivalent to the sequence of (1) creation 
            of a job_description with 'Executable' set to the values from the
            commandline, 'Interactive' set if I/O is requested, 'CandidateHost' 
            set to host; (2) create_job() with that description; (3) calling 
            run() on that job. This method can raise any of the exceptions 
            which can occur in this sequence, with the semantics defined in
            the detailed description of the methods used in this sequence. 
            No other exception are to be expected.
        @Note:  if 'host' is an empty string (the default), the implementation 
            chooses an arbitrary host for execution.
        @Note: stdin, stdout and stderr are guaranteed to contain/provide the 
            complete standard I/O streams, beginning at the start of the remote 
            process.

        """
        #@Note: the I/O handles have to be passed to the call as references, in 
        #    most languages, as calls often allow only one return value (perl or 
        #    python being notable exceptions). If these parameters are omitted, 
        #    the job is to be started non-interactively, and the output I/O 
        #    streams may be discarded.
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal, synchronous run_job()
        if tasktype == TaskType.NORMAL:               
            if type(commandline) is not str:
                raise BadParameter, "Parameter commandline is not a string but"\
                +" a " + str(commandline.__class__)
            if type(host) is not str:
                raise BadParameter, "Parameter host is not a string but a "\
                    + str(host.__class__)
            try:
                javaJobObject = self.delegateObject.runJob(commandline, host, True)
                returnJob = Job(delegateObject=javaJobObject)
            
                javaStdin = javaJobObject.getStdin() #OutputStream
                returnStdin = StdIO(delegateObject = javaStdin)
        
                javaStdout = javaJobObject.getStdout() #InputStream
                returnStdout = StdIO(delegateObject = javaStdout)
            
                javaStderr = javaJobObject.getStderr() #InputStream
                returnStderr = StdIO(delegateObject = javaStderr)            
        
                return returnJob, returnStdin, returnStdout, returnStderr
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)
        #Asynchronous run_job()
        else:
            if type(commandline) is not str:
                bp = BadParameter("Parameter commandline is not a string but"\
                +" a " + str(commandline.__class__))
                return Task(error = bp)
            
            if type(host) is not str:
                bp = BadParameter, "Parameter host is not a string but a "\
                    + str(host.__class__)
                return Task(error = bp)
            try:
             if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.runJob(TaskMode.ASYNC,commandline,host,True)
             if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.runJob(TaskMode.SYNC,commandline,host,True)
             if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.runJob(TaskMode.TASK,commandline,host,True)
             return Task(delegateObject=javaObject)                
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)              
            
    def list(self, tasktype=TaskType.NORMAL):
        #out array<string>   job_ids
        """
        Get a list of jobs which are currently known by the resource manager.
        @summary: Get a list of jobs which are currently known by the resource 
            manager. 
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: a list of strings representing of job identifiers
        @rtype: list
        @permission: Query on jobs identified by the returned ids
        @raise NotImplemented:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: which jobs are viewable by the calling user context, and how 
            long a resource manager keeps job information, are both 
            implementation dependent.
        @Note: a returned job_id may translate into a job (via get_job()) which 
            is not controllable by the requesting application (e.g. it could 
            cause an 'AuthorizationFailed' exception).

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")" 
        
        #Normal list()
        if tasktype == TaskType.NORMAL:
            try:
                retval = []
                javaList = self.delegateObject.list()
                for i in range(javaList.size()):
                    #retval.append( javaList.get(i).toString() )
                    retval.append( javaList.get(i) )
                return retval
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)
        
        #Asynchronous list()
        else:
            try:
                if tasktype is TaskType.ASYNC:
                    javaObject = self.delegateObject.list(TaskMode.ASYNC)
                if tasktype is TaskType.SYNC:
                    javaObject = self.delegateObject.list(TaskMode.SYNC)
                if tasktype is TaskType.TASK:
                    javaObject = self.delegateObject.list(TaskMode.TASK)
                return Task(delegateObject=javaObject)                
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)                  
        
    
    def get_job (self, job_id, tasktype=TaskType.NORMAL):
        #in  string job_id, out job job
        """
        Given a job identifier, this method returns a Job object 
        representing this job.
        @summary: Given a job identifier, this method returns a Job object 
            representing this job.
        @param job_id: job identifier as returned by the resource manager
        @type job_id: string 
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: a job object representing the job identified by job_id
        @rtype: L{Job} 
        @PreCondition: Job identified by job_id is managed by the job_service.
        @permission: Query on the job.
        @raise NotImplemented:
        @raise BadParameter:
        @raise DoesNotExist:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: in general, only a job_service representing the resource manager 
            which submitted the job may be able to handle the job_id, and to 
            identify the job. However, other job_services may succeed as well.
        @Note: if the resource manager can handle the job_id, but the referenced 
            job is not alive, a 'DoesNotExist' exception is raised.
        @Note: if the resource manager cannot parse the job_id at all, a 
            BadParameter exception is raised.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
                
        #Normal get_job()
        if tasktype == TaskType.NORMAL:
            if type(job_id) is not str:
                raise BadParameter, "Parameter job_id is not a string but a "\
                    + str(host.__class__)
            try:
                javaObject = self.delegateObject.getJob(job_id)
                return Job(delegateObject = javaObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)

        #Asynchronous get_job()
        else:
            if type(job_id) is not str:
                bp = BadParameter("Parameter job_id is not a string but a "\
                    + str(host.__class__))
                return Task(error = bp)
            try:
                if tasktype is TaskType.ASYNC:
                  javaObject = self.delegateObject.getJob(TaskMode.ASYNC,job_id)
                if tasktype is TaskType.SYNC:
                  javaObject = self.delegateObject.getJob(TaskMode.SYNC,job_id)
                if tasktype is TaskType.TASK:
                  javaObject = self.delegateObject.getJob(TaskMode.TASK,job_id)
                return Task(delegateObject=javaObject)                
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)                   
        
    def get_self (self, tasktype=TaskType.NORMAL):
        #out job_self job
        """
        This method returns a Job object representing I{B{this}} job, i.e. the 
        calling application.
        @summary: This method returns a Job object representing I{B{this}} job, 
            i.e. the calling application.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL} 
        @type tasktype: value from L{TaskType}
        @return: a L{JobSelf} object representing I{B{this}} job.
        @rtype: L{JobSelf}
        @PreCondition: the application is managed by the job_service.
        @PostCondition: job_self is, by definition, in 'Running' state.
        @permission: Query on the job.
        @raise NotImplemented:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: in general, only a job_service representing the resource manager 
            which started the application which now calls get_self() can 
            successfully return a job_self instance. However, other job_services 
            may succeed as well.
        @Note: if a job_service cannot handle the calling job as a job_self 
            instance, a 'NoSuccess' exception is raised, with a descriptive 
            error message.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
        
        #Normal get_self()
        if tasktype == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.getSelf()
                return JobSelf(delegateObject = javaObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)

        #Asynchronous get_self()
        else:
            try:
                if tasktype is TaskType.ASYNC:
                  javaObject = self.delegateObject.getSelf(TaskMode.ASYNC)
                if tasktype is TaskType.SYNC:
                  javaObject = self.delegateObject.getSelf(TaskMode.SYNC)
                if tasktype is TaskType.TASK:
                  javaObject = self.delegateObject.getSelf(TaskMode.TASK)
                return Task(delegateObject=javaObject)                
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)               

    def clone(self):
        try:
            javaClone = self.delegateObject.clone()
            clone = JobService( delegateObject = javaClone)
            return clone
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)
        
    def get_type(self):
        return ObjectType.JOBSERVICE
 
class StdIO(object):
    """
    This class is used to give acces to the opaque data like from from stdin, 
    stdout and stderr. This is an extention from the SAGA specification. 
    StdIO supports most operations associated with stdin, stdout and stderr
    but not all methods are available in the same object. For instance:
    if a StdIO object represents the job's stdin, it makes no sense to 
    read from the StdIO object as a stdin cannot generate data. 
    @summary: This class is used to give acces to the opaque data like from 
        stdin, stdout and stderr
    """


    def __init__(self, **impl):
        """
        Initializes the StdIO object. This object can only be created from the
        JobService.run_job() or Job.get_stdin(), Job.get_stdout() and 
        Job.get_stderr()  methods
        @summary: Initializes the StdIO object 
        """
        self.name = None
    	self.delegateObject = None
        self.EOF_reached = None
        if "delegateObject" in impl:
            if not isinstance(impl["delegateObject"],java.io.OutputStream) and \
               not isinstance(impl["delegateObject"],java.io.InputStream):
                raise BadParameter,"Parameter impl[\"delegateObject\"] is not" \
                    + " a java.io.InputStream/OutputStream. Type: " \
                    + str(impl["delegateObject"].__class__)
            self.delegateObject = impl["delegateObject"]
            if "name" in impl:
                if not type(impl["name"]) is str:
                    raise BadParameter,"Parameter impl[\"name\"] is not a " \
                        + "string but a " + str(impl["name"].__class__) 
                self.name =  impl["name"] 
            return
        raise BadParameter, "StdIO objects can only be created through "\
            + "JobService.run_job() or Job.get_stdin(), Job.get_stdout() and "\
            + "Job.get_stderr()"
    # OutputStream belongs to job.getStdin()
    # InputStream  belongs to job.getStdout and job.getStderr()
               
        
    def close(self):
        """
        Closes the stream from reading or writing (if applicable)
        @summary: Closes the stream from reading or writing (if applicable)
        """
        try:
            self.delagateObject.close()
        except java.io.IOException, e:
            raise convertException(e)
    
    def flush(self):
        """
        Forces the datastream to flush the data.
        @summary: Forces the datastream to flush the data
        """
        if isinstance( self.delegateObject, java.io.OutputStream):
            try:
                self.delagateObject.flush()
            except java.io.IOException, e:
                raise convertException(e)
        else:
            pass

    def get_name(self):
        """
        Returns the name of the StdIO object.
        @summary: Returns the name of the StdIO object.
        @return: '<stdin>' if this object represents the stdin of the job,
            '<stdout>' if it represents the stdout of the job or '<stderr>' if
            it represents the stderr of the job
        @rtype: string
        """
        if self.name != None:
            return self.name
        else:
            if isinstance(self.delegateObject, java.io.OutputStream):
                return "<stdin>"
            else:
                return "<undefined_stdout_or_stderr>"
                

    def get_mode(self):
       """
       Returns the mode of the StdIO object
       @summary: Returns the mode of the StdIO object
       @rtype: string
       @return: 'w' if this object represents the stdin of the job,
            'r' if it represents the stdout of the job and 'r' if
            it represents the stderr of the job
       """ 
       if isinstance(self.delegateObject, java.io.OutputStream):
           return "w"
       else:
           return "r"      

    def write(self, data):
        """
        Write data to the stdin of the job.
        @summary: Write data to the stdin of the job.
        @param data: the data to write
        @type data: string
        @raise PermissionDenied: if this object represents stdout or stderr of 
            the job.
        @note: due to buffering, flush() or close() may be needed before it 
            is written to stdin
        """
        if isinstance(self.delegateObject , java.io.InputStream):
            raise PermissionDenied, "Cannot write to the stdout or stderr of" \
                + " the job"
        if type(data) is not str:
            raise BadParameter, "Parameter data is not a string, but a " \
                + str(data.__class__)
        try:
            tempString = java.lang.String(data)
            tempByteArray = tempString.getBytes()
            self.delegateObject.write( tempByteArray )
        except java.io.IOException, e:
            raise self.convertException(e)

    def writelines(self, data):
        """
        Write a sequence of strings to the stdin of the job. Newlines in the 
        sequence are not written to the stdin of the job
        @param data: sequence of strings to write
        @type data: string, or a tuple, list or array of chars  
        @summary: Write a sequence of strings to the stdin of the job.
        @raise PermissionDenied: if this object represents stdout or stderr of 
            the job.
        """
        if isinstance(self.delegateObject , java.io.InputStream):
            raise PermissionDenied, "Cannot write to the stdout or stderr of" \
                + " the job"
        if type(data) is not str and not isinstance(data, array.array) \
        and type(data) is not list and type(data) is not tuple:
            raise BadParameter, "Parameter data is not a string, array, list " \
                "or tuple of strings"
        if type(data) is str:
            tempString = java.lang.String()
            tempList = data.split('\n')
            try:
                for i in range(len(tempList)):
                    tempString.concat( tempList[i] )
            except TypeError, e:
                raise BadParameter, "Parameter data cannot be parsed as a " \
                    + "string: " + str(e) 
            try:
                tempByteArray = tempString.getBytes()
                self.delegateObject.write( tempByteArray )
            except java.io.IOException, e:
                raise self.convertException(e)   
        elif type(data) is list or type(data) is tuple:
            tempString = java.lang.String()
            for i in range(len(data)):
                tempList = data[i].split('\n')
                try:
                    for j in range(len(tempList)):
                        tempString.concat( tempList[j] )
                except TypeError, e:
                    raise BadParameter, "Parameter data cannot be parsed as a" \
                        + " string: " + str(e) 
            try:
                tempByteArray = tempString.getBytes()
                self.delegateObject.write( tempByteArray )
            except java.io.IOException, e:
                raise self.convertException(e)               
        elif isinstance(data, array.array):
            if data.typecode != 'c':
                raise BadParameter, "Parameter is an array of wrong type. " \
                    + "Expected typecode 'c', got: " + data.typecode
            tempString = java.lang.String()
            templist = data.tostring().split('\n')
            try:
                for j in range(len(tempList)):
                    tempString.concat( tempList[j] )
            except TypeError, e:
                    raise BadParameter, "Parameter data cannot be parsed as a" \
                        + " string: " + str(e) 
            try:
                tempByteArray = tempString.getBytes()
                self.delegateObject.write( tempByteArray )
            except java.io.IOException, e:
                raise self.convertException(e)        
        else:
            raise BadParameter, "Parameter data cannot be parsed as a " \
                    + "string: " + str(data.__class__) 
            
            

    def read(self, size = -1, blocking=True):
        """
        Read at most size bytes from stdout or from stderr, depending which 
        one is represented by this object.
        @summary: Read at most size bytes from stdout/stderr.
        @return: string with the data 
        @rtype: string
        @param size: Maximum number of characters to read.
        @type size: bool
        @param blocking: whether the read should block until it has read a 
            number of bytes equal or less then size or not.
        @type blocking: int
        @raise PermissionDenied: if this object represents the stdin of the job.
        @note: whether blocking is True or False, read may return a string which
             length is smaller than parameter size. 
        @note: when there is no data available and blocking is True, read will
            block until it has read at least one byte. If blocking is False,
            read might return an empty string.
        @note: if size is not specified read will return as much data as is 
            available
        @note: if read has read an EOF from the stdout or stderr, read returns 
            an empty string for the blocking case and None for the non-blocking
            case.
      
        """
        if isinstance(self.delegateObject , java.io.OutputStream):
            raise PermissionDenied, "Cannot read from the stdin of the job" 
        if blocking != True and blocking != False:
            raise BadParameter, "Parameter blocking is not a bool, but a " \
                + str(blocking.__class__)
        if type(size) is not int:
            raise BadParameter, "Parameter size is not an int, but a " \
                + str(size.__class__)
        if size <= 0 and size != -1:
            raise BadParameter, "Parameter size is <= 0, namely" + str(size)
        
        import jarray.zeros
        import java.lang.Byte
        tempArray = None
        read = None
        
        if blocking == False:
            if self.EOF_reached == True:
                return None
            available = self.delegateObject.available()
            if available == 0:
                return ""
            
            elif available >= size and size != -1:
                tempArray = jarray.zeros('b', size)
                read = self.delegateObject.read(tempArray,0,size)
            else: #available < size
                tempArray = jarray.zeros('b', available)
                read = self.delegateObject.read(tempArray,0,available)

            if read >= 0:
                return tempArray.tostring()[0:read]
            else:
                self.EOF_reached = True
                return None    # end of file detected
        else:  #blocking == True
            if self.EOF_reached == True:
                return ""
            if size != -1:
                tempArray = jarray.zeros('b', size)
                read = self.delegateObject.read(tempArray,0,size)
            else: # size not specified
                available = self.delegateObject.available()
                if available == 0:
                    available = 4096
                tempArray = jarray.zeros('b', available)
                read = self.delegateObject.read(tempArray)
            if read >= 0:
                return tempArray.tostring()[0:read]
            else:
                self.EOF_reached = True
                return ""    # end of file detected

#TODO add the try / except
        
        
    def readline(self, size = -1, blocking = True):
        """
        Read the next line from the stdout or stderr of the job.
        @summary: Read the next line from the stdout or stderr of the job.
        @return: string with the line of data including the newline character
        @rtype: string
        @param size: Maximum number of characters to read. An incomplete line 
            may be returned
        @type size: bool
        @param blocking: whether the read should block until it has read a 
            line or number of bytes equal or less then size or not.
        @type blocking: int
        @raise PermissionDenied: if this object represents the stdin of the job.
        @note: if blocking is False, readline may return a string which length 
            is smaller than parameter size. 
        @note: when there is no data available and blocking is True, read will
            block until it has read at least one byte. If blocking is False,
            read might return an empty string. 
        @note: if size is not specified readline will return one line of data or
            as much data as is available
        @note: if readline has read an EOF from the stdout or stderr, read 
            returns an empty string for the blocking case and None for 
            the non-blocking case.        
        
        """
        if isinstance(self.delegateObject , java.io.OutputStream):
            raise PermissionDenied, "Cannot read from the stdin of the job" 
        if blocking != True and blocking != False:
            raise BadParameter, "Parameter blocking is not a bool, but a " \
                + str(blocking.__class__)
        if type(size) is not int:
            raise BadParameter, "Parameter size is not an int, but a " \
                + str(size.__class__)
        if size <= 0 and size != -1:
            raise BadParameter, "Parameter size is <= 0, namely" + str(size)

        import jarray.zeros
        import java.lang.Byte
        tempArray = None
        read = None
        available = self.delegateObject.available()
        
        if blocking == False:
            if self.EOF_reached ==True:
                return None
            if available == 0:
                    return ""

            if size == -1:
                tempArray = jarray.zeros('b', available)
                for i in range(available):
                    read = self.delegateObject.read(tempArray, i, 1)
                    if read == -1:
                       self.EOF_reached = True
                       return tempArray.tostring()[0:i]
                    if tempArray[i] == 10: # check for newline character
                        return tempArray.tostring()[0:i+1]    
                return tempArray.tostring()
            
            else: #size > 0
                if size < available:
                    available = size
                tempArray = jarray.zeros('b', available)
                for i in range(available):
                    read = self.delegateObject.read(tempArray, i, 1)
                    if read == -1:
                       self.EOF_reached = True
                       return tempArray.tostring()[0:i]
                    if tempArray[i] == 10: # check for newline character
                        return tempArray.tostring()[0:i+1]    
                return tempArray.tostring()            
            
        else: #blocking == True
            if self.EOF_reached == True:
                return ""
            if size == -1:
                if available == 0:
                    tempArray = jarray.zeros('b', 4096)
                else:
                    tempArray = jarray.zeros('b', available)                    
            else: #size > 0:
                tempArray = jarray.zeros('b', size)
                
            read = self.delegateObject.read(tempArray, 0, 1)
            if read == -1:
                self.EOF_reached = True
                return ""
            if tempArray[i] == 10: # check for newline character
                return "\n"                   
                
            available = self.delegateObject.available()
            if available > len(tempArray-1):
                available = len(tempArray-1)
                    
            for i in range(available):
                read = self.delegateObject.read(tempArray, i+i, 1)
                if read == -1:
                    self.EOF_reached = True
                    return tempArray.tostring()[0:i+1]
                if tempArray[i] == 10: # check for newline character
                    return tempArray.tostring()[0:i+2]    
            return tempArray.tostring()                
                            
                
 
#TODO: check newline and carriage return 
#TODO: add the try / except
            
    def readlines(self, size=-1, blocking = True):
        """
        Read multiple lines from the stdout or stderr.
        @summary: Read multiple lines from the stdout or stderr.
        @return: List of strings with lines of data without the newline 
            characters
        @rtype: list 
        @param size: Maximum number of characters to read. An list with an 
            incomplete line as last element of the list may be returned
        @type size: bool
        @param blocking: whether the read should block until it has read a 
            number of bytes equal or less then size or not.
        @type blocking: int
        @raise PermissionDenied: if this object represents the stdin of the job.
        @note: if blocking is False, readlines may return a list of strings 
            which total length including newlines is  smaller than parameter 
            size.
        @note: read newline character do count towards the size limit, although
            the are not returned to the user.
        @note: when there is no data available and blocking is True, read will
            block until it has read at least one byte. If blocking is False,
            read might return an empty list. 
        @note: if size is not specified readlines will return a list of as much
            strings available. The last element in the list may be an incomplete
            line
        @note: if readlines has read an EOF from the stdout or stderr, read 
            returns an empty list for the blocking case and None for 
            the non-blocking case.            
        
        """
        if isinstance(self.delegateObject , java.io.OutputStream):
            raise PermissionDenied, "Cannot read from the stdin of the job" 
        if blocking != True and blocking != False:
            raise BadParameter, "Parameter blocking is not a bool, but a " \
                + str(blocking.__class__)
        if type(size) is not int:
            raise BadParameter, "Parameter size is not an int, but a " \
                + str(size.__class__)
        if size <= 0 and size != -1:
            raise BadParameter, "Parameter size is <= 0, namely" + str(size)
        result = []
        total_read = 0
        
        if blocking == False:
            while total_read < size:
                string = self.readline( size-total_read, blocking)
                if string == None:
                    return result
                total_read += len(string)
                if string[-1] == '\n':
                    result.append( string[0:-1])
                else:
                    result.append( string )
                    return result
            return result
        else: # blocking == True:
            available = self.delegateObject.available()
            if available == 0:
                string = self.readline( size-total_read, blocking)
                if string == "":
                    return result
                if string[-1] == '\n':
                    result.append( string[0:-1])
                else:
                    result.append( string )
                return result                
            else:
                while total_read < size:
                    string = self.readline( size-total_read, blocking)
                    if string == None:
                        return result
                    total_read += len(string)
                    if string[-1] == '\n':
                        result.append( string[0:-1])
                    else:
                        result.append( string )
                        return result
                return result            

    name = property(get_name,
                    doc="""the name of the StdIO object.\n@type: string""")

    mode = property(get_mode,
                    doc="""the mode ot the StdIO object.\n@type: string""")

    
class Job(Task, Attributes, Permissions, Async): 
    """
    
    The job provides the manageability interface to a job instance submitted to 
    a resource manager. 

  
    B{Attributes:}
    
        - B{JobID}
            - name: JobID
            - desc: SAGA representation of the job identifier
            - mode: ReadOnly
            - type: String
            - value: -
            - notes: format: as described earlier
        - B{ExecutionHosts}
            - name: ExecutionHosts
            - desc: list of host names or IP addresses allocated to run this job
            - mode: ReadOnly, optional
            - type: List of Strings
            - value: -
            - notes: -
        - B{Created}
            - name: Created
            - desc: time stamp of the job creation in the resource manager
            - mode: ReadOnly, optional
            - type: Time
            - value: -
            - notes: can be interpreted as submission time
        - B{Started}
            - name: Started
            - desc: time stamp indicating when the job started running
            - mode: ReadOnly, optional
            - type: Time
            - value: -
        - B{Finished}
            - name: Finished
            - desc:  time stamp indicating when the job completed
            - mode:  ReadOnly, optional
            - type:  Time
            - value: -
        - B{WorkingDirectory}
            - name:  WorkingDirectory
            - desc:  working directory on the execution host
            - mode:  ReadOnly, optional
            - type:  String
            - value: -
            - notes: can be used to determine the location of
                files staged using relative file paths
        - B{ExitCode}
            - name:  ExitCode
            - desc:  process exit code as collected by the wait(2)
            - series of system calls.
            - mode: ReadOnly, optional
            - type: Int
            - value: -
            - notes: 
                - exit code is collected from the process which was started 
                  from the 'Executable'  attribute of the job_description 
                  object.
                - only available in final states, if at all
        - B{Termsig}
            - name:  Termsig
            - desc:  signal number which caused the job to exit
            - mode:  ReadOnly, optional
            - type:  Int
            - value: -
            - notes: only available in final states, if at all
    
    B{Metrics:}
    
        - B{job.state}
            - name: job.state
            - desc: fires on state changes of the job, and has the literal 
                value of the job state enum.
            - mode: ReadOnly
            - unit: 1
            - type: int
            - value: New
            - note: the state metric is inherited from Task, but has a 
                different set of possible values
        - B{job.state_detail}
            - name: job.state_detail
            - desc:  fires as a job changes its state detail
            - mode:  ReadOnly, optional
            - unit:  1
            - type:  String
            - value: -
        - B{job.signal}
            - name:  job.signal
            - desc:  fires as a job receives a signal, and has a value 
                indicating the signal number
            - mode: ReadOnly, optional
            - unit: 1
            - type: Int
            - value: -
            - note: no guarantees are made that any or all signals can be 
                notified by this metric
        - B{job.cpu_time}
            - name:  job.cpu_time
            - desc:  number of CPU seconds consumed by the job
            - mode:  ReadOnly, optional
            - unit:  seconds
            - type:  Int
            - value: -
            - notes: aggregated across all processes/threads
        - B{job.memory_use}
            - name:  job.memory_use
            - desc:  current aggregate memory usage
            - mode:  ReadOnly, optional
            - unit:  megabyte
            - type:  Float
            - value: 0.0
            - note:  metric becomes 'Final' after job completion, and then 
                shows the memory high water mark
        - B{job.vmemory_use}
            - name:  job.vmemory_use
            - desc:  current aggregate virtual memory usage
            - mode:  ReadOnly, optional
            - unit:  megabyte
            - type:  Float
            - value: 0.0
            - note:  metric becomes 'Final' after job completion, and then 
                shows the virtual memory high water mark
        - B{job.performance}
            - name:  job.performance
            - desc:  current performance
            - mode:  ReadOnly, optional
            - unit:  FLOPS
            - type:  Float
            - value: 0.0
            - notes: metric becomes 'Final' after job completion, and then 
                shows the performance high water mark

    @summary: The job provides the manageability interface to a job 
        instance submitted to a resource manager.
    @version: 1.0, designed for Python 2.x
    @undocumented: __get_JobID
    @undocumented: __get_ExecutionHosts
    @undocumented: __get_Created
    @undocumented: __get_Started
    @undocumented: __get_Finished
    @undocumented: __get_WorkingDirectory
    @undocumented: __get_ExitCode
    @undocumented: __get_Termsig

    """


    def __get_JobID(self):
        return self.get_attribute("JobID")  

    JobID = property(__get_JobID,  
                          doc="""The JobID attribute.
                              @type:string""")

    def __get_ExecutionHosts(self):
        return self.get_vector_attribute("ExecutionHosts")  
           
    ExecutionHosts = property(__get_ExecutionHosts, 
                          doc="""The ExecutionHosts attribute.
                              @type:list of strings""")

    def __get_Created(self):
        return self.get_attribute("Created")  

    Created = property(__get_Created,  
                          doc="""The Created attribute.
                              @type:string""")

#TODO: Check type of Created, Timestamp is vague.
#            - name: Created
#            - desc: time stamp of the job creation in the resource manager
#            - mode: ReadOnly, optional
#            - type: Time
#            - value: -
#            - notes: can be interpreted as submission time

        
    def __get_Started(self):
        return self.get_attribute("Started")  
 
    Started = property(__get_Started, doc="""The  attribute.\n @type:string""")
#TODO: Check type of Started, Timestamp is vague.
#            - name: Started
#            - desc: time stamp indicating when the job started running
#            - mode: ReadOnly, optional
#            - type: Time
#            - value: -

    def __get_Finished(self):
        return self.get_attribute("Finished")  

    Finished = property(__get_Finished, doc="""The Finished attribute.\n
                          @type:string""")
#TODO: Check type of Finished, Timestamp is vague.
#            - name: Finished
#            - desc:  time stamp indicating when the job completed
#            - mode:  ReadOnly, optional
#            - type:  Time
#            - value: -

    def __get_WorkingDirectory(self):
        return self.get_attribute("WorkingDirectory")  

    WorkingDirectory = property(__get_WorkingDirectory, 
                                doc="""The WorkingDirectory attribute.\n
                                @type:string""")

    def __get_ExitCode(self):
        return self.get_attribute("ExitCode")  

    ExitCode = property(__get_ExitCode, 
                          doc="""The ExitCode attribute.\n @type:int""")
#TODO: implementation ExitCode: cast to int

    def __get_Termsig(self):
        return self.get_attribute("Termsig")  

    Termsig = property(__get_Termsig, doc="""The Termsig attribute.\n
                          @type:int""")
#TODO: implementation TermSig: cast to int
    def __init__(self, **impl):
        """
        @summary: Initializes the Job object. Cannot only be created by
            methods which create a Job, and not through j = Job()
        """
        self.delegateObject = None
        self.fileReadBuffer = None
        self.taskFailed = False
        self.failureCause = None
        self.taskWasRunJob = False
        self.name = None
        if "delegateObject" in impl:
            if not isinstance(impl["delegateObject"],org.ogf.saga.job.Job):
                raise BadParameter,"Parameter impl[\"delegateObject\"] is not" \
                    + " a org.ogf.saga.job.Job. Type: " \
                    + str(impl["delegateObject"].__class__)
            self.delegateObject = impl["delegateObject"]
            return 
        else:
            raise BadParameter, "Job can only be created through methods" \
                + " and not through \"job = Job()\" or likewise "

    #job inspection
    def get_job_description(self, tasktype=TaskType.NORMAL):
        #out job_description  jd
        """
        Retrieve the job_description which was used to submit this job instance.
        @summary: Retrieve the job_description which was used to submit this job
            instance.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: the JobDescription object
        @rtype: L{JobDescription}
        @PostCondition: return value is deep copied (no state is shared after 
            method invocation)
        @permission: Query:
        @raise NotImplemented:
        @raise DoesNotExist:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: There are cases when the JobDescription is not available. This 
            may include cases when the job was not submitted through SAGA and 
            get_job() was used to retrieve the job, or when this state 
            information has been lost (e.g. the client application restarts and 
            the particular SAGA implementation did not persist the information).
            In that case, a 'DoesNotExist' exception is raised, with a 
            descriptive error message.
        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
        
        #Normal get_job_description()
        if tasktype == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.getJobDescription()
                return JobDescription(delegateObject = javaObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)   
            
        #Asynchronous get_job_description()
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.getJobDescription(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.getJobDescription(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.getJobDescription(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)           
    
    
    def get_stdin(self, tasktype=TaskType.NORMAL):
        """
        Retrieve input stream for a job.
        @summary: Retrieve input stream for a job.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: standard input stream for the job
        @rtype: L{StdIO}
        @PreCondition:    the job is interactive.
        @PostCondition:   the jobs standard input stream is available at stdin.
        @permission: Write (application can write to the jobs stdin).
        @raise NotImplemented:
        @raise BadParameter:
        @raise DoesNotExist:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: if the preconditions are met, but the standard input stream is 
            not available for some reason, a 'DoesNotExist' exception is raised.
        @Note: the stream is valid until the job reaches a final state. If it 
            is, for some reason, disconnected earlier, a error  message is 
            raised. 
        @Note: if the job is not interactive, e.g. it was  submitted with the 
            'Interactive' attribute set to 'False', an 'IncorrectState' 
            exception is raised.
        @Note: if the job is not in 'New' state, it is not guaranteed that the 
            job did not receive other data on its standard input stream before.
        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
 
        #Normal get_stdin()
        if tasktype == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.getStdin()
                return StdIO(delegateObject = javaObject, name= "<stdin>")
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous get_stdin()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.getStdin(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.getStdin(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.getStdin(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)               
    

    def get_stdout(self, tasktype=TaskType.NORMAL):
        """
        Retrieve output stream of job
        @summary: Retrieve output stream of job
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: standard output stream for the job
        @rtype: L{StdIO}
        @PreCondition: the job is interactive.
        @PostCondition: the jobs standard output stream is available from stdout.
        @permission: Read (application can read the jobs stdout).
        @raise NotImplemented:
        @raise BadParameter:
        @raise DoesNotExist:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: if the preconditions are met, but the standard output stream is 
            not available for some reason, a 'DoesNotExist' exception is raised.
        @Note: the stream is valid until the job reaches a final state. 
            If it is, for some reason, disconnected earlier, a error message is 
            raised.
        @Note: if the job is not interactive, e.g. it was submitted with the 
            'Interactive' attribute set to 'False', an 'IncorrectState' 
            exception is raised.
        @Note: if the job is not in 'New' state, it is not guaranteed that the 
            job did write data on its standard output stream before, which are 
            then not returned on the returned stream.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal get_stdout()
        if tasktype == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.getStdout()
                return StdIO(delegateObject = javaObject, name = "<stdout>")
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous get_stdout()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.getStdout(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.getStdout(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.getStdout(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)      
    
    def get_stderr(self, tasktype=TaskType.NORMAL):
        """
        Retrieve error stream of job
        @summary: Retrieve error stream of job
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @return: standard error stream for the job
        @rtype: L{StdIO}
        @PreCondition: the job is interactive.
        @PostCondition: the jobs standard error stream is available from stderr.
        @permission: Read (application can read the jobs stderr).
        @raise NotImplemented:
        @raise BadParameter:
        @raise DoesNotExist:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: if the preconditions are met, but the standard error stream is 
            not available for some reason, a 'DoesNotExist' exception is raised.
        @Note: the stream is valid until the job reaches a final state. 
            If it is, for some reason, disconnected earlier, a error message is 
            raised.
        @Note: if the job is not interactive, e.g. it was submitted with the 
            'Interactive' attribute set to 'False', an 'IncorrectState' 
            exception is raised.
        @Note: if the job is not in 'New' state, it is not guaranteed that the 
            job did write data on its standard error stream before, which are 
            then not returned on the returned stream.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal get_stderr()
        if tasktype == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.getStderr()
                return StdIO(delegateObject = javaObject, name = "<stderr>")
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous get_stderr()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.getStderr(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.getStderr(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.getStderr(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)     
    
    #job management
    def suspend(self, tasktype=TaskType.NORMAL):
        """
        Ask the resource manager to perform a suspend operation on the running 
        job.
        @summary: Ask the resource manager to perform a suspend operation on 
            the running job.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @PreCondition: the job is in 'Running' state.
        @PostCondition: the job is in 'Suspended' state.
        @permission: Exec (job can be controlled).
        @raise NotImplemented:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: if the job is not in 'Running' state, an 'IncorrectState' 
            exception is raised.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal suspend()
        if typetask == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.suspend()
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous suspend()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.suspend(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.suspend(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.suspend(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)                    
                          
    def resume(self, tasktype=TaskType.NORMAL):
        """
        Ask the resource manager to perform a resume operation on a suspended 
        job.
        @summary: Ask the resource manager to perform a resume operation on a 
            suspended job.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}  
        @type tasktype: value from L{TaskType}
        @PreCondition: the job is in 'Suspended' state.
        @PostCondition: the job is in 'Running' state.
        @permission: Exec (job can be controlled).
        @raise NotImplemented:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note:  if the job is not in 'Suspended' state, an 'IncorrectState' 
            exception is raised.
        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"
                
        #Normal resume()
        if typetask == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.resume()
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous resume()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.resume(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.resume(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.resume(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)   
    
    def checkpoint(self, tasktype=TaskType.NORMAL):
        """
        Ask the resource manager to initiate a checkpoint operation on a running 
        job.
        @summary: Ask the resource manager to initiate a checkpoint operation 
            on a running job.
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @PreCondition: the job is in 'Running' state.
        @PostCondition: the job is in 'Running' state.
        @PostCondition: the job was checkpointed.
        @permission: Exec (job can be controlled).
        @raise NotImplemented:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: The semantics of checkpoint(), and the actions taken to initiate 
            a checkpoint, are resource manager specific. In particular, the 
            implementation or backend can trigger either a system level or an 
            application level
        @note: if the job is not in 'Running' state, an 'IncorrectState' 
            exception is raised.

        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal checkpoint()
        if typetask == TaskType.NORMAL:
            try:
                javaObject = self.delegateObject.checkpoint()
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous checkpoint()    
        else:
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.checkpoint(TaskMode.ASYNC)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.checkpoint(TaskMode.SYNC)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.checkpoint(TaskMode.TASK)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)  
                    
    def migrate(self, jd, tasktype=TaskType.NORMAL):
        #in job_description jd
        """
        Ask the resource manager to migrate a job.
        @param jd: new job parameters to apply when the job is migrated
        @type jd: L{JobDescription} 
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @PreCondition:    the job is in 'Running' or 'Suspended' state.
        @PostCondition:    the job keeps its state.
        @PostCondition: jd is deep copied (no state is shared after method 
            invocation)
        @PostCondition: the job reflects the attributes specified in the 
            job_description.
        @permission:   Exec (job can be controlled).
        @raise NotImplemented:
        @raise BadParameter:
        @raise IncorrectState:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise PermissionDenied:
        @raise Timeout:
        @raise NoSuccess:
        @Note: jd might indicate new resource requirements, for example.
        @Note: the action of migration might change the job identifier within 
            the resource manager.
        @Note: ideally, the submitted job description was obtained by 
            get_job_description(), and then changed by the application. This is 
            not a requirement though.
        @Note: if the job is not in 'Running' or 'Suspended' state, an 
            'IncorrectState' exception is raised.
        @Note: the method can call the same exceptions as the submit_job() 
            and run() methods, in particular in respect to an incorrect 
            job_description.
       
        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal migrate()
        if typetask == TaskType.NORMAL:
            if not isinstance(jd, JobDescription):
                raise BadParameter, "Parameter jd is not a JobDescription, but"\
                    +" a "+ str(jd.__class__)
            
            try:
                javaObject = self.delegateObject.migrate(jd.delegateObject)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous migrate()    
        else:
          if not isinstance(jd, JobDescription):
                bp = BadParameter("Parameter jd is not a JobDescription, but"\
                    +" a "+ str(jd.__class__))
                return Task(error = bp)
          
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.migrate(TaskMode.ASYNC,jd.delegateObject)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.migrate(TaskMode.SYNC,jd.delegateObject)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.migrate(TaskMode.TASK,jd.delegateObject)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)                  
                    
    def signal(self, signum, tasktype=TaskType.NORMAL):
        #in int signum
        """
        Ask the resource manager to deliver an arbitrary signal to a dispatched 
        job.
        @param signum: signal number to be delivered
        @type signum: int
        @param tasktype: return the normal return values or a Task object in a 
            final, RUNNING or NEW state. By default, tasktype is L{TaskType.NORMAL}
        @type tasktype: value from L{TaskType}
        @PreCondition: job is in 'Running' or 'Suspended' state.
        @PostCondition: the signal was delivered to the job.
        @Permission:  Exec (job can be controlled).
        @raise NotImplemented:
        @raise BadParameter:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @Note: there is no guarantee that the signal number specified is valid 
            for the operating system on the execution host where the job is 
            running, or that the signal can be delivered.
        @Note: if the signal number is not supported by the backend, a 
            BadParameter exception is raised.
        @Note: if the job is not in 'Running' or 'Suspended' state, an 
            'IncorrectState' exception is raised.
        
        """
        if tasktype is not TaskType.NORMAL and tasktype is not TypeTask.SYNC \
        and tasktype is not TaskType.ASYNC  and tasktype is not TypeTask.TASK:
            raise BadParameter, "Parameter tasktype is not one of the TypeTask"\
                +" values, but "+ str(tasttype)+"("+ str(tasktype.__class__)+")"

        #Normal signal()
        if typetask == TaskType.NORMAL:
            if not isinstance(signum, int):
                raise BadParameter, "Parameter signum is not an int, but"\
                    +" a "+ str(signum.__class__)
            
            try:
                javaObject = self.delegateObject.signal(signum)
            except org.ogf.saga.error.SagaException, e:
                raise self.convertException(e)        
    
        #Asynchronous signal()    
        else:
          if not isinstance(signum, int):
                bp =  BadParameter("Parameter signum is not an int, but"\
                                   +" a "+ str(signum.__class__))
                return Task(error = bp)
          
          try:
            if tasktype is TaskType.ASYNC:
              javaObject = self.delegateObject.signal(TaskMode.ASYNC,signum)
            if tasktype is TaskType.SYNC:
              javaObject = self.delegateObject.signal(TaskMode.SYNC,signum)
            if tasktype is TaskType.TASK:
              javaObject = self.delegateObject.signal(TaskMode.TASK,signum)
            return Task(delegateObject=javaObject)                
          except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e) 
                

class JobSelf(Job, Steerable):
  """
  The job_self class IS-A job which represents the current application (i.e. the
  very application which owns that job_self instance). It can only by created
  by calling get_self() on a job service (that call can fail though).
  """
  