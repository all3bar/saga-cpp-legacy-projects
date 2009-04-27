
#ifndef DIGGEDAG_DAG_IMPL_HPP
#define DIGGEDAG_DAG_IMPL_HPP

#include <map>

#include "dag.hpp"
#include "scheduler.hpp"


namespace diggedag
{
  namespace impl
  {
    class dag 
    {
      private:
        std::map    <std::string, diggedag::node> nodes_; // dag node names and instances
        std::vector <diggedag::edge>              edges_; // dag edge instances

        diggedag::scheduler scheduler_;
        state               state_;


      public:
        dag (void);
        ~dag (void); 

        void  add_node  (const std::string & name, 
                         diggedag::node    & node);
        void  add_edge  (diggedag::edge    & e, 
                         diggedag::node    & src, 
                         diggedag::node    & tgt);
        void  add_edge  (diggedag::edge    & e, 
                         const std::string & src, 
                         const std::string & tgt);
        void  fire      (void);
        void  wait      (void);
        state get_state (void);
        void  dump      (void);
        void  schedule  (diggedag::dag     & d);
    };

  } // namespace impl

} // namespace diggedag

#endif // DIGGEDAG_DAG_IMPL_HPP

