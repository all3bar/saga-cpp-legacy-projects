//  Copyright (c) 2008 Michael Miceli and Christopher Miceli
// 
//  Distributed under the Boost Software License, Version 1.0. (See accompanying 
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#include "AllPairsBase.hpp"
#include "../utils/type.hpp"

using namespace AllPairs;

double comp_matrix[4][4] = {
{0.0, 1.0, 2.0, 2.5},
{0.0, 0.0, 2.0, 1.5},
{1.0, 1.0, 0.0, 1.0},
{0.0, 1.5, 2.0, 0.0}};

class AllPairsImpl : public AllPairsBase<AllPairsImpl> {
  public:
   AllPairsImpl(int argCount, char **argList)
     : AllPairsBase<AllPairsImpl>(argCount, argList) {}
   double compare(saga::url object1, saga::url object2) {
      saga::filesystem::file f(object1, saga::filesystem::ReadWrite);
      saga::filesystem::file g(object2, saga::filesystem::ReadWrite);
      return 0.2;
   }
};

/*********************************************************
 * This is the entry point for the worker, the master    *
 * will call this, there is no need to ever call this    *
 * directly.                                             *
 * ******************************************************/
int main(int argc,char **argv) {
   //putenv("SAGA_VERBOSE=100");
   std::freopen("/tmp/worker-stderr.txt", "w", stderr);
   std::freopen("/tmp/worker-stdout.txt", "w", stdout);
   try {
      AllPairsImpl allPairs(argc, argv);
      allPairs.run();
   }
   catch (saga::exception const& e) {
      std::cerr << "Saga:  exception caught: " << e.what() << std::endl;
      std::cerr << "Exiting..." << std::endl;
   }
   catch (std::exception const& e) {
      std::cerr << "std:  exception caught: " << e.what() << std::endl;
      std::cerr << "Exiting..." << std::endl;
   }
   catch (...) {
      std::cerr << "FATAL Exception caught!" << std::endl << "Exiting..." << std::endl;
      return 255;
   }
   return 0;
}
