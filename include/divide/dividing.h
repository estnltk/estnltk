/* Functions to speed up dividing and splitting algorithms in Estnltk's Text class

Duplicates the functionality of pure-Python divide module.
*/

#include <pair>
#include <vector>
#include <string>
#include <unordered_set>
#include <algorithm>

typedef std::pair<int, int> Span;
typedef std::vector<Span> SpanVector;
typedef std::vector<SpanVector> SpanVectors;

typedef std::pair<Span, int> IndexedSpan;
typedef std::vector<IndexedSpan> IndexedSpanVector;

typedef std::vector<int> IntVector;
typedef std::vector<IntVector> IntVectors;
