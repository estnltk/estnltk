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
#include "speller.h"

namespace vabamorf {

#if defined(UNICODE)
speller::speller(const std::wstring &lex)
#else
speller::speller(const std::string &lex)
#endif
{
	try {
		linguistic.Open(lex.c_str());
	} catch (...) {
		throw exception();
	}
}

bool speller::spell(const std::wstring &word)
{
	try {
		return (linguistic.SpellWord(word.c_str()) == SPL_NOERROR);
	} catch (...) {
		throw exception();
	}
}

std::vector< std::wstring > speller::suggest(const std::wstring &word)
{
	try {
		std::vector< std::wstring > results;
		CFSWStringArray suggs = linguistic.Suggest(word.c_str());
		for (INTPTR ip=0; ip<suggs.GetSize(); ip++) {
			results.push_back((const wchar_t *)suggs[ip]);
		}
		return results;
	} catch (...) {
		throw exception();
	}
}

} // namespace