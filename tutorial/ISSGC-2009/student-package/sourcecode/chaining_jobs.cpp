//  Copyright (c) 2005-2009 Hartmut Kaiser
// 
//  Distributed under the Boost Software License, Version 1.0. (See accompanying 
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include <iostream>
#include <saga/saga.hpp>
#include <boost/thread.hpp>

///////////////////////////////////////////////////////////////////////////////
// The chaining_jobs example tries to overcome one of the limitations of the 
// hello_world example: it introduces dependencies between 3 (possibly remotely)
// spawned childs. In this example the next child will be spawned only after 
// the previous one has finished its execution. To make it more interesting we 
// now use /usr/bin/bc to do some calculations, where the result of the previous
// calculation is used as the input for the next one.
//
// Try to make more complex calculations if you like!
///////////////////////////////////////////////////////////////////////////////

///////////////////////////////////////////////////////////////////////////////
// The host names to run the spawned jobs on. For the sake of simplicity this 
// example needs to be modified in order to use different host names than the 
// local machine. Please change the 3 macros below to the host names you want
// the 3 childs to be spawned on.
///////////////////////////////////////////////////////////////////////////////
#define HOST1 "localhost"
#define HOST2 "localhost"
#define HOST3 "localhost"

///////////////////////////////////////////////////////////////////////////////
// the routine spawning the SAGA jobs and waiting for their results
std::string increment(std::string host, std::string argument)
{
    try {
        saga::job::service js (host);
        saga::job::ostream in;
        saga::job::istream out;
        saga::job::istream err;

        // run the job
        saga::job::job j = js.run_job("/usr/bin/bc -q", host, in, out, err);

        // wait for the job to finish
        saga::job::state s = j.get_state();
        while (s != saga::job::Running && s != saga::job::Failed)
            s = j.get_state();

        // if the job didn't start successfully, print error message
        if (s == saga::job::Failed) {
            std::cerr << "SAGA job: " << j.get_job_id() << " failed (state: " 
                      << saga::job::detail::get_state_name(s) << ")\n";
            return argument;
        }

        // feed the remote process some input
        in << "1 + " + argument + "\n";

        // receive result
        std::string line;
        std::getline(out, line);

        // quit remote process
        in << "quit\n";

        return line;
    }
    catch (saga::exception const& e) {
        std::cerr << "saga::exception caught: " << e.what () << std::endl;
    }
    catch (std::exception const& e) {
        std::cerr << "std::exception caught: " << e.what () << std::endl;
    }
    catch (...) {
        std::cerr << "unexpected exception caught" << std::endl;
    }
    return argument;    // by default just return argument
}

///////////////////////////////////////////////////////////////////////////////
int main(int argc, char* argv[])
{
    // run 3 separate threads executing the saga calls
    std::string result = increment(HOST1, "1");
    result = increment(HOST2, result);
    result = increment(HOST3, result);

    std::cout << "The overall result is: " << result << std::endl;

    return 0;
}
