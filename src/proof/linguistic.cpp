#include "fsc.h"
#include "etmrf.h"

#include "pttype.h"
#include "ptword.h"
#include "linguistic.h"
#include "suggestor.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

void CLinguistic::Open(const CFSFileName &FileName)
{
	if (m_pMorph) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::OPEN);
	}
	try {
		m_pMorph=new ETMRFAS(0, FileName, FSTSTR(""));
	} catch(const VEAD&) {
		Close();
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	} catch(...) {
		Close();
		throw;
	}
}

void CLinguistic::Close()
{
	try {
		IGNORE_FSEXCEPTION( delete m_pMorph; );
		m_pMorph=0;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

SPLRESULT CLinguistic::SpellWord(const CFSWString &szWord)
{
	try {
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		if (szWord.IsEmpty()) {
			return SPL_NOERROR;
		}

		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_SPL;
		if (!m_bAbbrevations) Flags&=(~MF_LYHREZH);
		if (!m_bRomanNumerals) Flags|=MF_ARAROOMA;
		m_pMorph->SetFlags(Flags);

		m_pMorph->Set1(szWord);
		LYLI Lyli;
		if (!m_pMorph->Flush(Lyli)) return SPL_NOERROR;
		ASSERT((Lyli.lipp & PRMS_MRF) && Lyli.ptr.pMrfAnal);
		if (!Lyli.ptr.pMrfAnal->on_tulem()) return SPL_INVALIDWORD;

		return SPL_NOERROR;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

CFSArray<SPLRESULT> CLinguistic::SpellWords(const CPTWordArray &Words)
{
	try {
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		CFSArray<SPLRESULT> Results;

		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_SPL;
		if (m_bCombineWords) Flags|=MF_V0TAKOKKU;
		if (!m_bAbbrevations) Flags&=(~MF_LYHREZH);
		if (!m_bRomanNumerals) Flags|=MF_ARAROOMA;
		m_pMorph->SetFlags(Flags);

		for (INTPTR ip=0; ip<Words.GetSize(); ip++){
			Results.AddItem(SPL_INVALIDWORD);
			m_pMorph->Set1(Words[ip].m_szWord);
			m_pMorph->Tag<int>((int)ip, PRMS_TAGSINT);
		}
		SPLRESULT lResult=SPL_INVALIDWORD;
		LYLI Lyli;
		while (m_pMorph->Flush(Lyli)){
			if (Lyli.lipp & PRMS_TAGSINT){
				INTPTR ipPos=Lyli.ptr.arv;
				ASSERT(ipPos<Words.GetSize());
				Results[ipPos]=lResult;
			}
			else if (Lyli.lipp & PRMS_MRF){
				lResult=(Lyli.ptr.pMrfAnal->on_tulem() ? SPL_NOERROR : SPL_INVALIDWORD);
			}
		}

		return Results;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

CFSWStringArray CLinguistic::Suggest(const CFSWString &szWord, bool bStartSentence)
{
	class CLinguisticSuggestor : public CSuggestor {
	public:
		CLinguisticSuggestor(ETMRFAS *pMorph) : m_pMorph(pMorph) { }
	protected:
		virtual SPLRESULT SpellWord(const CFSWString &szWord, CFSWString &szWordReal, long *pLevel) {
			m_pMorph->Clr();
			m_pMorph->Set1(szWord);
			LYLI Lyli;
			if (!m_pMorph->Flush(Lyli)) return SPL_NOERROR;
			ASSERT((Lyli.lipp & PRMS_MRF) && Lyli.ptr.pMrfAnal);
			if (!Lyli.ptr.pMrfAnal->on_tulem()) return SPL_INVALIDWORD;

			if (pLevel) *pLevel=Lyli.ptr.pMrfAnal->tagasiTasand;

			MRF_FLAGS Flags(MF_DFLT_SUG); FSXSTRING XString;
			(*Lyli.ptr.pMrfAnal)[0]->Strct2Strng(&XString, &Flags);
			szWordReal=XString;
			szWordReal.Remove(FSWSTR('_'));
			szWordReal.Trim();
			return SPL_NOERROR;
		}
		virtual void SetLevel(long lLevel){
			m_pMorph->SetMaxTasand(lLevel);
		}
		ETMRFAS *m_pMorph;
	};

	try{
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		CFSWStringArray Results;
		if (szWord.IsEmpty()) {
			return Results;
		}

		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		m_pMorph->SetFlags(MF_DFLT_SUG);
		CLinguisticSuggestor Suggestor(m_pMorph);
		Suggestor.Suggest(szWord);
		for (INTPTR ip=0; ip<Suggestor.GetSize(); ip++) {
			CFSWString szSuggestion;
			Suggestor.GetItem(ip, szSuggestion, 0);
			Results.AddItem(szSuggestion);
		}

		return Results;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

CFSArray<CMorphInfo> CLinguistic::Analyze(const CFSWString &szWord)
{
	try {
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		CFSArray<CMorphInfo> Results;
		if (szWord.IsEmpty()) {
			return Results;
		}

		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_MORFA &(~MF_V0TAKOKKU);
		if (!m_bAbbrevations) Flags&=(~MF_LYHREZH);
		if (!m_bRomanNumerals) Flags|=MF_ARAROOMA;
		if (m_bGuess) { Flags|=MF_OLETA; Flags&=(~MF_PIKADVALED); }
		if (m_bPhonetic) Flags|=MF_KR6NKSA;
		m_pMorph->SetFlags(Flags);

		m_pMorph->Set1(szWord);
		LYLI Lyli;
		if (!m_pMorph->Flush(Lyli)) return Results;
		Lyli.ptr.pMrfAnal->StrctKomadLahku();
		for (int i=0; i<Lyli.ptr.pMrfAnal->idxLast; i++){
			CMorphInfo MorphInfo1;
			MRFTULtoMorphInfo(MorphInfo1, *(*Lyli.ptr.pMrfAnal)[i]);
			Results.AddItem(MorphInfo1);
		}

		return Results;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

CFSArray<CMorphInfos> CLinguistic::AnalyzeSentense(const CPTWordArray &Words)
{
	try {
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		CFSArray<CMorphInfos> Result;
		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_MORFA | MF_YHESTA;
		if (!m_bCombineWords) Flags&=(~MF_V0TAKOKKU);
		if (!m_bAbbrevations) Flags&=(~MF_LYHREZH);
		if (!m_bRomanNumerals) Flags|=MF_ARAROOMA;
		if (m_bGuess) { Flags|=MF_OLETA; Flags&=(~MF_PIKADVALED); }
		if (m_bPhonetic) Flags|=MF_KR6NKSA;
		if (m_bProperName) Flags|=MF_LISAPNANAL;
		m_pMorph->SetFlags(Flags);

		m_pMorph->Set1(new LYLI(FSWSTR("<s>"), PRMS_TAGBOS));
		for (INTPTR ip=0; ip<Words.GetSize(); ip++){
			Result.AddItem(CMorphInfos());
			m_pMorph->Set1(Words[ip].m_szWord);
			m_pMorph->Tag<int>((int)ip, PRMS_TAGSINT);
		}
		m_pMorph->Set1(new LYLI(FSWSTR("</s>"), PRMS_TAGEOS));

		LYLI Lyli;
		CMorphInfos Result1;
		while (m_pMorph->Flush(Lyli)){
			if (Lyli.lipp == PRMS_TAGSINT){
				INTPTR ipPos=Lyli.ptr.arv;
				ASSERT(ipPos<Words.GetSize());
				Result[ipPos]=Result1;
				Result1=CMorphInfos();
			}
			else if (Lyli.lipp & PRMS_MRF){
				Lyli.ptr.pMrfAnal->StrctKomadLahku();
				MRFTULEMUSEDtoMorphInfos(Result1, *Lyli.ptr.pMrfAnal);
			}
		}

		return Result;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

CFSArray<CMorphInfo> CLinguistic::Synthesize(const CMorphInfo &MorphInfo, CFSWString szHint)
{
	try {
		if (!m_pMorph) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		CFSArray<CMorphInfo> Results;
		if (MorphInfo.m_szRoot.IsEmpty()) {
			return SPL_NOERROR;
		}

		m_pMorph->Clr();
		m_pMorph->SetMaxTasand();
		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_GEN &(~MF_V0TAKOKKU);
		if (m_bGuess) Flags|=MF_OLETA;
		if (m_bPhonetic) Flags|=MF_KR6NKSA;
		m_pMorph->SetFlags(Flags);

		MRFTUL GenInput;
		MorphInfotoMRFTUL(GenInput, MorphInfo);

		MRFTULEMUSED GenResult;
		if (m_pMorph->Synt(GenResult, GenInput, szHint) && GenResult.on_tulem()){
			for (INTPTR ip=0; GenResult[ip]; ip++){
				CMorphInfo MorphInfo1;
				MRFTULtoMorphInfo(MorphInfo1, *(GenResult[ip]));
				Results.AddItem(MorphInfo1);
			}
		}

		return Results;
	} catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}
