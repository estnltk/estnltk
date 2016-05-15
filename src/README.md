Vabamorf wrapper in Estnltk
===========================

Current version of vabamorf in Estnltk is https://github.com/estnltk/estnltk/commit/3b0c6d1c7a8d0ed875d1ab5dddc081bee1d9bf66

Current setup requires migrating changes in vabamorf into estnltk manually, going through commits in vabamorf library and
copying relevant parts of relevant files. Fortunately, the number of updates and commits is small and the manual approach is feasible.
After the migrations, please update the vabamorf commit number in this readme.

There are a number of other differences that you should be aware of:

1. Vabamorf code is distributed in folders `lib/etana`, `lib/etsyn` etc (See https://github.com/Filosoft/vabamorf/tree/master/lib) having both the `.h` and `.cpp` files in the same folder. Estnltk has separate `include` and `src` folders for include and source files (See https://github.com/estnltk/estnltk/tree/devel/include and https://github.com/estnltk/estnltk/tree/devel/src).
2. `#include` directives in vabamorf use relative paths (for example `#include <../etana/etana.h>`) while estnltk uses canonical `#include <etana.h>`.
3. Estnltk files have License headers.
4. Estnltk code is missing code for OpenOffice speller integration.
5. Estnltk has heavily changed `#ifdef` statements in `include/fsc/stdfsc.h` file in order to make vabamorf compile in Python setuptools environment.

