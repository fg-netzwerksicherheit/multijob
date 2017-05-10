#include "include/multijob/Args.h"
#include "include/multijob/MultijobError.h"

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

    std::ostringstream err_msg;
    err_msg << "params were not consumed: ";

    bool want_comma = false;
    for (auto const& k : keys)
    {
        if (want_comma)
            err_msg << ", ";
        err_msg << std::quoted(k);
        want_comma = true;
    }

    throw MultijobError(err_msg.str());
}

auto Args::get_s(std::string const& name) -> std::string
{
    auto result = m_args.at(name);
    m_args.erase(name);
    return result;
}

auto Args::get_i(std::string const& name) -> int
{
    auto s = get_s(name);
    std::size_t consumed_chars = 0;
    int result = std::stoi(s, &consumed_chars);

    if (consumed_chars != s.size()) {
        MULTIJOB_ERROR(
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
        MULTIJOB_ERROR(
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

    MULTIJOB_ERROR(
            "param " << std::quoted(name) <<
            " is not boolean: " << std::quoted(s));
}

}
