# Core data structures of EstNLTK

* Layer is a sorted dictionary of spans.
* Each span specifies a segment or a list of segments in a text.
* Each span must have an annotation that consists of named attributes.

Layer is the only class to be used under normal circumstances.
All other classes are not intended to be used in application code unless you know what you are doing.
