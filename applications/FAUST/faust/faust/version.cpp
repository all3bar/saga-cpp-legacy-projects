/*
 *  version.cpp
 *  FAUST - Framework for Adaptive Ubiquitous Scalable Tasks
 *  Website: https://macpro01.cct.lsu.edu/trac/faust
 *
 *  Created by Ole Weidner <oweidner@cct.lsu.edu> on 11/22/08.
 *  Copyright 2008-2009 Center for Computation & Technology. 
 *
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying 
 *  LICENSE file or copy at http://www.boost.org/LICENSE_1_0.txt)
 */

#include <boost/preprocessor/stringize.hpp>
#include <faust/faust/version.hpp>

///////////////////////////////////////////////////////////////////////////////
//

namespace faust 
{  
  unsigned long get_faust_version (void)
  {
    return FAUST_VERSION_FULL;
  }
  
  ///@cond - exclude from Doxygen
  char const FAUST_CHECK_VERSION[] = BOOST_PP_STRINGIZE(FAUST_CHECK_VERSION);
  ///@endcond - exclude from Doxygen
  
}

//
///////////////////////////////////////////////////////////////////////////////
