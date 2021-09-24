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

class CSettings {
public:
	CSettings() {
		m_bGuess=false;
		m_bPhonetic=false;
	}

	bool m_bGuess;
	bool m_bPhonetic;
};

class CMyJSONReader : public CJSONReader {
public:
	CMyJSONReader(CFSStream &Stream, CLinguistic &Linguistic, const CSettings &Settings, CJSONWriter &Writer) : CJSONReader(Stream), m_Linguistic(Linguistic), m_Settings(Settings), m_Writer(Writer) { }

protected:
	void OnValReadStart(const CFSAString &szKey) {
		if (szKey.IsEmpty()) {
			m_Writer.ObjectStart();
		} else if (szKey=="/words") {
			m_Writer.Key("words");
			m_Writer.ArrayStart();
			m_iCollectData--;
		} else if (KeyMatch(szKey, "/words/%d")) {
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
			SubKeys("words", Data);
			m_Writer.ObjectEnd();
		} else if (szKey=="/words") {
			m_Writer.ArrayEnd();
			m_iCollectData++;
		} else if (KeyMatch(szKey, "/words/%d")) {

			const CFSVar &Word=Data;

			CMorphInfo Input;
			Input.m_szRoot=Word["lemma"].GetWString();
			Input.m_cPOS=Word["partofspeech"].GetWString()[0];
			if (!Input.m_cPOS) Input.m_cPOS='*';
			Input.m_szForm=Word["form"].GetWString();
			CFSWString szHint=Word["hint"].GetWString();

			CFSArray<CMorphInfo> Result=m_Linguistic.Synthesize(Input, szHint);
			if (Result.GetSize()){
				CFSVar Text;
				Text.Cast(CFSVar::VAR_ARRAY);
				for (INTPTR ipRes=0; ipRes<Result.GetSize(); ipRes++){
					Text[ipRes]=Result[ipRes].m_szRoot+Result[ipRes].m_szEnding+Result[ipRes].m_szClitic;
				}
				Data["text"]=Text;
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
	fprintf(stderr, "Use: etsyn -options\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -in file  -- read input from file, default input from stdin\n");
	fprintf(stderr, " -out file -- write output to file, default output to stdout\n");
	fprintf(stderr, " -lex file -- path to lexicon file, default et.dct\n");
	fprintf(stderr, " -guess    -- guess forms for unknown words\n");
	fprintf(stderr, " -phonetic -- add phonetic markup\n");
	fprintf(stderr, " -help     -- this screen\n");
	fprintf(stderr, "\n");
	return -1;
}

int main(int argc, char* argv[])
{
	int iRes=-1;
	FSCInit();

	try {
		// Command line parsing
		CSettings Settings;
		CFSAString InFileName, OutFileName, LexFileName="et.dct";
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
			} else if (CFSAString("-guess")==argv[i]) {
				Settings.m_bGuess=true;
			} else if (CFSAString("-phonetic")==argv[i]) {
				Settings.m_bPhonetic=true;
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
		Linguistic.m_bGuess=Settings.m_bGuess;
		Linguistic.m_bPhonetic=Settings.m_bPhonetic;

		CJSONWriter JSONWriter(OutFile);
		CMyJSONReader JSONReader(InFile, Linguistic, Settings, JSONWriter);

		// Run the loop
		JSONReader.Read();

		// Success
		iRes=0;
	} catch (const CJSONException &e) {
		fprintf(stderr, "JSON error: %s\n", (const char *)FSStrTtoA(e.GetText()));
	} catch (const CLinguisticException &e) {
		fprintf(stderr, "Linguistic engine error: %s\n", (const char *)FSStrTtoA(e.GetText()));
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
