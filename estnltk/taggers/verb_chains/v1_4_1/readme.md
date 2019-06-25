### Verb chain detector from the version v1.4.1

This folder contains source code (and additional resources) of the verb chain detector from EstNLTK's v1.4.1.

Entry point to the source is `verbchain_detector.py`, where class `VerbChainDetector` provides verb chain detection functionality. Note that it only operates on the _words / morphological analyses_ data structure of the version v1.4.1, so you need to convert the input data to the old data structure. 