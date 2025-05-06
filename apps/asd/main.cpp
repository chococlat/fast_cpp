#include <iostream>
#include <string>
#include <filesystem>

#include "subdir/class.hpp"
#include "core/class.hpp"
#include <fmt/core.h>

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
    int age = 30;
    string name = "Max";

    // Format string with placeholders
    std::string message = fmt::format("Helloooo, {}! You are {} years old.", name, age);
    fmt::print("{}\n", message);
    system("PAUSE");
    return 0;
}
