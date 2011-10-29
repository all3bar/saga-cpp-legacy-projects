""" 
This file contains the API for the (proposed) TROY PilotData Framework.
"""
class State(object):
    Unknown = 0
    New = 1
    Running = 2
    Done = 3
    Canceled = 4
    Failed = 5
    Pending = 6
#
# TROY PilotStore Description
#
class PilotStoreDescription(dict):
    """ TROY PilotStoreDescription.
        {
            'service_url': "ssh://localhost/tmp/pilotstore/",
            'size':100                                
        }    
    """
    
    def __init__(self):
        pass
    

#
# TROY PilotStore
#
class PilotStore(object):
    """ TROY PilotStore.  """

    # Class members
    __slots__ = (
        'id',           # Reference to this PJ
        'description',  # Description of PilotStore
        'context',      # SAGA context
        'resource_url', # Resource  URL       
        'state',        # State of the PilotStore
        'state_detail', # Adaptor specific state of the PilotStore       
    )

    def cancel(self):        
        """ Cancel PilotStore 

            Keyword arguments:
            None
        """
        pass
    
    
    def get_state(self):
        pass
    
    def get_state_detail(self):
        pass

#
# TROY PilotStore Service
#
class PilotStoreService(object):
    """ TROY PilotStoreService (PSS).
    """

    # Class members
    __slots__ = (
        'id',           # Reference to this PJS
        'state',       # Status of the PJS
        'pilot_stores'    # List of PJs under this PJS
    )

    def __init__(self, pss_id=None):
        """ Create a PilotStoreService

            Keyword arguments:
            pss_id -- restore from pss_id
        """
        pass

    def create_pilotstore(self, pilotstore_desc):
        """ Create a PilotStore 

            Keyword arguments:
            pilotstore_desc -- PilotStore Description            
            
            Return value:
            A PilotStore handle
        """
        pass

    def list_pilotstores(self):
        """ List all PSs of PSS """
        pass

    def cancel(self):
        """ Cancel the PilotStoreService.
            
            Keyword arguments:
            None

            Return value:
            Result of operation
        """
        pass


#
# TROY PilotDataService
# 
class PilotDataService(object):
    """ TROY PilotDataService (PDS).   
        
    """

    # Class members
    __slots__ = (
        'id',                # id to this PilotDataService
        'state',             # Status of the PilotDataService
        'pilot_stores',      # PilotStores connected to this PD
        'pilot_data'         # List of PDs
    )

    def __init__(self, pds_id=None):
        """ Create a PilotDataService.

            Keyword arguments:
            pds_id -- Reconnect to an existing PilotDataService 
        """
        pass

    def add(self, pss):
        """ Add a PilotStoreService 

            Keyword arguments:
            pss -- The PilotStoreService to add.

            Return:
            Result
        """
        pass

    def remove(self, pss):
        """ Remove a PilotStoreService 

            
            Keyword arguments:
            pss -- The PilotStoreService to remove 
            Return:
            Result
        """
        pass
    
    def list_pilotdata(self):
        """ List all PDs of PDS """
        pass

    
    def cancel(self):
        """ Cancel the PDS.            
            
            Keyword arguments:
            None

            Return:
            Result
        """
        pass



#
# TROY PilotDataDescription
# 
class PilotDataDescription(dict):
    """ TROY PilotDataDescription.
        {
            'file_urls': [file1, file2, file3]        
        } 
    """

    def __init__(self):
        pass


#
# TROY PilotData 
# 
class PilotData(object):
    """ TROY PilotData. Holds a set of data units.        
    """

    # Class members
    __slots__ = (
        'id',               # Reference 
        'description',      # Description
        'state',            # State
        'data_units'        # DU managed by PilotData object
    )

    def cancel(self):
        """ Cancel the PD. """
        pass
    
    def add_data_unit(self, data_unit):
        pass
    
    def remove_data_unit(self, data_unit):
        pass
    
    def list_data_units(self):
        pass
        
    def get_state(self):
        pass    
    

class DataUnit(object):
    """ TROY DataUnit """

    __slots__ = (
        'id',        
        'url'
    )
    
    def __init__(self):
        pass
    
    
    
    