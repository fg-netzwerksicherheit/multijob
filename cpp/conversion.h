#pragma once

#include <string>

namespace multijob
{

auto convert_str_to_i(std::string const& name, std::string const& str)
    -> int;

auto convert_str_to_ul(std::string const& name, std::string const& str)
    -> unsigned long;

auto convert_str_to_ld(std::string const& name, std::string const& str)
    -> double;

}
