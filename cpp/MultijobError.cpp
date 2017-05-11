#include "MultijobError.h"

namespace multijob {

auto MultijobError::what() const noexcept -> char const*
{
    // only overridden to silence some VTable-related warnings
    return std::runtime_error::what();
}

}
