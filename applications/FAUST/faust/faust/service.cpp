/*
 *  service.cpp
 *  FAUST - Framework for Adaptive Ubiquitous Scalable Tasks
 *  Website: https://macpro01.cct.lsu.edu/trac/faust
 *
 *  Created by Ole Weidner <oweidner@cct.lsu.edu> on 11/22/08.
 *  Copyright 2008-2009 Center for Computation & Technology. 
 *
 *  Distributed under the Boost Software License, Version 1.0. (See accompanying 
 *  LICENSE file or copy at http://www.boost.org/LICENSE_1_0.txt)
 */

#include <faust/faust/service.hpp>
#include <faust/impl/service_impl.hpp>

using namespace faust;

////////////////////////////////////////////////////////////////////////////////
//
boost::shared_ptr <faust::impl::service_impl> service::get_impl (void) const
{ 
  typedef faust::object base_type;
  
  return boost::static_pointer_cast 
    <faust::impl::service_impl> (this->base_type::get_impl ());
}

////////////////////////////////////////////////////////////////////////////////
//
service::service (std::vector<faust::resource> resource_vector, int num_jobs)
: faust::object (new faust::impl::service_impl(resource_vector, num_jobs), object::Service)
{
}

////////////////////////////////////////////////////////////////////////////////
//
service::~service()
{
}

////////////////////////////////////////////////////////////////////////////////
//
job service::create_job(job_description job_desc)
{
  return get_impl()->create_job(job_desc);
}

////////////////////////////////////////////////////////////////////////////////
//
job service::create_job(job_description job_desc, std::string job_id, dependency dep)
{
  return get_impl()->create_job(job_desc, job_id, dep);
}

////////////////////////////////////////////////////////////////////////////////
//
job service::create_job(job_description job_desc, job job_obj, dependency dep)
{
  return get_impl()->create_job(job_desc, job_obj, dep);
}

/*////////////////////////////////////////////////////////////////////////////////
//
job service::create_job(description job_desc, job_group job_group_obj, dependency dep)
{
  return get_impl()->create_job(job_desc, job_group_obj, dep);
}

////////////////////////////////////////////////////////////////////////////////
//
job_group service::create_job_group(std::vector<description> job_descs)
{
  return get_impl()->create_job_group(job_descs);
}

////////////////////////////////////////////////////////////////////////////////
//
job_group service::create_job_group(std::vector<description> job_descs, 
                           std::string dep_job, dependency dep)
{
  return get_impl()->create_job_group(job_descs, dep_job, dep);
}

////////////////////////////////////////////////////////////////////////////////
//
job_group service::create_job_group(std::vector<description> job_descs, 
                                    job job_obj, dependency dep)
{
  return get_impl()->create_job_group(job_descs, job_obj, dep);
}

////////////////////////////////////////////////////////////////////////////////
//
job_group service::create_job_group(std::vector<description> job_descs, 
                                    job_group job_group_obj, dependency dep)
{
  return get_impl()->create_job_group(job_descs, job_group_obj, dep);
}*/

////////////////////////////////////////////////////////////////////////////////
//
std::vector<std::string> service::list_jobs()
{
  return get_impl()->list_jobs();
}

////////////////////////////////////////////////////////////////////////////////
//
std::vector<std::string> service::list_resource_descriptions()
{
  return get_impl()->list_resource_descriptions();
}

////////////////////////////////////////////////////////////////////////////////
//
faust::job service::get_job(std::string job_id)
{
  return get_impl()->get_job(job_id);
}

////////////////////////////////////////////////////////////////////////////////
//
faust::resource_description service::get_resource_description(std::string contact)
{
  return get_impl()->get_resource_description(contact);
}

////////////////////////////////////////////////////////////////////////////////
//
/*faust::job_group service::get_job_group(std::string job_id)
{
  return get_impl()->get_job_group(job_id);
}
*/
