/*
 *  job.hpp
 *  FAUST - Framework for Adaptive Ubiquitous Scalable Tasks
 *
 *  Created by Ole Weidner on 11/22/08.
 *  Copyright 2008 Center for Computation & Technology. All rights reserved.
 *
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying 
 *  LICENSE file or copy at http://www.boost.org/LICENSE_1_0.txt)
 */

#ifndef FAUST_MANYJOBS_JOB_HPP
#define FAUST_MANYJOBS_JOB_HPP

#include <boost/shared_ptr.hpp>

#include <faust/faust/exports.hpp>
#include <faust/faust/manyjobs/state.hpp>
#include <faust/faust/manyjobs/description.hpp>

namespace faust
{
  // fwd. decl. implementation class // 
  ///@cond - exclude from Doxygen
  namespace impl { namespace manyjobs { class job_impl; class service_impl; } }
  ///@endcond - exclude from Doxygen


  namespace manyjobs {

    /*! \brief The %job provides the manageability interface to a %job 
     *         instance submitted through a manyjob %service instance. 
     *         It can't be instanciated directly, only thourgh the create_job
     *         factory method. 
     */
    class FAUST_EXPORT job : public saga::object
    {
    
      // service impl. class needs to be friend to call private c'tor 
      friend class faust::impl::manyjobs::service_impl;
      
    private:

      typedef boost::shared_ptr<faust::impl::manyjobs::job_impl> impl_ptr;
      impl_ptr impl;
      
      job();
            
    public:
            
      /*! \brief Tries to run this %job instance. 
       *
       */
      void run();
      
      /*! \brief Tries to wait for this %job instance to complete.
       *
       */
      bool wait(double timeout = -1.0);

      /*! \brief Tries to cancel this %job instance.
       *
       */
      bool cancel(double timeout = -1.0);

      /*! \brief Tries to suspend this %job instance.
       *
       */
      bool suspend();

      /*! \brief Tries to resume this %job instance.
       *
       */
      bool resume();

      /*! \brief Returns this %job instance's %job ID.
       *  
       */      
      std::string get_job_id();
      
      /*! \brief Tries to return this %job instance's state.
       *
       */
      faust::manyjobs::state get_state();
      
      /*! \brief Returns this %job instance's description.
       *
       */
      faust::manyjobs::description get_description();

    };
  }
}

#endif /* FAUST_MANYJOBS_JOB_HPP */
