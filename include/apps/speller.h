#if !defined(_STLSPELLER_H_jfahsdjfgqwurwajdnfe_)
#define _STLSPELLER_H_jfahsdjfgqwurwajdnfe_

#include "proof.h"
#include <string>
#include <vector>

namespace vabamorf {

class exception : public std::exception {
public:
	exception() : std::exception() { }
};

class speller {
public:
	DECLARE_FSNOCOPY(speller);

#if defined(UNICODE)
	speller(const std::wstring &lex);
#else
	speller(const std::string &lex);
#endif
	virtual ~speller() { }

	bool spell(const std::wstring &word);
	std::vector< std::wstring > suggest(const std::wstring &word);

protected:
	CLinguistic linguistic;
};

} // namespace

#endif
