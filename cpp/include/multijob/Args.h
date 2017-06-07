#pragma once

#include <unordered_map>
#include <string>
#include <cstddef>

namespace multijob
{

using ID = std::uint32_t;

class Args final
{
    const ID m_job_id;
    const ID m_repetition_id;
    std::unordered_map<std::string, std::string> m_args;

public:

    Args(ID job_id, ID repetition_id, std::unordered_map<std::string, std::string> args)
        : m_job_id{job_id}
        , m_repetition_id{repetition_id}
        , m_args{std::move(args)}
    {}

    auto job_id() const -> ID { return m_job_id; }

    auto repetition_id() const -> ID { return m_repetition_id; }

    auto get_s(std::string const& name) -> std::string;

    auto get_i(std::string const& name) -> int;

    auto get_u(std::string const& name) -> unsigned int;

    auto get_d(std::string const& name) -> double;

    auto get_b(std::string const& name) -> bool;

    auto no_further_arguments() const -> void;
};

}
