/*
 *  resource_monitor_impl.hpp 
 *  FAUST - Framework for Adaptive Ubiquitous Scalable Tasks
 *  Website: https://macpro01.cct.lsu.edu/trac/faust
 *
 *  Created by Ole Weidner <oweidner@cct.lsu.edu> on 02/13/09.
 *  Copyright 2008-2009 Center for Computation & Technology. 
 *
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying 
 *  LICENSE file or copy at http://www.boost.org/LICENSE_1_0.txt)
 */

#ifndef FAUST_IMPL_RESOURCE_MONITOR_IMPL_HPP
#define FAUST_IMPL_RESOURCE_MONITOR_IMPL_HPP

#include <faust/faust/exports.hpp>
#include <faust/faust/description.hpp>
#include <faust/impl/object_impl.hpp>

#include <saga/impl/engine/attribute.hpp>

namespace faust
{
  namespace impl 
  {
    //////////////////////////////////////////////////////////////////////////
    //
    class resource_monitor : public faust::impl::object, 
    public saga::impl::attribute
    {

    private:
      
      saga::advert::entry monitor_adv_;
      
    public:
      
      resource_monitor(saga::advert::entry & monitor_adv);
      
      saga::impl::attribute* get_attributes() { return this; }
      saga::impl::attribute const* get_attributes() const { return this; }
      
      saga::impl::attribute_cache get_cache() {return attributes_;}
			
    };
    //
    //////////////////////////////////////////////////////////////////////////
  }
}

#endif /* FAUST_IMPL_JOB_IMPL_HPP */

