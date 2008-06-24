// 
//  Distributed under the Boost Software License, Version 1.0. (See accompanying 
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)
#ifndef SAGA_ADAPTORS_MIGOL_LOGICALFILE_DATABASE_HPP
#define SAGA_ADAPTORS_MIGOL_LOGICALFILE_DATABASE_HPP
#include <jni.h>

// saga includes
#include <saga/saga.hpp>
#include <saga/impl/engine/ini/ini.hpp>
//#include <saga/packages/job/adaptors/job.hpp>
//#include <saga/packages/job/adaptors/job_self.hpp>
//#include <saga/adaptors/attribute.hpp>


#include <boost/utility.hpp>
#include <boost/thread/thread.hpp>
#include <boost/thread/mutex.hpp>
#include <boost/thread/condition.hpp>

///////////////////////////////////////////////////////////////////////////////
namespace cpr
{
    ///////////////////////////////////////////////////////////////////////////
    class migol      {
    public:
            //singleton getter
        static boost::shared_ptr<migol> instance() {
                if( NULL == migol_instance.get() ) {
                    migol_instance.reset( new migol() );
                }
                return migol_instance;
            };
        
        //singleton getter
        static boost::shared_ptr<migol> instance(saga::ini::ini adap_ini) {
            if( NULL == migol_instance.get() ) {
                migol_instance.reset( new migol(adap_ini) );
            }
            return migol_instance;
        };
        ~migol();
        
        static std::string init_migol_context(saga::ini::ini ini);
        std::string register_service(std::string url, std::string service_name, std::string state) ;
        bool change_service_state(std::string guid, std::string newState);
        bool register_checkpoint(std::string guid, std::string fileName);
        std::vector<saga::url> get_files (std::string guid);
        std::map<saga::url, std::map<std::string, std::string> > get_files_map (std::string guid);
        bool replicate(std::string guid, int automatic_replication);
        bool update_machine(std::string guid, std::string url);
        bool update_jobdescription(std::string guid, saga::job::description jd);
        static void init() {migol_instance.reset(new migol()); }
        std::string getUrl();
        
        
            //int register_checkpoint_directory(char *guid, char *directory);
    private:
        std::string ais_url;
        std::string globus_location;
        std::string guid;
        
        static boost::shared_ptr<migol> migol_instance; 
        //Singleton
        migol(saga::ini::ini adapt_ini);
        migol();
        
        //init ini file
        saga::ini::ini ini;
        void initIni();
        
        //for monitoring 
        //thread with gsoap server
        //typedef boost::mutex::scoped_lock
        //scoped_lock;
        
        //JNI Calls
        JavaVM *jvm;
        jclass ais_global_cls, crs_global_cls;
        //jmethodID mid_register_service, mid_register_check_point, mid_change_service_state;
        std::string jvmOptionString;
        std::string clientConfigOption;
        
        /* Pre-Declaration */
        std::string initJVMOptions();
        JNIEnv* initJVM();
        void printFault(JNIEnv*, std::string);
        std::string discoverClientConfig();
        int fileExists(std::string);
        void destroyJVM();
        
        int soap_port;
        volatile bool terminate;
        volatile bool initialized;
        void monitorable_server();
        
        
        std::string external_monitoring_host;
        void init_external_monitoring();
        pid_t reverse_proxy_pid;
        
        boost::thread monitorable_thread;
        boost::thread *reverse_proxy_thread;
        //boost::mutex mutex;
        //boost::condition cond;
        
        std::string get_ip (); 
        
       
        /**
         * Add all jars in dirname to classpath
         */
        void addJarsFromDir(std::string dirname, std::string& classpath);
       
    };
}

#endif // !SAGA_ADAPTORS_MIGOL_LOGICALFILE_DATABASE_HPP
