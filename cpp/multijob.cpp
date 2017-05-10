#include "include/multijob.h"
#include "include/multijob/MultijobError.h"

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
            MULTIJOB_ERROR("can't split as argument: " << std::quoted(arg));

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

namespace multijob
{

auto parse_commandline(
        int argc,
        char const* const* argv,
        JobArgvConfig const& config)
    -> Args
{
    MapStrStr special_args;
    MapStrStr normal_args;
    std::tie(special_args, normal_args) = separate_argv(argc, argv, "--");

    auto job_id_it = special_args.find(config.job_id_key);
    if (job_id_it == special_args.end())
    {
        MULTIJOB_ERROR(
                "special job_id argument " <<
                std::quoted(config.job_id_key) << " required");
    }
    auto job_id_str = job_id_it->second;
    special_args.erase(job_id_it);

    auto repetition_id_it = special_args.find(config.repetition_id_key);
    if (repetition_id_it == special_args.end())
    {
        MULTIJOB_ERROR(
                "special repetition_id argument " <<
                std::quoted(config.repetition_id_key) << " required");
    }
    auto repetition_id_str = repetition_id_it->first;
    special_args.erase(repetition_id_it);

    if (special_args.size())
    {
        std::vector<std::string> keys;
        for (auto const& kv : special_args)
            keys.emplace_back(kv.first);
        std::sort(keys.begin(), keys.end());

        MULTIJOB_ERROR(
                "unknown special arguments before " << std::quoted("--") <<
                " separator: " <<
                joined_and_quoted(", ", keys.begin(), keys.end()));
    }

    std::size_t consumed_chars = 0;
    ID job_id = ID(std::stoul(job_id_str, &consumed_chars));
    if (consumed_chars != job_id_str.size())
    {
        MULTIJOB_ERROR(
                "can't parse job_id: " << std::quoted(job_id_str));
    }

    consumed_chars = 0;
    ID repetition_id = ID(std::stoul(repetition_id_str, &consumed_chars));
    if (consumed_chars != repetition_id_str.size())
    {
        MULTIJOB_ERROR(
                "can't parse repetition_id: " << std::quoted(repetition_id_str));
    }

    return {job_id, repetition_id, normal_args};
}

}
