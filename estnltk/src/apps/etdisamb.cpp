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
#include "json.h"
#include "proof.h"

class CMyJSONReader : public CJSONReader {
public:
	CMyJSONReader(CFSStream &Stream, CDisambiguator &Disambiguator, CJSONWriter &Writer) : CJSONReader(Stream), m_Disambiguator(Disambiguator), m_Writer(Writer) { }

protected:
	void OnValReadStart(const CFSAString &szKey) {
		if (szKey.IsEmpty()) {
			m_Writer.ObjectStart();
		} else if (szKey=="/paragraphs") {
			m_Writer.Key("paragraphs");
			m_Writer.ArrayStart();
			m_iCollectData--;
		} else if (KeyMatch(szKey, "/paragraphs/%d")) {
			m_Writer.ObjectStart();
			m_iCollectData++;
		} else if (KeyMatch(szKey, "/paragraphs/%d/sentences")) {
			m_Writer.Key("sentences");
			m_Writer.ArrayStart();
			m_iCollectData--;
		} else if (KeyMatch(szKey, "/paragraphs/%d/sentences/%d")) {
			m_iCollectData++;
		}
	}

	void SubKeys(const CFSAString szExcept, const CFSVar &Data) {
		for (INTPTR ip=0; ip<Data.GetSize(); ip++) {
			CFSAString szKey=Data.GetKey(ip);
			if (szKey==szExcept) continue;
			m_Writer.Key(szKey);
			m_Writer.Val(Data[szKey]);
		}
	}

	void OnValReadEnd(const CFSAString &szKey, CFSVar &Data) {
		if (szKey.IsEmpty()) {
			SubKeys("paragraphs", Data);
			m_Writer.ObjectEnd();
		} else if (szKey=="/paragraphs") {
			m_Writer.ArrayEnd();
			m_iCollectData++;
		} else if (KeyMatch(szKey, "/paragraphs/%d")) {
			SubKeys("sentences", Data);
			m_Writer.ObjectEnd();
			m_iCollectData--;
		} else if (KeyMatch(szKey, "/paragraphs/%d/sentences")) {
			m_Writer.ArrayEnd();
			m_iCollectData++;
		} else if (KeyMatch(szKey, "/paragraphs/%d/sentences/%d")) {
			if (Data.KeyExist("words")) {

				CFSVar &Words=Data["words"];
				CFSArray<CMorphInfos> WordsAnalysis;
				for (INTPTR ip=0; ip<Words.GetSize(); ip++) {
					const CFSVar &Word=Words[ip];
					CMorphInfos Analysis;
					Analysis.m_szWord=Word["text"].GetWString();
					const CFSVar &VarAnalysis=Word["analysis"];
					for (INTPTR ip2=0; ip2<VarAnalysis.GetSize(); ip2++) {
						const CFSVar &VarAnalysis1=VarAnalysis[ip2];
						CMorphInfo Analysis1;
						Analysis1.m_szRoot=VarAnalysis1["root"].GetWString();
						Analysis1.m_szEnding=VarAnalysis1["ending"].GetWString();
						Analysis1.m_szClitic=VarAnalysis1["clitic"].GetWString();
						Analysis1.m_cPOS=VarAnalysis1["partofspeech"].GetWString()[0];
						Analysis1.m_szForm=VarAnalysis1["form"].GetWString();
						Analysis.m_MorphInfo.AddItem(Analysis1);
					}
					WordsAnalysis.AddItem(Analysis);
				}

				WordsAnalysis=m_Disambiguator.Disambiguate(WordsAnalysis);
				RT_ASSERT(Words.GetSize()==WordsAnalysis.GetSize());

				for (INTPTR ip=0; ip<Words.GetSize(); ip++) {
					const CMorphInfos &Analysis=WordsAnalysis[ip];
					CFSVar VarAnalysis;
					VarAnalysis.Cast(CFSVar::VAR_ARRAY);
					for (INTPTR ipRes=0; ipRes<Analysis.m_MorphInfo.GetSize(); ipRes++) {
						const CMorphInfo &Analysis1=Analysis.m_MorphInfo[ipRes];
						CFSVar VarAnalysis1;
						VarAnalysis1["root"]=Analysis1.m_szRoot;
						VarAnalysis1["ending"]=Analysis1.m_szEnding;
						VarAnalysis1["clitic"]=Analysis1.m_szClitic;
						VarAnalysis1["partofspeech"]=CFSWString(Analysis1.m_cPOS);
						VarAnalysis1["form"]=Analysis1.m_szForm;
						VarAnalysis[ipRes]=VarAnalysis1;
					}
					Words[ip]["analysis"]=VarAnalysis;
				}

			}
			m_Writer.Val(Data);
			m_iCollectData--;
		}
	}

protected:
	CDisambiguator &m_Disambiguator;
	CJSONWriter m_Writer;
};

int PrintUsage() {
	fprintf(stderr, "Use: etdisamb -options\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -in file    -- read input from file, default input from stdin\n");
	fprintf(stderr, " -out file   -- write output to file, default output to stdout\n");
	fprintf(stderr, " -lex file   -- path to lexicon file, default et3.dct\n");
	fprintf(stderr, " -help       -- this screen\n");
	fprintf(stderr, "\n");
	return -1;
}

int main(int argc, char* argv[])
{
	int iRes=-1;
	FSCInit();

	try {
		// Command line parsing
		CFSAString InFileName, OutFileName, LexFileName="et3.dct";
		for (int i=1; i<argc; i++) {
			if (CFSAString("-help")==argv[i]) {
				return PrintUsage();
			} else if (CFSAString("-lex")==argv[i]) {
				if (i+1<argc) {
					LexFileName=argv[++i];
				} else {
					return PrintUsage();
				}
			} else if (CFSAString("-in")==argv[i]) {
				if (i+1<argc) {
					InFileName=argv[++i];
				} else {
					return PrintUsage();
				}
			} else if (CFSAString("-out")==argv[i]) {
				if (i+1<argc) {
					OutFileName=argv[++i];
				} else {
					return PrintUsage();
				}
			} else {
				return PrintUsage();
			}
		}

		// Initialize streams and set up analyzer
		CFSFile InFile, OutFile;
		if (InFileName.IsEmpty()) {
			InFile.Attach(stdin, false);
		} else {
			InFile.Open(InFileName, "rb");
		}
		if (OutFileName.IsEmpty()) {
			OutFile.Attach(stdout, false);
		} else {
			OutFile.Open(OutFileName, "wb");
		}

		CDisambiguator Disambiguator;
		Disambiguator.Open(LexFileName);
		CJSONWriter JSONWriter(OutFile);
		CMyJSONReader JSONReader(InFile, Disambiguator, JSONWriter);

		// Run the loop
		JSONReader.Read();

		// Success
		iRes=0;
	} catch (const CJSONException &e) {
		fprintf(stderr, "JSON error: %s\n", (const char *)FSStrTtoA(e.GetText()));
	} catch (const CDisambiguatorException &e) {
		fprintf(stderr, "Disambiguator engine error: %s\n", (const char *)FSStrTtoA(e.GetText()));
	} catch (const CFSFileException &e) {
		fprintf(stderr, "I/O error: %d\n", e.m_nError);
	} catch (const CFSException &) {
		fprintf(stderr, "Internal error\n");
	} catch (...) {
		fprintf(stderr, "Unexpected error\n");
	}

	FSCTerminate();
	return iRes;
}
