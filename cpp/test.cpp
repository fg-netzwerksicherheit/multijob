#include "include/multijob.h"

#include <iostream>
#include <string>
#include <typeinfo>
#include <stdexcept>
#include <vector>
#include <memory>

#pragma clang diagnostic ignored "-Wshadow"

namespace
{
    template<class A, class B>
    auto default_comparator(A&& a, B&& b) -> bool { return a == b; }
}

class Test final
{
    struct Statistics final {
        std::size_t tests = 0;
        std::size_t passed = 0;
        std::size_t failed = 0;

        Statistics() = default;
    };

    std::shared_ptr<Statistics> m_stats;
    std::ostream& m_out;
    std::string m_name;
    std::size_t m_indent;

    std::string indent() const { return std::string(m_indent, ' '); }

public:

    Test(
            std::ostream& out,
            std::string name = "",
            std::size_t indent = 0,
            std::shared_ptr<Statistics> stats = nullptr)
        : m_stats{ stats ? stats : std::shared_ptr<Statistics>{ new Statistics() } }
        , m_out{out}
        , m_name{name}
        , m_indent{indent}
    {}

    Test(Test const&) = delete;

    auto print_plan() -> void
    {
        m_out
            << indent()
            << "# " << m_stats->tests << " tests: "
            << m_stats->passed << " passed, "
            << m_stats->failed << " failed" << std::endl;
        m_out
            << indent()
            << "1.." << m_stats->tests << std::endl;
    }

    auto get_clamped_failed() const -> int {
        if (m_stats->failed > 0xff - 1)
            return 0xff - 1;
        return int(m_stats->failed);
    }

    auto ok(std::string const& name, bool is_ok)
    {
        ++m_stats->tests;
        if (is_ok)
        {
            ++m_stats->passed;
        }
        else
        {
            ++m_stats->failed;
        }

        m_out
            << indent()
            << (is_ok ? "ok" : "not ok")
            << " " << m_stats->tests
            << " - " << name
            << std::endl;
    }

    template<class A, class B, class Comparator = decltype(default_comparator<A, B>)>
    auto is(
            std::string const& name,
            A&& got,
            B&& expected,
            Comparator comparator = default_comparator<A, B>)
    {
        bool test = comparator(std::forward<A>(got), std::forward<B>(expected));
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
        return ok(name, body_was_completed && s.m_stats->failed == 0);
    }

    template<class Body>
    auto describe(std::string const& item_name, Body body) -> void
    {
        std::string name = (m_name.empty())
            ? item_name
            : m_name + "::" + item_name;

        Test s{m_out, name, m_indent, m_stats};

        bool body_was_completed = s.execute(body);

        if (!body_was_completed)
            return ok(name, false);
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

void describe_parse_commandline(Test&);
void describe_Args(Test&);

int main(int, char**) {
    Test t{std::cout};

    t.describe("parse_commandline()", describe_parse_commandline);

    t.describe("Args", describe_Args);

    t.print_plan();
    return t.get_clamped_failed();
}

void describe_parse_commandline(Test& t) {

    t.it("decodes IDs", [&](auto& t) {
        int const argc = 5;
        char const* const argv[] = {
            "self", "--id=4", "--rep=7", "--", "a=b",
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
                {"self", "--id=0", "--"}},
            {"missing --id",
                {"self", "--rep=0", "--"}},
            {"unknown special arg",
                {"self", "--id=0", "--rep=0", "--this doesn't exist=0", "--"}},
            {"Id is not numeric",
                {"self", "--id=x", "--rep=0", "--"}},
            {"Rep is not numeric",
                {"self", "--id=0", "--rep=x", "--"}},
            {"special arg has no value",
                {"self", "--id", "--rep=0", "--"}},
            {"arg has no value",
                {"self", "--id=0", "--rep=0", "--", "x"}},
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

}

void describe_Args(Test& t)
{
    t.describe("no_further_arguments()", [&](auto& t) {

        t.it("does nothing when all items were consumed", [&](auto&) {
            multijob::Args args { 4, 7, { { "a", "b" }, { "c", "d" } } };
            args.get_s("a");
            args.get_s("c");
            args.no_further_arguments();
        });

        t.it("throws when items remain", [&](auto& t) {
            multijob::Args args { 57, 3, { { "z", "y"}, { "a", "b" } } };

            t.template throws<std::runtime_error>("because items remain", [&](auto&) {
                args.no_further_arguments();
            });
        });

    });

    t.describe("get_i", [&](auto& t) {

        t.it("works", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "403"}} };
            t.is("expected result", args.get_i("a"), 403);
        });

        t.it("can be negative", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "-17"}} };
            t.is("expected result", args.get_i("a"), -17);
        });

        t.it("throws for non-integers", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "4.2"}} };
            t.template throws<std::runtime_error>("", [&](auto&) {
                args.get_i("a");
            });
        });

        t.it("throws when out of range", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", std::string(100, '9')}} };
            t.template throws<std::runtime_error>("", [&](auto&) {
                args.get_i("a");
            });
        });

    });

    t.describe("get_u", [&](auto& t) {

        t.it("works", [&](auto& t) {
            multijob::Args args { 4, 6, {{"a", "403"}} };
            std::size_t result = args.get_u("a");
            t.is("expected result", result, unsigned{403});
        });

        t.it("throws for non-integers", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "0foo"}} };
            t.template throws<std::runtime_error>("", [&](auto&) {
                args.get_u("a");
            });
        });

        t.it("throws when negative", [&](auto& t) {
            multijob::Args args { 3, 8, {{"a", "-5"}} };
            t.template throws<std::runtime_error>("", [&](auto&) {
                args.get_u("a");
            });
        });

    });

    t.describe("get_d", [&](auto& t) {

        t.it("works", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "40.0123E2"}} };
            t.is("expected result", args.get_d("a"), 4001.23, [](double a, double b)
            {
                return !(a < b || b < a);
            });
        });

        t.it("throws for non-doubles", [&](auto& t) {
            multijob::Args args { 4, 5, {{"a", "42x"}} };
            t.template throws<std::runtime_error>("", [&](auto&) {
                args.get_d("a");
            });
        });

    });

    t.describe("get_b", [&](auto& t) {

        t.it("works", [&](auto& t) {
            std::vector<std::pair<std::string, bool>> cases {
                {"True", true},
                {"true", true},
                {"False", false},
                {"false", false},
            };

            for (auto const& c : cases)
            {
                multijob::Args args { 4, 6, {{"a", c.first}} };
                t.is(c.first, args.get_b("a"), c.second);
            }
        });

        t.it("throws for invalid formats", [&](auto& t) {
            std::vector<std::string> cases { "1", "0", "yes", "no", "t", "f" };

            for (auto const& not_accepted : cases)
            {
                multijob::Args args { 4, 5, {{"a", not_accepted}} };
                t.template throws<std::runtime_error>(not_accepted, [&](auto&) {
                    args.get_b("a");
                });
            }
        });

    });

}
