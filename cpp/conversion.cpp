#include "conversion.h"

#include "MultijobError.h"

#include <iomanip>
#include <utility>

namespace multijob
{

namespace {

template<
    class Converter,
    class Result = decltype(std::declval<Converter>()("", nullptr))>
auto convert(
    std::string const& type_descr,
    std::string const& name,
    std::string const& s,
    Converter converter
    ) -> Result
{
    std::size_t consumed_chars = 0;

    Result result = [&] {
        try
        {
            return converter(s, &consumed_chars);
        }
        catch (std::invalid_argument const& ex)
        {
            throw MULTIJOB_ERROR(
                    "can't parse " << name << ": "
                    << std::quoted(s) << " is not " << type_descr << ": "
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
                << std::quoted(s) << " is not " << type_descr);
    }

    return result;
}

}

auto convert_str_to_i(std::string const& name, std::string const& s)
    -> int
{
    return convert("an integer number", name, s, [](auto&& str, auto&& pos){
        return std::stoi(str, pos, 0);
    });
}

auto convert_str_to_ul(std::string const& name, std::string const& s)
    -> unsigned long
{
    return convert("an unsigned integer number", name, s, [](auto&& str, auto&& pos){
        return std::stoul(str, pos, 0);
    });
}

auto convert_str_to_ld(std::string const& name, std::string const& s)
    -> double
{
    return convert("a floating point number", name, s, [](auto&& str, auto&& pos) {
        return std::stod(str, pos);
    });
}

}
