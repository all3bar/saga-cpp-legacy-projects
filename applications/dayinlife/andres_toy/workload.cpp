
#include <stdio.h>

#include "workload.hpp"

#define DEFAULT_MAX   25
#define BUFSIZE      100


// ctor
workload::workload (logger & log, int argc, char** argv)
  : max_ (DEFAULT_MAX)
  , log_ (log)
{
  log_.log (" -- wl ctor\n");

  if ( argc >= 2 )
  {
    max_ = atoi (argv[2]);

    log_.log (" -- setting max to ");
    log_.log (max_);
    log_.log ("\n");
  }
}


// dtor
workload::~workload (void)
{
  log_.log (" -- wl dtor\n");
}


// someone tells us where the input data are.  We open that file, and read our
// two data items.  After that the input file is useless, and gets removed.
void workload::set_input (std::string in)
{
  log_.log (" -- wl set_input: ");
  log_.log (in);
  log_.log ("\n");

  // open input
  f_in_.open (in.c_str (), std::fstream::in);

  if ( f_in_.is_open () )
  {
    std::string tmp;

    // read data
    f_in_ >> tmp;   // "max:"
    f_in_ >> max_;
    f_in_ >> tmp;   // "cnt:"
    f_in_ >> cnt_;

    f_in_.close ();

    // remove input file
    ::remove (in.c_str ());
  }
  else
  {
    // default: start from zero
    log_.log (" -- wl has no input - reset\n");
    cnt_ = 0;   
  }

  return;
}


// someone tells us where we are supposed to store output data.  We open that
// file (to check if thats a valid location), and save the handle for later I/O
void workload::set_output (std::string out)
{
  log_.log (" -- wl set_output: ");
  log_.log (out);
  log_.log ("\n");

  // check if valid - throw if not
  f_out_.open (out.c_str (), std::fstream::out);
}



// we perform one chunk of work.  When that is done, we store the intermediate
// data in the earlier opened output file.
void workload::work (void)
{
  log_.log (" -- wl work\n");

  // check if there is something to do
  if ( test () )
  {

    log_.log (" -- old count: ");
    log_.log (cnt_);
    log_.log ("\n");

    cnt_++;

    log_.log (" -- new count: ");
    log_.log (cnt_);
    log_.log ("\n");
  }
  else
  {
    log_.log (" -- wl has nothing to do\n");
    log_.log (" -- count: ");
    log_.log (cnt_);
    log_.log ("\n");
  }


  // write data
  //
  // we do that even if there is nothing to do, to recreate the state we had
  // before running
  f_out_ << "max: " << max_ << std::endl;
  f_out_ << "cnt: " << cnt_ << std::endl;

  f_out_.close ();
}



// this routine determines if work() managed to finish our _global_ task.  If
// not, it returns true, indicating that we need to continue
bool workload::test (void) 
{
  log_.log (" -- wl test:   ");
  log_.log (cnt_);
  log_.log (" >= ");
  log_.log (max_);
  log_.log ("\n");

  // we are only done if the counter exceeds max_.
  if ( cnt_ >= max_ )
    return false;
  else
    return true;
}

