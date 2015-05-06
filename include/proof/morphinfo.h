#if !defined _MORPHINFO_H_DFGAVADFGERFSVSDGERRWEFSFFG_
#define _MORPHINFO_H_DFGAVADFGERFSVSDGERRWEFSFFG_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

class CMorphInfo {
public:
	CMorphInfo() : m_cPOS(0) { }

	CFSWString m_szRoot;
	CFSWString m_szEnding;
	CFSWString m_szClitic;
	wchar_t m_cPOS;
	CFSWString m_szForm;
};

class CMorphInfos {
public:
	CFSWString m_szWord;
	CFSArray<CMorphInfo> m_MorphInfo;
};

inline void MRFTULtoMorphInfo(CMorphInfo &MorphInfo, const MRFTUL &Tul)
{
	MorphInfo.m_szRoot=Tul.tyvi;
	MorphInfo.m_szEnding=Tul.lopp;
	MorphInfo.m_szClitic=Tul.kigi;
	MorphInfo.m_cPOS=Tul.sl[0];
	MorphInfo.m_szForm=Tul.vormid;
	MorphInfo.m_szForm.TrimRight(L", ");
}

inline void MorphInfotoMRFTUL(MRFTUL &Tul, const CMorphInfo &MorphInfo)
{
	Tul.tyvi=MorphInfo.m_szRoot;
	Tul.lopp=MorphInfo.m_szEnding;
	Tul.kigi=MorphInfo.m_szClitic;
	Tul.sl=MorphInfo.m_cPOS;
	Tul.vormid=MorphInfo.m_szForm;
	if (!MorphInfo.m_szForm.IsEmpty()) {
		Tul.vormid+=L", ";
	}
}

inline void MRFTULEMUSEDtoMorphInfos(CMorphInfos &MorphInfos, const MRFTULEMUSED &Tul)
{
	MorphInfos.m_szWord=Tul.s6na;
	MorphInfos.m_MorphInfo.Cleanup();
	for (int i=0; i<Tul.idxLast; i++){
		CMorphInfo MorphInfo1;
		MRFTULtoMorphInfo(MorphInfo1, *Tul[i]);
		MorphInfos.m_MorphInfo.AddItem(MorphInfo1);
	}
}

inline void MorphInfostoMRFTULEMUSED(MRFTULEMUSED &Tul, const CMorphInfos &MorphInfos)
{
	Tul.Stop();
	Tul.s6na=MorphInfos.m_szWord;
	for (INTPTR ip=0; ip<MorphInfos.m_MorphInfo.GetSize(); ip++) {
		MRFTUL MrfTul;
		MorphInfotoMRFTUL(MrfTul, MorphInfos.m_MorphInfo[ip]);
		Tul.AddClone(MrfTul);
	}
}

#endif // _MORPHINFO_H_DFGAVADFGERFSVSDGERRWEFSFFG_
