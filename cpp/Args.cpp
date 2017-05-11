#include "include/multijob/Args.h"
#include "MultijobError.h"
#include "JoinedAndQuoted.h"

#include <vector>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include <stdexcept>

namespace multijob
{

auto Args::no_further_arguments() const -> void
{
    if (this->m_args.empty())
        return;

    // gather keys for error message
    std::vector<std::string> keys;
    for (auto const& kv : m_args)
        keys.emplace_back(kv.first);


    std::sort(keys.begin(), keys.end());

    throw MULTIJOB_ERROR(
            "params were not consumed: " <<
            joined_and_quoted(", ", keys.begin(), keys.end()));
}

auto Args::get_s(std::string const& name) -> std::string
{
    auto result_it = m_args.find(name);

    if (result_it == m_args.end())
    {
        throw MULTIJOB_ERROR(
                "param does not exist: " << std::quoted(name));
    }

    auto result = result_it->second;

    m_args.erase(result_it);

    return result;
}

auto Args::get_i(std::string const& name) -> int
{
    auto s = get_s(name);
    std::size_t consumed_chars = 0;
    int result = std::stoi(s, &consumed_chars);

    if (consumed_chars != s.size()) {
        throw MULTIJOB_ERROR(
                "param " << std::quoted(name) <<
                " is not integer: " << std::quoted(s));
    }

    return result;
}

auto Args::get_d(std::string const& name) -> double
{
    auto s = get_s(name);
    std::size_t consumed_chars = 0;
    double result = std::stod(s, &consumed_chars);

    if (consumed_chars != s.size())
    {
        throw MULTIJOB_ERROR(
                "param " << std::quoted(name) <<
                " is not double: " << std::quoted(s));
    }

    return result;
}

auto Args::get_b(std::string const& name) -> bool
{
    auto s = get_s(name);

    if (s == "True" || s == "true")
        return true;

    if (s == "False" || s == "false")
        return false;

    throw MULTIJOB_ERROR(
            "param " << std::quoted(name) <<
            " is not boolean: " << std::quoted(s));
}

}
