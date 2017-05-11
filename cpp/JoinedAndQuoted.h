#pragma once

#include <string>
#include <iosfwd>
#include <iomanip>

namespace multijob
{
namespace
{

template<class It>
class JoinedAndQuoted final
{
    std::string const m_sep;
    It m_begin;
    It const m_end;

public:
    JoinedAndQuoted(std::string sep, It begin, It end)
        : m_sep{sep}
        , m_begin{begin}
        , m_end{end}
    {}

    friend auto operator<<(std::ostream& out, JoinedAndQuoted const& self)
        -> std::ostream&
    {
        auto it = self.m_begin;

        bool want_comma = false;
        for (; it != self.m_end; ++it)
        {
            if (want_comma)
                out << ", ";
            want_comma = true;

            out << std::quoted(*it);
        }

        return out;
    }
};

template<class It>
auto joined_and_quoted(std::string sep, It begin, It end)
    -> JoinedAndQuoted<It>
{
    return {sep, begin, end};
}

}
}
