#include <iostream>
#include <string>
#include <filesystem>

#include "subdir/class.hpp"
#include "core/class.hpp"

using std::cin;
using std::cout;
using std::string;
using std::wcin;
using std::wcout;
using std::wstring;
namespace fs = std::filesystem;

int main(){
    std::wcout << "Hello World! from asd\n";

    core::MyClass mc;
    mc.say_hello();
    system("PAUSE");
    return 0;
}
