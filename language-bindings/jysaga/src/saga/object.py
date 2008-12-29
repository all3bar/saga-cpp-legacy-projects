# Package: saga
# Module: object 
# Description: The module which specifies the base SAGA object class and 
#    ObjectType class
# Specification and documentation can be found in section 3.2, page 47-52 of 
#    the GFD-R-P.90 document
# Author: P.F.A. van Zoolingen, Computer Systems Section, Faculty of 
#    Exact Science (FEW), Vrije Universiteit, Amsterdam, The Netherlands.

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
import java.io.IOException
 
class ObjectType(object):
    """
    ObjectType allows for inspection of SAGA object instances.
    This, in turn, allows to treat large numbers of SAGA object instances in containers, 
    without the need to create separate container types for each specific SAGA object type.
    @version: 1.0

    """
    EXCEPTION         =  1
    URL               =  2
    BUFFER            =  3
    SESSION           =  4
    CONTEXT           =  5
    TASK              =  6
    TASKCONTAINER     =  7
    METRIC            =  8
    NSENTRY           =  9
    NSDIRECTORY       = 10
    IOVEC             = 11
    FILE              = 12
    DIRECTORY         = 13
    LOGICALFILE       = 14
    LOGICALDIRECTORY  = 15
    JOBDESCRIPTION    = 16
    JOBSERVICE        = 17
    JOB               = 18
    JOBSELF           = 19
    STREAMSERVICE     = 20
    STREAM            = 21
    PARAMETER         = 22
    RPC               = 23
  
class Object(object):
    """
    The SAGA object provides methods which are essential for all SAGA
    objects. It provides a unique ID which helps maintain a list of SAGA objects
    at the application level as well as allowing for inspection of objects type and its
    associated session.
    @version: 1.0
    
    """
        
    def get_id(self):
        """
        Query the object ID.
        @summary: Query the object ID.
        @return: uuid for the object
        @rtype: string 
        """
        try:
            return self.delegateObject.getId()
        except org.ogf.saga.error.SagaException, e:
           raise self.convertException(e)
      
    def get_type(self):
        """
        Query the object type.
        @summary: Query the object type.
        @return: type of the object as an int from ObjectType
        @rtype: int
        """
        from saga.error import NotImplemented
        raise NotImplemented, "get_type() is not yet implemented in this object"
        
    def get_session(self):
        """
        Query the objects session.
        @summary: Query the objects session.
        @return: session of the object
        @rtype: L{Session}
        @PreCondition: the object was created in a session, either
            explicitly or implicitly.
        @PostCondition: the returned session is shallow copied.
        @raise DoesNotExist:
        @Note: if no specific session was attached to the object at creation time, 
            the default SAGA session is returned.
        @note: some objects do not have sessions attached, such as JobDescription, Task, Metric, and the
            Session object itself. For such objects, the method raises a 'DoesNotExist' exception.
        """
        from saga.session import Session
        try:
            tempSession = self.delegateObject.getSession()
            session = Session(sessionObject=tempSession)
            return session
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)
    
    def clone(self):
        """
        @summary: Deep copy the object
        @return: the deep copied object
        @rtype: L{Object}
        @PostCondition: apart from session and callbacks, no other state is shared
            between the original object and it's copy.
        @raise NoSuccess:
        @Note: that method is overloaded by all classes which implement saga.object.Object, and returns
                 a deep copy of the respective class type.
        @see: section 2 of the GFD-R-P.90 document for deep copy semantics.

        """
        from saga.error import NotImplemented
        raise NotImplemented, "clone() is not yet implemented in this object"
 
#        try:
#            javaClone = self.delegateObject.clone()
#            clone = <OBJECT_NAME>(delegateObject=javaClone)
#            return clone
#        except org.ogf.saga.error.SagaException, e:
#            raise self.convertException(e)
        
    def convertException(self, e):
        from saga.error import NotImplemented, IncorrectURL, BadParameter, \
            AlreadyExists, DoesNotExist, IncorrectState, PermissionDenied, \
             AuthorizationFailed, AuthenticationFailed, Timeout, NoSuccess
        object = None
        message = ""

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
        import java.io.IOException


        try:
            object = e.getObject()
            from saga.file import Directory, File
            from saga.namespace import NSEntry, NSDirectory
            from saga.job import Job, JobSelf, JobService
            from saga.stream import StreamService, Stream
            from saga.rpc import RPC
            import org.ogf.saga.file.Directory
            import org.ogf.saga.file.File
            import org.ogf.saga.namespace.NSEntry
            import org.ogf.saga.namespace.NSDirectory
            
            #TODO: Subclasses first!
         
         
            if isinstance(object, org.ogf.saga.file.Directory):
                object = Directory(name="", delegateObject = object)
            elif isinstance(object, org.ogf.saga.file.File):
                object = File(name="", delegateObject = object)
            elif isinstance(object,org.ogf.saga.namespace.NSDirectory):
                object = NSDirectory(name="", delegateObject = object)
            elif isinstance(object, org.ogf.saga.namespace.NSEntry ):
                object = NSEntry(name="", delegateObject = object) 
            elif isinstance(object, org.ogf.saga.job.Job ):
                object = Job(delegateObject=object)
            elif isinstance(object, org.ogf.saga.job.JobService ):
                object = JobService(delegateObject=object)    
            elif isinstance(object, org.ogf.saga.job.JobSelf ):
                object = JobSelf(delegateObject=object)    
            elif isinstance(object, org.ogf.saga.stream.StreamService):
                object = StreamService(delegateObject=object) 
            elif isinstance(object, org.ogf.saga.stream.Stream):
                object = Stream(delegateObject=object) 
            elif isinstance(object, org.ogf.saga.rpc.RPC):
                object = RPC(funcname="",delegateObject=object)
            else:
                print "convertException: java Exception (",e.__class__,\
                "had an attached sagaObject."\
                +"Object is NOT yet translated to a python object. " + \
                str(object.__class__)
                object = None
            #TODO: convert sagaObject naar Object -> referentie naar self
        except org.ogf.saga.error.DoesNotExistException, exception:
            object = None
        message = e.getMessage()

               
        if isinstance(e, org.ogf.saga.error.AlreadyExistsException):
            error = AlreadyExists(message, object)
        elif isinstance(e, org.ogf.saga.error.AuthenticationFailedException):
            error = AuthenticationFailed(message, object)
        elif isinstance(e, org.ogf.saga.error.AuthorizationFailedException):
            error = AuthorizationFailed(message, object)
        elif isinstance(e, org.ogf.saga.error.BadParameterException):
            error = BadParameter(message, object)
        elif isinstance(e, org.ogf.saga.error.DoesNotExistException):
            error = DoesNotExist(message, object)
        elif isinstance(e, org.ogf.saga.error.IncorrectStateException):
            error = IncorrectState(message, object)
        elif isinstance(e, org.ogf.saga.error.IncorrectURLException):
            error = IncorrectURL(message, object)
        elif isinstance(e, org.ogf.saga.error.NoSuccessException):
            error = NoSuccess(message, object)
        elif isinstance(e, org.ogf.saga.error.NotImplementedException):
            error = NotImplemented(message, object)
        elif isinstance(e, org.ogf.saga.error.PermissionDeniedException):
            error = PermissionDenied(message, object)
        elif isinstance(e, org.ogf.saga.error.SagaIOException):
            error = sagaIO(message, object)
        elif isinstance(e, org.ogf.saga.error.TimeoutException):
            error = Timeout(message, object)
        elif isinstance(e, java.io.IOException):    #needed for StdIO class
            error = sagaIO(messaga, object)
        else:
            error = NoSuccess(message, object)
        return error

#DOCUMENT: python readlines does not live up to its own description.    
#DOCUMENT: Document SagaIOException -> NoSucces IOError, multiple inheritence 

    id = property(get_id, 
            doc="""The object ID.\n@type: string""")
    type= property(get_type,
            doc="""The object type.\n@type: int""")
    session= property(get_session,
            doc="""The L{Session} of the object.\n@type:L{Session}""")