/** Functions to speed up dividing and splitting algorithms in Estnltk's Text class

These are meant to be used for splitting layers.
Has optimized code for both simple and multi layers.
Duplicates the functionality of pure-Python divide module.
*/

#include <utility>
#include <vector>
#include <string>
#include <unordered_set>
#include <algorithm>

/// spans are simple start, end position pairs
typedef std::pair<int, int> Span;

/// SpanVector can represent fully a simple layer
/// or a element of a multi layer
typedef std::vector<Span> SpanVector;

/// spanvectors typically represent a multi layer
typedef std::vector<SpanVector> SpanVectors;

/// spans with associated index
typedef std::pair<Span, int> IndexedSpan;
typedef std::vector<IndexedSpan> IndexedSpanVector;


typedef std::vector<int> IntVector;
typedef std::vector<IntVector> IntVectors;
