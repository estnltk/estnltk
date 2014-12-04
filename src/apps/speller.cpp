#include "speller.h"

namespace openmorf {

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
		linguistic.SetFlags(MF_DFLT_SPL | MF_LUBAMITMIKUO);
		linguistic.SetLevel(100);
		return (linguistic.SpellWord(word.c_str()) == SPL_NOERROR);
	} catch (...) {
		throw exception();
	}
}

class suggestor : public CSuggestor
{
public:
	suggestor(CLinguistic *pLinguistic) : m_pLinguistic(pLinguistic) { }
	virtual SPLRESULT SpellWord(const CFSWString &szWord, CFSWString &szWordReal, long *pLevel) {
		if (pLevel) *pLevel=1;
		return m_pLinguistic->SpellWord(szWord, &szWordReal, pLevel);
	}

	virtual void SetLevel(long lLevel) { m_pLinguistic->SetLevel(lLevel); }
protected:
	CLinguistic *m_pLinguistic;
};

std::vector< std::wstring > speller::suggest(const std::wstring &word)
{
	try {
		std::vector< std::wstring > result;
		linguistic.SetFlags(MF_DFLT_SUG | MF_LUBAMITMIKUO);
		linguistic.SetLevel(100);
		suggestor sugg(&linguistic);
		sugg.SetTimeOut(3.0);
		sugg.Suggest(word.c_str());
		for (INTPTR ip=0; ip<sugg.GetSize(); ip++) {
			CFSWString suggestion;
			sugg.GetItem(ip, suggestion, 0);
			result.push_back((const wchar_t *)suggestion);
		}
		return result;
	} catch (...) {
		throw exception();
	}
}

} // namespace