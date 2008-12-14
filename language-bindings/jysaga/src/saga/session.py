# Package: saga
# Module: session 
# Description: The module which specifies the session used in saga
# Specification and documentation can be found in section 3.5, 
#    page 75-80 of the GFD-R-P.90 document
# Author: P.F.A. van Zoolingen, Computer Systems Section, Faculty of 
#    Exact Science (FEW), Vrije Universiteit, Amsterdam, The Netherlands.


from saga.object import Object, ObjectType
from saga.attributes import Attributes
from saga.error import NotImplemented, BadParameter
from saga.context import Context

from org.ogf.saga.session import Session, SessionFactory
from org.ogf.saga.context import ContextFactory

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

class Session(Object):
    """
    The session object provides the functionality of a session, which isolates in-
    dependent sets of SAGA objects from each other. Sessions also support the
    management of security information
    """
        
    def __init__(self, default=True, **impl):
        """
        Initialize the object.
        @summary: Initialize the object.
        @param default: indicates this object should be the default session 
        @type default: bool
        @raise NotImplemented:
        @raise NoSuccess:
        @Note: the created session has no context instances attached.
        @note: if 'default' is specified as 'True', the constructor returns a shallow copy of the
             default session, with all the default contexts attached. The application can then
             change the properties of the default session, which is continued to be implicetly used on
             the creation of all saga objects, unless specified otherwise.
        """
        self.delegateObject = None
        if "delegateObject" in impl:
            if impl["delegateObject"].__class__ is not org.ogf.saga.session.Session:
                raise BadParameter, "Parameter impl[\"delegateObject\"] is not a org.ogf.saga.session.Session. Type: " + str(impl["delegateObject"].__class__)
            self.delegateObject = impl["delegateObject"]
        else:
            if default == True:
                self.delegateObject = SessionFactory.createSession()
            else:
                self.delegateObject = SessionFactory.createSession(False)
#TODO: check type of default    
        
    def add_context(self, context):
        """
        Attach a security context to a session.
        @summary: Attach a security context to a session.
        @param context: Security context to add
        @type context: L{Context}
        @PostCondition: the added context is deep copied, and no state is shared.
        @postcondition: any object within that session can use the context, even if 
            it was created before add_context() was called.
        @raise NotImplemented:
        @Note: if the session already has a context attached which has exactly the same set of attribute
            values as the parameter context, no action is taken.

        """
        if type(context) is not Context:
            raise BadParameter, "Parameter context is not of type Context but " + str(type(context))
        try:
            self.delegateObject.addContext(context.delegateObject)
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)

    def remove_context(self, context):
        """
        Detach a security context from a session.
        @summary: Detach a security context from a session.
        @param context: Security context to remove
        @type context: L{Context}
        @raise NotImplemented:
        @raise DoesNotExist:
        @PreCondition: a context with completely identical attributes is available in the session.
        @PostCondition: that context is removed from the session, and can from now on not be used by any object in
              that session, even if it was created before remove_context() was called.
        @Note: this methods removes the context on the session which has exactly the same set of
              parameter values as the parameter context.
        @note: a 'DoesNotExist' exception is raised if no context exist on the session which has the
              same attributes as the parameter context.

        """
        if type(context) is not Context:
            raise BadParameter, "Parameter context is not of type Context but " + str(type(context))
        try:
            self.delegateObject.removeContext(context.delegateObject)
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)
#DOCUMENT: removeContext() doesn't work yet
        
    def list_contexts(self):
        """
        Retrieve all contexts attached to a session.
        @summary: Retrieve all contexts attached to a session.
        @return: contexts of this session
        @rtype: list
        @raise NotImplemented:
        @Note: a empty list is returned if no context is attached.
        @note: contexts may get added to a session by default, hence the returned list may be
              non-empty even if add_context() was never called before.
        @note: a context might still be in use even if not included in the returned list. See notes
              about context life time in the GFD-R-P.90 document.
        """
        javaArray = None
        retval = []
        try:
            javaArray = self.delegateObject.listContexts()
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)
        if (len(javaArray)) is 0:
            return retval
        else:
            for i in range(len(javaArray)):
                retval.append( Context(delegateObject=javaArray[i]))
            return retval

#    def get_id(self): Inherited from Object
#    def get_session(self): Inherited from Object
#    def clone(self): Inherited from Object
 
    def get_type(self):
        """
        Query the object type.
        @summary: Query the object type.
        @return: type of the object as an int from ObjectType
        @rtype: int
        """
        return ObjectType.SESSION

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
        try:
            javaClone = self.delegateObject.clone()
            clone = Session(delegateObject=javaClone)
            return clone
        except org.ogf.saga.error.SagaException, e:
            raise self.convertException(e)
    
    contexts = property(list_contexts,
            doc="""Contexts attached to a session\n@type: list""")
