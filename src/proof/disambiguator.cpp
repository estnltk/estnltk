#include "fsc.h"
#include "etmrf.h"
#include "etmrfyhh.h"

#include "ptword.h"
#include "disambiguator.h"

//////////////////////////////////////////////////////////////////////
// Construction/Destruction
//////////////////////////////////////////////////////////////////////

void CDisambiguator::Open(const CFSFileName &FileName)
{
	if (m_pDisambiguator) {
		throw CDisambiguatorException(CDisambiguatorException::MAINDICT, CDisambiguatorException::OPEN);
	}
	try {
		m_pDisambiguator=new ET3(MF_DFLT_MORFY, FileName);
	} catch(const VEAD&) {
		Close();
		throw CDisambiguatorException(CDisambiguatorException::MAINDICT);
	} catch(...) {
		Close();
		throw;
	}
}

void CDisambiguator::Close()
{
	try {
		IGNORE_FSEXCEPTION( delete m_pDisambiguator; );
		m_pDisambiguator=0;
	} catch(const VEAD&) {
		throw CDisambiguatorException(CDisambiguatorException::MAINDICT);
	}
}

CFSArray<CMorphInfos> CDisambiguator::Disambiguate(const CFSArray<CMorphInfos> &Analysis)
{
	try {
		if (!m_pDisambiguator) {
			throw CDisambiguatorException(CDisambiguatorException::MAINDICT);
		}

		m_pDisambiguator->Clr();

		for (INTPTR ip=0; ip<Analysis.GetSize(); ip++) {
			MRFTULEMUSED MrfTulemused;
			MorphInfostoMRFTULEMUSED(MrfTulemused, Analysis[ip]);
			m_TagConverter.FsTags2YmmTags(&MrfTulemused);
			LYLI Lyli(MrfTulemused);
			m_pDisambiguator->Set1(Lyli);
		}

		CFSArray<CMorphInfos> Result;
		LYLI Lyli;
		while (m_pDisambiguator->Flush(Lyli)) {
			Lyli.ptr.pMrfAnal->StrctKomadLahku();
			CMorphInfos Result1;
			MRFTULEMUSEDtoMorphInfos(Result1, *Lyli.ptr.pMrfAnal);
			Result.AddItem(Result1);
		}
		return Result;
	} catch(const VEAD&) {
		throw CDisambiguatorException(CDisambiguatorException::MAINDICT);
	}
}
