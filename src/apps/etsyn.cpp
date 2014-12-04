#include "json.h"
#include "etmrf.h"

class CSettings {
public:
	CSettings() {
		m_bGuess=false;
		m_bPhon=false;
	}

	bool m_bGuess;
	bool m_bPhon;
};

class CMyJSONReader : public CJSONReader {
public:
	CMyJSONReader(CFSStream &Stream, ETMRFAS &Morf, const CSettings &Settings, CJSONWriter &Writer) : CJSONReader(Stream), m_Morf(Morf), m_Settings(Settings), m_Writer(Writer) { }

protected:
	void OnValReadStart(const CFSAString &szKey) {
		if (szKey.IsEmpty()) {
			m_Writer.ObjectStart();
			m_Writer.Key("words");
			m_Writer.ArrayStart();
			m_iCollectData--;
			m_ipWordIndex=0;
			m_szWordKey.Format("/words/%zd", m_ipWordIndex);
		} else if (szKey==m_szWordKey) {
			m_iCollectData++;
		}
	}
	void OnValReadEnd(const CFSAString &szKey, CFSVar &Data) {
		if (szKey.IsEmpty()) {
			m_Writer.ArrayEnd();
			m_Writer.ObjectEnd();
			m_iCollectData++;
		} else if (szKey==m_szWordKey) {
			const CFSVar &Word=Data;

			MRFTUL Input;
			Input.tyvi=Word["lemma"].GetWString();
			Input.sl=Word["partofspeech"].GetWString();
			if (Input.sl.IsEmpty()) Input.sl=FSWSTR("*");
			Input.vormid=Word["form"].GetWString();
			CFSWString szHint=Word["hint"].GetWString();

			m_Morf.Clr();
			MRFTULEMUSED Result;
			if (m_Morf.Synt(Result, Input, szHint) && Result.on_tulem()){
				CFSVar Text;
				Text.Cast(CFSVar::VAR_ARRAY);
				for (INTPTR ipRes=0; Result[ipRes]; ipRes++){
					Text[ipRes]=Result[ipRes]->tyvi+Result[ipRes]->lopp+Result[ipRes]->kigi;
				}
				Data["text"]=Text;
			}

			m_Writer.Val(Data);

			m_ipWordIndex++;
			m_szWordKey.Format("/words/%zd", m_ipWordIndex);
			m_iCollectData--;
		}
	}

protected:
	ETMRFAS &m_Morf;
	CSettings m_Settings;
	CJSONWriter m_Writer;

	INTPTR m_ipWordIndex;
	CFSAString m_szWordKey;
};

int PrintUsage() {
	fprintf(stderr, "Use: etsyn -options\n");
	fprintf(stderr, "\n");
	fprintf(stderr, "Options:\n");
	fprintf(stderr, " -in file  -- read input from file, default input from stdin\n");
	fprintf(stderr, " -out file -- write output to file, default output stdout\n");
	fprintf(stderr, " -lex path -- path to lexicon files, default active directory\n");
	fprintf(stderr, " -guess    -- guess forms for unknown words\n");
	fprintf(stderr, " -phonetic -- add phonetic markup\n");
	fprintf(stderr, "\n");
	return -1;
}

int main(int argc, char* argv[])
{
	int iRes=-1;
	FSCInit();

	try {
		// Command line parsing
		if (argc<=1) {
			return PrintUsage();
		}

		CSettings Settings;
		CFSAString InFileName, OutFileName, LexPath=".";
		for (int i=1; i<argc; i++) {
			if (CFSAString("-lex")==argv[i]) {
				if (i+1<argc) {
					LexPath=argv[++i];
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
				Settings.m_bPhon=true;
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

		MRF_FLAGS_BASE_TYPE Flags=MF_DFLT_MORFA;
		if (Settings.m_bGuess) Flags|=MF_OLETA;
		if (Settings.m_bPhon) Flags|=MF_KR6NKSA;

		ETMRFAS Morf;
		Morf.Start(LexPath, Flags);
		CJSONWriter JSONWriter(OutFile);
		CMyJSONReader JSONReader(InFile, Morf, Settings, JSONWriter);

		// Run the loop
		JSONReader.Read();

		// Success
		iRes=0;
	} catch (const CJSONException &e) {
		fprintf(stderr, "JSON error: %s\n", (const char *)FSStrTtoA(e.GetText()));
	} catch (const VEAD &e) {
		fprintf(stderr, "Morph engine error: "); e.Print();
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
