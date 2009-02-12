/*
 *  job_group_impl.hpp 
 *  FAUST - Framework for Adaptive Ubiquitous Scalable Tasks
 *  Website: https://macpro01.cct.lsu.edu/trac/faust
 *
 *  Created by Ole Weidner <oweidner@cct.lsu.edu> on 11/30/08.
 *  Copyright 2008-2009 Center for Computation & Technology. 
 *
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying 
 *  LICENSE file or copy at http://www.boost.org/LICENSE_1_0.txt)
 */

#ifndef FAUST_IMPL_JOB_GROUP_IMPL_HPP
#define FAUST_IMPL_JOB_GROUP_IMPL_HPP

#include <faust/faust/exports.hpp>
#include <faust/faust/job.hpp>
#include <faust/faust/state.hpp>
#include <faust/faust/description.hpp>

#include <faust/impl/object_impl.hpp>

namespace faust
{
  namespace impl
  {
    //////////////////////////////////////////////////////////////////////////
    //
    class  job_group : public faust::impl::object
    {
        
      private:
        
        std::string jobid_;
        
      public:
        
        job_group();
        void run();
        bool wait(double timeout = -1.0);
        bool cancel(double timeout = -1.0);
        bool suspend();
        bool resume();
        std::string get_job_id();
        std::vector<std::string> list_jobs();
    };
    //
    //////////////////////////////////////////////////////////////////////////
  }
}

#endif /* FAUST_IMPL_JOB_GROUP_IMPL_HPP */