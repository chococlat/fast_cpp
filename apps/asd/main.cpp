
#include <iostream>
#include <string>
#include <filesystem>

#include "subdir/class.hpp"
#include <boost/interprocess/managed_shared_memory.hpp>

using std::cin;
using std::cout;
using std::string;
namespace fs = std::filesystem;

int main(){
    boost::interprocess::managed_shared_memory segment{boost::interprocess::open_or_create, "asd", 65536};
    std::cout << "Hello Worlds!\n";
    int unused_var = 42;
    return 0;
}
