# GFD-R-P.90
#package saga.Task
from object import Object, ObjectType
from monitoring import Monitorable
from error import NotImplemented

class State(object):
    """ 
    State specifies the possible states a Task can be in
    """
    
    NEW      = 1
    """
    @summary: this state identifies a newly constructed Task instance which has not yet
        run. This state corresponds to the BES state 'Pending'. This state is
        initial.
    """
    
    RUNNING  = 2
    """
    @summary: the run() method has been invoked on the Task, either explicitly or
        implicitly. This state corresponds to the BES state 'Running'. This
        state is initial
    """
    
    DONE     = 3
    """
    @summary: the synchronous or asynchronous operation has finished successfully. It
        corresponds to the BES state 'Finished'. This state is final.
    """
    
    CANCELED = 4
    """
    @summary: the asynchronous operation has been canceled, i.e. cancel() has been
        called on the Task instance. It corresponds to the BES state 'Canceled'.
        This state is final.
    """
    
    FAILED   = 5
    """
    @summary: the synchronous or asynchronous operation has finished unsuccessfully.
        It corresponds to the BES state 'Failed'. This state is final.
    """

class WaitMode(object):
    """
    The wait mode enum specifies the condition on which a wait() operation on a
    saga.Task.TaskContainer returns.
    """
    ALL = 0  
    """@summary: wait() returns if all Tasks in the container reached a final state"""
    ANY = 1
    """@summary: wait() returns if one or more Tasks in the container reached a final state."""

class Async(object):
    """
    This interface is empty on purpose, and is used only for tagging of SAGA 
    classes which implement the SAGA Task model.
    """
    pass

class Task(Object, Monitorable):
    """
    Tasks represent asynchronous API calls. They are only created
    by invoking an asynchronous method (Tasks should not be created directly) on a SAGA object
    which returns a Task object (with saga.Task.Async or saga.Task.Task).  
    But as saga.job.Job instances inherit from the Task class, Jobs are also effectively
    created as Tasks. If a Task gets created, it will share the state of the object it was created from.

        - B{Metric:}
            - name:  Task.state
            - desc:  fires on Task state change, and has the literal value of a the TaskState class variable.
            - mode:  ReadOnly
            - unit:  1
            - type: int
            - value: 0

    """
#    def __init__(self):
#        #no constructor
#        super(Task,self).__init__()
#        pass
    
    def __del__(self):
        """
        Destroy the object
        @PostCondition: state is no longer shared with the object the Task was created from.
        @PostCondition: the Task instance is 'CANCELED' prior to resource deallocation.
        @Note: if the instance was not in a final state before, the destructor performs a cancel()
            on the instance, and all notes to cancel() apply.
        """
        Object.__del__(self)
        Monitorable.__del__(self)
        pass
    
    def run(self):
        """
        Start the asynchronous operation
        @summary:  start the asynchronous operation
        @precondition: Task is in 'NEW' state
        @postcondition: Task is in 'RUNNING' state
        @permission: appropriate permissions for the method represented by the Task
        @raise  NotImplemented:
        @raise IncorrectState:
        @raise Timeout:
        @raise NoSuccess:
        @note: run can only be called on a Task in 'NEW' state. All other states will cause the
               'IncorrectState' exception to be thrown.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to start the Task.

        """
        raise NotImplemented, "run() is not implemented in this object"
    
    def cancel(self, timeout=0.0):
        #in float timeout = 0.0
        """
        Cancel the asynchronous operation
        @summary:  cancel the asynchronous operation
        @param   timeout:              time for freeing resources
        @type timeout: float
        @precondition: Task is in 'RUNNING' state.
        @postcondition: Task is in 'CANCELED' state.
        @raise NotImplemented:
        @raise IncorrectState:
        @raise Timeout:
        @raise NoSuccess:
        @note: for resource deallocation semantics and timeout semantics, see Section 2 of the GFD-R-P.90 document.
        @note: if cancel() fails to cancel the Task immediately, and tries to continue to cancel
            the Task in the background, the Task state remains 'RUNNING' until the cancel operation
            succeeded. The state then changes to 'CANCELED'.
        @note: if the Task is in a final state, the call has no effect, and, in particular, does NOT change
            the state from 'DONE' to 'CANCELED', or from 'FAILED' to 'CANCLED'. This is to avoid race conditions.
        @note: if the Task is in 'NEW' state, an 'IncorrectState' exception is thrown.
        @note: a 'NoSuccess' exception indicates that the backend was not able to initiate the cancelation for the Task.
          

        """
        raise NotImplemented, "cancel() is not implemented in this object"
    
    def wait(self, timeout=-1.0):
        #in float timeout = -1.0, out boolean finished
        """
        Wait for the Task to finish
        @summary:  wait for the Task to finish
        @param timeout: seconds to wait
        @type timeout: float
        @return: indicator if the Task is done running
        @rtype: bool
        @precondition: Task is not in 'NEW' state.
        @postcondition: if no timeout occurs, Task is in a final state.
        @raise NotImplemented:
        @raise IncorrectState:
        @raise Timeout:
        @raise NoSuccess:
        @note: wait returns success (True) as soon as the Task enters a final state
        @note: if the Task is already in a final state, the call returns success (True) immediately.
        @note: if the Task is in 'NEW' state, an 'IncorrectState' exception is thrown.
        @note: wait returns no success (False) if the Task is, even after timeout, not in a final state.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to wait for the
            Task. Note that a 'Timeout' exception does not indicate that the Task is not in a final
            state after the given wait period - that causes an unsuccessfull (False) return value.
        @note: for timeout semantics, see Section 2 of the GFD-R-P.90 document

        """        
        raise NotImplemented, "wait() is not implemented in this object"
      
    def get_state(self):
        #out state state
        """
        Get the state of the Task
        @summary:  get the state of the Task
        @return: state of the Task
        @rtype: int
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to retrieve the Task state.
        """
        raise NotImplemented, "get_state() is not implemented in this object"
      
    def get_result(self):
        """
        Get the result of the async operation
        @summary: get the result of the async operation
        @return: return value of the async method
        @rtype: I{<return value>}
        @precondition: Task is not in NEW, FAILED or CANCELED state.
        @postcondition: Task is in a final state.
        @raise NotImplemented:
        @raise IncorrectState:
        @raise Timeout:
        @raise NoSuccess:
        @note: get_result implies a wait() - all notes to wait apply.
        @note: the method returns the type and value which would be returned by the synchronous version of
            the respective function call.
        """
        
    def get_object(self):
        """
        Get the object from which this Task was created 
        @summary: get the object from which this Task was created
        @return: object this Task was created from
        @rtype I{<object>}
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: the method returns a shallow copy of the object this Task was created from.
        """
      
      # error handling
    def rethrow(self):
        """
        Re-throw any exception a failed Task caught
        @summary:  re-throw any exception a failed Task caught
        @raise NotImplemented:
        @raise IncorrectURL:
        @raise BadParameter:
        @raise AlreadyExists:
        @raise DoesNotExist:
        @raise IncorrectState:
        @raise PermissionDenied:
        @raise AuthorizationFailed:
        @raise AuthenticationFailed:
        @raise Timeout:
        @raise NoSuccess:
        @note: this method does nothing unless the Task is in 'FAILED' state, and also throws
                 'IncorrectState' if the Task is in any other state.
        @note: if in 'FAILED' state, the method raises an exception which indicates the reason why that
                 Task entered the 'FAILED' state (i.e. it throws the exception which caused it to enter the
                 'FAILED' state.
        @note: rethrow() can be called multiple times, always throwing the same exception.
        """
    
    
    
class TaskContainer(Object, Monitorable):
    """
    The TaskContainer class is designed to effectively handle a large number
    of asynchronous operations, since managing a large number of Tasks can be tedious.
    For example, when an application uses many Tasks, it would be inefficient to
    invoke the wait() method on each of them individually. The TaskContainer
    class provides (amongst other operations) a mechanism to wait for a set of Tasks.
 
        - B{Metric}
            - name:  TaskContainer.state
            - desc:  fires on state changes of any Task in container, and has the value of that Task's cookie.
            - mode:  ReadOnly
            - unit:  1
            - type:  Int
            - value: -

    """
    
    def __init__(self):
        """
        Initialize the TaskContainer
        @summary: initialize the TaskContainer
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to create a TaskContainer.
        """
        
        
    def __del__(self):
        """
        Destroy the TaskContainer
        @summary: destroy the TaskContainer
        @note: Tasks in the TaskContainer during its destruction are not affected by its
                       destruction, and, in particular, are not canceled.
        """


    def add(self, task):
        """
        Add a Task to a TaskContainer
        @summary: add a Task to a TaskContainer
        @param task: Task to add to the TaskContainer
        @type task: L{Task}
        @return: cookie identifying the added Task
        @rtype int
        @postcondition: the Task is managed by the Task container.
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: a Task can be added only once. Any attempt to add a Task to the container which already
                  is in the container is silently ignored, and the same cookie as for the original Task is
                  returned again.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to add the Task
                  to the container.
                  
        """
        
    def remove(self, cookie):
        """
        Remove a Task from a TaskContainer
        @summary:  remove a Task from a TaskContainer
        @param cookie: cookie identifying the Task to be removed
        @type cookie: int
        @return: the removed Task
        @rtype: L{Task}
        @precondition: the Task is managed by the TaskContainer
        @postcondition: the Task is not managed by the TaskContainer 
        @raise NotImplemented:
        @raise DoesNotExist:
        @raise Timeout:
        @raise NoSuccess:
        @note: if a Task was added more than once, it can be removed only once - see notes to add().
        @note: if the Task identified by the cookie is not in the TaskContainer, a 'DoesNotExist' exception is thrown.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to remove the
                  Task from the TaskContainer.
                  
        """

    def run(self):
        """
        Start all asynchronous operations in the TaskContainer
        @summary:  start all asynchronous operations in the TaskContainer.
        @precondition: all Tasks in the container are in 'NEW' state.
        @postcondition: all Tasks in the comtainer are in 'RUNNING' state.
        @permission: see permissions on Task.run()
        @raise NotImplemented:
        @raise IncorrectState:
        @raise DoesNotExist:
        @raise Timeout:
        @raise NoSuccess:
        @note: run() causes an 'IncorrectState' exception if any of the Tasks in the container causes
                  that exception on run().
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to run one or
                  more Tasks in the container.
        @note: if the TaskContainer is empty, an 'DoesNotExist' exception is thrown.
        @note: As the order of execution of the Tasks is undefined, no assumption on the individual
                  Task states can be made after any exception gets thrown.
        """
        
    def wait(self, mode, timeout):
        """
        Wait for one or more of the Tasks to finish
        @summary:  wait for one or more of the Tasks to finish
        @param mode: wait for All or Any Task
        @param timeout: seconds to wait
        @type mode: int
        @type timeout: float
        @return: finished Task or one of all the finished Tasks
        @rtype: L{Task}
        @postcondition: if no timeout occurs, All/Any Tasks in the container are in a final state.
        @raise NotImplemented:
        @raise IncorrectState:
        @raise DoesNotExist:
        @raise Timeout:
        @raise NoSuccess:
        @note: if mode is 'ALL", the wait call returns only if all Tasks in the container are finished,
                  or on timeout, whichever occurs first. The output Task is then any of the finished Tasks.
        @note: if mode is 'Any', the wait call returns on the first Task which would return on Task.wait() in
                  that timeout period, and returns that Task.
        @note: the default wait mode is 'ALL" (0).
        @note: the returned Task is removed from the container, which allows constructs like::
                    while tc.size() > 0:
                         task = tc.wait (WaitMode.ANY) 
                         ...
                    
        @note: wait() MAY cause an 'IncorrectState' exception if any of the Tasks in the container causes
                  that exception on wait().
        @note: if the TaskContainer is empty, an 'DoesNotExist' exception is thrown.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to wait for one
                  or more Tasks in the container.
        @note: As the order of execution of the Tasks is undefined, no assumption on the individual
                  Task states can be made after any exception gets thrown.
        @note: for timeout semantics, see Section 2 of the GFD-R-P.90 document
        """
        
    def cancel(self, timeout):
        """
        Cancel all the asynchronous operations in the container
        @summary:  cancel all the asynchronous operations in the container
        @param timeout:              time for freeing resources
        @type timeout: float
        @postcondition: if no timeout occurs, all Tasks in the container are in 'CANCELED' state.
        @raise NotImplemented:
        @raise IncorrectState:
        @raise DoesNotExist:
        @raise Timeout:
        @raise NoSuccess:
        @note: see semantics of Task cancel.
        @note: cancel() MUST cause an 'IncorrectState' exception if any of the Tasks in the container
                  causes that exception on cancel().
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to run one or
                  more Tasks in the container.
        @note: if the TaskContainer is empty, a 'DoesNotExist' exception is thrown.
        @note: As the order of execution of the Tasks is undefined, no assumption on the individual
                  Task states can be made after any exception gets thrown.
        """

    def size(self):
        """
        Return the number of Tasks in the TaskContainer
        @summary:  return the number of Tasks in the TaskContainer
        @return: number of Tasks in TaskContainer
        @rtype: int
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to 
            list the Tasks in the container.
        """
        
    def list_tasks(self):
        """
        @summary: List the Tasks in the TaskContainer.
        @return: tuple of cookies for all Tasks in TaskContainer
        @rtype: tuple
        @raise   NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to list the
                  Tasks in the container.
        """
        
    def get_task(self, cookie):
        """
        Get a single Task from the TaskContainer
        @summary:  get a single Task from the TaskContainer
        @param cookie: the cookie identifying the Task to return
        @type cookie: int
        @return: the Task identified by cookie
        @rtype: L{Task}
        @raise NotImplemented:
        @raise DoesNotExist:
        @raise Timeout:
        @raise NoSuccess:
        @note: the returned Task is NOT removed from the TaskContainer.
        @note: if cookie specifies a Task which is not in the  container, a 'DoesNotExist' exception is thrown.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to list the
                  Tasks in the container.
        """
    
    def get_tasks(self):
        """
        Get the Tasks in the TaskContainer 
        @summary: get the Tasks in the TaskContainer
        @return: list of Tasks in TaskContainer
        @rtype: list
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: the returned Tasks are NOT removed from the TaskContainer.
        @note: if the TaskContainer is empty, an empty list is returned.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to list the
                 Tasks in the container.
        """
        
    def get_states(self):
        """
        Get the states of all Tasks in the TaskContainer
        @summary: get the states of all Tasks in the TaskContainer.
        @return: list of states for Tasks in TaskContainer
        @raise NotImplemented:
        @raise Timeout:
        @raise NoSuccess:
        @note: the returned list is not ordered
        @note: if the TaskContainer is empty, an empty list is returned.
        @note: a 'Timeout' or 'NoSuccess' exception indicates that the backend was not able to obtain the
                 states of the Tasks in the container.
        """