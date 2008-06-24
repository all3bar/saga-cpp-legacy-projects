#  Copyright (c) 2005-2007 Andre Merzky (andre@merzky.net)
# 
#  Distributed under the Boost Software License, Version 1.0. (See accompanying
#  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

ifndef SAGA_MK_INC_CONF_SQLITE3
       SAGA_MK_INC_CONF_SQLITE3 = yes

############################################################
# 
# SQLITE3
#

include /Users/luckow/workspace/saga-cpr-svn/adaptors/default/config//make.cfg

ifeq "$(SAGA_HAVE_SQLITE3)" "yes"
  SAGA_SQLITE3_LOCATION  = /usr
  SAGA_SQLITE3_INC_FLAGS = -I/usr/include/
  SAGA_SQLITE3_LIB_FLAGS = -L/usr/lib/ -lsqlite3
  SAGA_SQLITE3_S_LIBS    = 

  SAGA_CPPINCS          += $(SAGA_SQLITE3_INC_FLAGS)
  SAGA_LDFLAGS_EXT      += $(SAGA_SQLITE3_LIB_FLAGS)
  SAGA_S_LIBS           += $(SAGA_SQLITE3_S_LIBS)

  SAGA_CPPDEFS          += -DHAVE_SQLITE3_DTOR_TYPE=$(HAVE_SQLITE3_DTOR_TYPE)
endif
# 
###########################################################

endif # guard

