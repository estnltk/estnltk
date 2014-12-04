#include "../fsc/fsc.h"
#include "../etana/etmrf.h"

#include "pttype.h"
#include "ptword.h"
#include "linguistic.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

void CLinguistic::Open(const CFSFileName &FileName)
{
	if (m_pMorf) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::OPEN);
	}
	try{
		m_pMorf=new ETMRFA(0, FileName, FSTSTR(""));
	}catch(const VEAD&) {
		Close();
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}catch(...) {
		Close();
		throw;
	}
}

void CLinguistic::Close()
{
	try{
		IGNORE_FSEXCEPTION( delete m_pMorf; );
		m_pMorf=0;
	}catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

void CLinguistic::SetFlags(MRF_FLAGS_BASE_TYPE Flags)
{
	try{
		if (!m_pMorf) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		m_Flags=Flags;
		m_pMorf->SetFlags(m_Flags);
	}catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

void CLinguistic::SetLevel(long lLevel)
{
	try{
		if (!m_pMorf) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		m_pMorf->SetMaxTasand(lLevel);
	}catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

SPLRESULT CLinguistic::SpellWord(const CFSWString &szWord, CFSWString *pszRealWord, long *pLevel)
{
	try{
		if (!m_pMorf) {
			throw CLinguisticException(CLinguisticException::MAINDICT);
		}
		m_pMorf->Clr();
		m_pMorf->Set1(szWord);
		LYLI Lyli;
		if (!m_pMorf->Flush(Lyli)) return SPL_NOERROR;
		ASSERT((Lyli.lipp & PRMS_MRF) && Lyli.ptr.pMrfAnal);
		if (!Lyli.ptr.pMrfAnal->on_tulem()) return SPL_INVALIDWORD;

		if (pLevel) *pLevel=Lyli.ptr.pMrfAnal->tagasiTasand;

		if (pszRealWord){
			MRF_FLAGS Flags(m_Flags); FSXSTRING XString;
			(*Lyli.ptr.pMrfAnal)[0]->Strct2Strng(&XString, &Flags);
			CFSWString szStr=XString;
			szStr.Remove(FSWSTR('_'));
			szStr.Trim();
			(*pszRealWord)=szStr;
		}
		return SPL_NOERROR;
	}catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}

void CLinguistic::SpellWords(const CPTWordArray &Words, CFSArray<SPLRESULT> &Results)
{
	try{
		INTPTR ip;
		if (!m_pMorf) throw CLinguisticException(CLinguisticException::MAINDICT);
		m_pMorf->Clr();
		Results.Cleanup();
		for (ip=0; ip<Words.GetSize(); ip++){
			Results.AddItem(SPL_INVALIDWORD);
			m_pMorf->Set1(Words[ip].m_szWord);
			m_pMorf->Tag<int>((int)ip, PRMS_TAGSINT);
		}
		SPLRESULT lResult=SPL_INVALIDWORD;
		LYLI Lyli;
		while (m_pMorf->Flush(Lyli)){
			if (Lyli.lipp & PRMS_TAGSINT){
				INTPTR ipPos=Lyli.ptr.arv;
				ASSERT(ipPos<Words.GetSize());
				Results[ipPos]=lResult;
			}
			else if (Lyli.lipp & PRMS_MRF){
				lResult=(Lyli.ptr.pMrfAnal->on_tulem() ? SPL_NOERROR : SPL_INVALIDWORD);
			}
		}
	}catch(const VEAD&) {
		throw CLinguisticException(CLinguisticException::MAINDICT, CLinguisticException::UNDEFINED);
	}
}
