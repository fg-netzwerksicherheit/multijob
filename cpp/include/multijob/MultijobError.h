#pragma once

#include <stdexcept>
#include <sstream>

#define MULTIJOB_ERROR(msg_stream_operations) \
    do { \
        std::ostringstream _multijob_err_msg; \
        _multijob_err_msg << "multijob: " << msg_stream_operations; \
        throw multijob::MultijobError{multijob::MultijobError::tag_no_prefix{}, _multijob_err_msg.str()}; \
    } while (false)

namespace multijob
{

class MultijobError final : public std::runtime_error
{
public:
    struct tag_no_prefix {};

    explicit MultijobError(std::string const& message)
        : MultijobError{tag_no_prefix{}, "multijob: " + message}
    {}

    MultijobError(tag_no_prefix, std::string const& message)
        : std::runtime_error{message}
    {}

    auto what() const noexcept -> char const* override;
};

}
