#pragma once

#include <multijob/Args.h>

namespace multijob
{

struct JobArgvConfig final {
    std::string job_id_key;
    std::string repetition_id_key;

    JobArgvConfig()
        : job_id_key{"--id"}
        , repetition_id_key{"--rep"}
    {}
};

auto parse_commandline(
        int argc,
        char const* const* argv,
        JobArgvConfig const& = {})
    -> Args;

}
