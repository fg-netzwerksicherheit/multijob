# Multijob C++ interface

This library allows you to implement C++ executables that understand the command line interface expected by Multijob.

    #include <multijob.h>

    void your_ea(std::string a, int b, double c, bool d);

    // ./your-program --id=4 --rep=7 -- a="foo bar" b=123 c=4.5 d=False
    int main(int argc, char** argv) {
        multijob::Args args = multijob::parse_commandline(argc, argv);

        std::string a = args.get_s("a");
        int         b = args.get_i("b");
        double      c = args.get_d("c");
        bool        d = args.get_b("d");

        args.no_further_arguments();

        your_ea(a, b, c, d);

        return 0;
    }

## How to install

Within this directory, run:

    $ make
    $ sudo make install

This will install Multijob under "/usr/local".

If you want to install in a custom directory (e.g. `./multijob`), you can specify a PREFIX:

    $ make install PREFIX=`pwd`/multijob

To use this library, you need to add compiler flags:

 -  add `.../include` to your include search path:

        -I .../include

 -  add `.../lib` to your library search path, and link to Multijob:

        -L .../lib -lmultijob
