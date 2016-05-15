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
#include "../../lib/json.h"
#include "../../../lib/proof/proof.h"

class CSettings {
public:
	CSettings() {
		m_bAnalyzeGuess=false;
		m_bAnalyzePhonetic=false;
		m_bAnalyzeProperName=false;
		m_bSpellSuggest=false;
	}

	CFSAString m_szCommand;

	bool m_bAnalyzeGuess;
	bool m_bAnalyzePhonetic;
	bool m_bAnalyzeProperName;

	bool m_bSpellSuggest;
};

class CMyJSONReader : public CJSONReader {
public:
	CMyJSONReader(CFSStream &Stream, CLinguistic &Linguistic, const CSettings &Settings, CJSONWriter &Writer) : CJSONReader(Stream), m_Linguistic(Linguistic), m_Settings(Settings), m_Writer(Writer) { }

protected:
	void OnValReadStart(const CFSAString &szKey) {
		//printf("OnObjectReadStart(%s)\n", (const char *)szKey);
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
		//printf("OnObjectReadEnd(%s, ...)\n", (const char *)szKey);
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

				if (m_Settings.m_szCommand=="spell") {

					for (INTPTR ip=0; ip<Words.GetSize(); ip++) {
						CFSVar &Word=Words[ip];
						CPTWord PTWord=Word["text"].GetWString();
						PTWord.RemoveHyphens();
						PTWord.RemovePunctuation();
						PTWord.Trim();
						if (PTWord.m_szWord.IsEmpty() || m_Linguistic.SpellWord(PTWord.m_szWord)==SPL_NOERROR) {
							Word["spelling"]=true;
						} else {
							Word["spelling"]=false;
							if (m_Settings.m_bSpellSuggest) {
								CFSWStringArray Suggestions=m_Linguistic.Suggest(PTWord.m_szWord);
								CFSVar VarSuggestions;
								VarSuggestions.Cast(CFSVar::VAR_ARRAY);
								for (INTPTR ipRes=0; ipRes<Suggestions.GetSize(); ipRes++) {
									VarSuggestions[ipRes]=Suggestions[ipRes];
								}
								Word["suggestions"]=VarSuggestions;
							}
						}
					}

				} else if (m_Settings.m_szCommand=="analyze") {

					CFSArray<CPTWord> PTWords;
					for (INTPTR ip=0; ip<Words.GetSize(); ip++) {
						PTWords.AddItem(Words[ip]["text"].GetWString());
					}
					CFSArray<CMorphInfos> MorphResults=m_Linguistic.AnalyzeSentence(PTWords);
					ASSERT(PTWords.GetSize()==MorphResults.GetSize());
					for (INTPTR ip=0; ip<Words.GetSize(); ip++) {
						const CFSArray<CMorphInfo> &Analysis=MorphResults[ip].m_MorphInfo;
						CFSVar VarAnalysis;
						VarAnalysis.Cast(CFSVar::VAR_ARRAY);
						for (INTPTR ipRes=0; ipRes<Analysis.GetSize(); ipRes++) {
							const CMorphInfo &Analysis1=Analysis[ipRes];
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
			}
			m_Writer.Val(Data);
			m_iCollectData--;
		}
	}

protected:
	CLinguistic &m_Linguistic;
	CSettings m_Settings;
	CJSONWriter m_Writer;
};

int PrintUsage() {
	fprintf(stderr, "Use: etana command -options\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Commands:\n");
	fprintf(stderr, " analyze     -- morphological analysis\n");
	fprintf(stderr, " spell       -- check spelling\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -in file    -- read input from file, default input from stdin\n");
	fprintf(stderr, " -out file   -- write output to file, default output to stdout\n");
	fprintf(stderr, " -lex file   -- path to lexicon file, default et.dct\n");
	fprintf(stderr, " -guess      -- guess forms for unknown words (analyze only)\n");
	fprintf(stderr, " -phonetic   -- add phonetic markup (analyze only)\n");
	fprintf(stderr, " -propername -- additional proper name analysis (analyze only)\n");
	fprintf(stderr, " -suggest    -- suggest correct forms (spell only)\n");
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
		if (argc<=2) {
			return PrintUsage();
		}

		CSettings Settings;
		Settings.m_szCommand=argv[1];
		if (Settings.m_szCommand!="analyze" && Settings.m_szCommand!="spell") {
			return PrintUsage();
		}

		CFSAString InFileName, OutFileName, LexFileName="et.dct";
		for (int i=2; i<argc; i++) {
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
			} else if (CFSAString("-guess")==argv[i]) {
				Settings.m_bAnalyzeGuess=true;
			} else if (CFSAString("-phonetic")==argv[i]) {
				Settings.m_bAnalyzePhonetic=true;
			} else if (CFSAString("-propername")==argv[i]) {
				Settings.m_bAnalyzeProperName=true;
			} else if (CFSAString("-suggest")==argv[i]) {
				Settings.m_bSpellSuggest=true;
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

		CLinguistic Linguistic;
		Linguistic.Open(LexFileName);
		if (Settings.m_szCommand=="analyze") {
			Linguistic.m_bProperName=Settings.m_bAnalyzeProperName;
			Linguistic.m_bGuess=(Settings.m_bAnalyzeGuess || Linguistic.m_bProperName);
			if (Linguistic.m_bGuess) Linguistic.m_bAbbrevations=false;
			Linguistic.m_bPhonetic=Settings.m_bAnalyzePhonetic;
		}
		CJSONWriter JSONWriter(OutFile);
		CMyJSONReader JSONReader(InFile, Linguistic, Settings, JSONWriter);

		// Run the loop
		JSONReader.Read();

		// Success
		iRes=0;
	} catch (const CJSONException &e) {
		fprintf(stderr, "JSON error: %s\n", (const char *)FSStrTtoA(e.GetText()));
	} catch (const CLinguisticException &e) {
+		fprintf(stderr, "Linguistic engine error: %s\n", (const char *)FSStrTtoA(e.GetText()));
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
