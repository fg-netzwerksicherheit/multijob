#include "include/multijob.h"

#include <iostream>
#include <string>
#include <typeinfo>
#include <stdexcept>
#include <vector>

#pragma clang diagnostic ignored "-Wshadow"

class Test final
{
    std::size_t m_test = 0;
    std::size_t m_passed = 0;
    std::size_t m_failed = 0;
    std::ostream& m_out;
    std::string m_name;
    std::size_t m_indent;

    std::string indent() const { return std::string(m_indent, ' '); }

public:

    Test(std::ostream& out, std::string name = "", std::size_t indent = 0)
        : m_out{out}
        , m_name{name}
        , m_indent{indent}
    {}

    Test(Test const&) = delete;

    auto print_plan() -> void
    {
        m_out
            << indent()
            << "# " << m_test << " tests: "
            << m_passed << " passed, "
            << m_failed << " failed" << std::endl;
        m_out
            << indent()
            << "1.." << m_test << std::endl;
    }

    auto get_clamped_failed() const -> int {
        if (m_failed > 0xff - 1)
            return 0xff - 1;
        return int(m_failed);
    }

    auto ok(std::string const& name, bool is_ok)
    {
        ++m_test;
        if (is_ok)
        {
            ++m_passed;
        }
        else
        {
            ++m_failed;
        }

        m_out
            << indent()
            << (is_ok ? "ok" : "not ok")
            << " " << m_test
            << " - " << name
            << std::endl;
    }

    template<class A, class B>
    auto is(std::string const& name, A&& got, B&& expected)
    {
        bool test = got == expected;
        ok(name, test);
        if (!test)
        {
            m_out
                << indent()
                << "#      got: (" << got << ")" << std::endl
                << "# expected: (" << expected << ")" << std::endl;
        }
    }

    template<class Error, class Body>
    auto throws(std::string const& when_something_happens, Body body) -> void
    {
        using namespace std::string_literals;
        std::string name = "throws "s + typeid(Error).name() + " "s + when_something_happens;

        try
        {
            body(*this);
        }
        catch (Error const& ex)
        {
            return ok(name, true);
        }

        return ok(name, false);
    }

    template<class Body>
    auto execute(Body body) -> bool
    {
        try
        {
            body(*this);
            return true;
        }
        catch (std::exception const& ex)
        {
            m_out
                << indent()
                << "# caught exception " << typeid(ex).name()
                << ": " << ex.what()
                << std::endl;
            return false;
        }
        catch (...)
        {
            m_out
                << indent()
                << "# caught unknown exception"
                << std::endl;
            return false;
        }
    }

    template<class Body>
    auto subtest(std::string const& name, Body body) -> void
    {
        m_out
            << indent()
            << "# subtest " << name << std::endl;

        Test s{m_out, name, m_indent + 2};

        bool body_was_completed = s.execute(body);

        s.print_plan();
        return ok(name, body_was_completed && s.m_failed == 0);
    }

    template<class Body>
    auto describe(std::string const& item_name, Body body) -> void
    {
        std::string name = (m_name.empty())
            ? item_name
            : m_name + "::" + item_name;
        return subtest(name, body);
    }

    template<class Body>
    auto it(std::string const& does_something, Body body) -> void
    {
        std::string name = (m_name.empty())
            ? does_something
            : m_name + " " + does_something;
        return subtest(name, body);
    }
};

int main(int, char**) {
    Test t{std::cout};

    t.describe("parse_commandline()", [&](auto& t) {

        t.it("decodes IDs", [&](auto& t) {
            int const argc = 4;
            char const* const argv[] = {
                "--id=4", "--rep=7", "--", "a=b",
            };

            multijob::Args args = multijob::parse_commandline(argc, argv);

            t.is("job_id",
                    args.job_id(), unsigned(4));
            t.is("repetition_id",
                    args.repetition_id(), unsigned(7));

            t.is("get_s(\"a\")",
                    args.get_s("a"), "b");

            t.template throws<std::runtime_error>("get_s(\"nonexistent\")", [&](auto&) {
                args.get_s("nonexistent");
            });

        });

        t.it("raises errors for malformed command lines", [&](auto& t) {
            std::vector<std::pair<std::string, std::vector<char const*>>> cases = {
                {"missing --rep",
                    {"--id=0", "--"}},
                {"missing --id",
                    {"--rep=0", "--"}},
                {"unknown special arg",
                    {"--id=0", "--rep=0", "--this doesn't exist=0", "--"}},
                {"Id is not numeric",
                    {"--id=x", "--rep=0", "--"}},
                {"Rep is not numeric",
                    {"--id=0", "--rep=x", "--"}},
                {"special arg has no value",
                    {"--id", "--rep=0", "--"}},
                {"arg has no value",
                    {"--id=0", "--rep=0", "--", "x=y"}},
            };

            for (auto const& c : cases)
            {
                std::string const name = c.first;
                int const argc = static_cast<int>(c.second.size());
                char const* const* const argv = c.second.data();
                t.template throws<std::runtime_error>("because " + name, [&](auto&) {
                    multijob::Args args = multijob::parse_commandline(
                            argc, argv);
                });
            }
        });

    });

    t.print_plan();
    return t.get_clamped_failed();
}
