These are recipes for building conda packages.
Tested and built versions are for linux-64 python3.5 and windows-64 python3.5.

We depend on the conda-forge project for most of our dependencies and publish our own versions to the estnltk channel as needed.

To build:

`conda build -c estnltk -c conda-forge <recipe-directory>`