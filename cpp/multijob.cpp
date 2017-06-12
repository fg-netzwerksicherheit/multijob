#include "include/multijob.h"
#include "MultijobError.h"
#include "JoinedAndQuoted.h"
#include "conversion.h"

#include <string>
#include <iomanip>
#include <tuple>
#include <algorithm>

namespace
{
    auto split_arg(std::string const& arg)
        -> std::pair<std::string, std::string>
    {
        auto sep_pos = arg.find('=');

        if (sep_pos == std::string::npos)
            throw MULTIJOB_ERROR("can't split as argument: " << std::quoted(arg));

        auto key    = arg.substr(0, sep_pos);
        auto value  = arg.substr(sep_pos + 1);

        return {key, value};
    }

    using MapStrStr = std::unordered_map<std::string, std::string>;

    auto separate_argv(
            int argc,
            char const* const* argv,
            std::string const& sep)
        -> std::pair<MapStrStr, MapStrStr>
    {
        char const* const* end = &argv[argc];

        MapStrStr special_args;
        for (; argv != end; ++argv)
        {
            if (*argv == sep)
                break;

            std::string key;
            std::string value;
            std::tie(key, value) = split_arg(*argv);
            special_args[key] = std::move(value);
        }

        if (argv != end)
            ++argv;

        MapStrStr normal_args;
        for (; argv != end; ++argv)
        {
            std::string key;
            std::string value;
            std::tie(key, value) = split_arg(*argv);
            normal_args[key] = std::move(value);
        }

        return {std::move(special_args), std::move(normal_args)};
    }

  }

namespace multijob
{

auto parse_commandline(
        int argc,
        char const* const* argv,
        JobArgvConfig const& config)
    -> Args
{
    // skip argv[0], which is the executable name
    --argc;
    ++argv;

    MapStrStr special_args;
    MapStrStr normal_args;
    std::tie(special_args, normal_args) = separate_argv(argc, argv, "--");

    auto job_id_it = special_args.find(config.job_id_key);
    if (job_id_it == special_args.end())
    {
        throw MULTIJOB_ERROR(
                "special job_id argument " <<
                std::quoted(config.job_id_key) << " required");
    }
    auto job_id_str = job_id_it->second;
    special_args.erase(job_id_it);

    auto repetition_id_it = special_args.find(config.repetition_id_key);
    if (repetition_id_it == special_args.end())
    {
        throw MULTIJOB_ERROR(
                "special repetition_id argument " <<
                std::quoted(config.repetition_id_key) << " required");
    }
    auto repetition_id_str = repetition_id_it->second;
    special_args.erase(repetition_id_it);

    if (special_args.size())
    {
        std::vector<std::string> keys;
        for (auto const& kv : special_args)
            keys.emplace_back(kv.first);
        std::sort(keys.begin(), keys.end());

        throw MULTIJOB_ERROR(
                "unknown special arguments before " << std::quoted("--") <<
                " separator: " <<
                joined_and_quoted(", ", keys.begin(), keys.end()));
    }

    ID job_id = ID(convert_str_to_ul("job_id", job_id_str));
    ID repetition_id = ID(convert_str_to_ul("repetition_id", repetition_id_str));

    return {job_id, repetition_id, normal_args};
}

}
