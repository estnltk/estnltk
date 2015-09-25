/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
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
