#  Copyright (c) 2005-2007 Andre Merzky (andre@merzky.net)
# 
#  Distributed under the Boost Software License, Version 1.0. (See accompanying
#  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

ifndef SAGA_MK_INC_CONF_POSTGRES
       SAGA_MK_INC_CONF_POSTGRES = yes

############################################################
# 
# POSTGRESQL
#
include /Users/luckow/workspace/saga-cpr-svn/adaptors/default/config//make.cfg

ifeq "$(SAGA_HAVE_POSTGRESQL)" "yes"
  SAGA_POSTGRESQL_LOCATION  = 
  SAGA_POSTGRESQL_INC_FLAGS = 
  SAGA_POSTGRESQL_LIB_FLAGS = 
  SAGA_POSTGRESQL_S_LIBS    = 

  SAGA_CPPINCS             += $(SAGA_POSTGRESQL_INC_FLAGS)
  SAGA_LDFLAGS_EXT         += $(SAGA_POSTGRESQL_LIB_FLAGS)
  SAGA_S_LIBS              += $(SAGA_POSTGRESQL_S_LIBS)
endif
# 
###########################################################

endif # guard

