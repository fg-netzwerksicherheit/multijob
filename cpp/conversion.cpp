#include "conversion.h"

#include "MultijobError.h"

#include <iomanip>

namespace multijob
{

auto convert_str_to_ul(std::string const& name, std::string const& s)
    -> unsigned long
{
    std::size_t consumed_chars = 0;

    unsigned long result = [&] {
        try
        {
            return std::stoul(s, &consumed_chars);
        }
        catch (std::invalid_argument const& ex)
        {
            throw MULTIJOB_ERROR(
                    "can't parse " << name << ": "
                    << std::quoted(s) << " is not numeric: "
                    << ex.what());
        }
        catch (std::out_of_range const& ex)
        {
            throw MULTIJOB_ERROR(
                    "can't parse " << name << ": "
                    << std::quoted(s) << " is out of range: "
                    << ex.what());
        }
    }();

    if (consumed_chars != s.size())
    {
        throw MULTIJOB_ERROR(
                "can't parse " << name << ": "
                << std::quoted(s) << " is not numeric");
    }

    return result;
}

}
