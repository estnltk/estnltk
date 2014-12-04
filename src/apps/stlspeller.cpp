#include "speller.h"
#include <iostream>

const wchar_t *words[] = { L"esimene", L"vikane", L"teine", L"vannaema", 0 };

#if defined (UNICODE)
int wmain(int argc, wchar_t* argv[])
#else
int main(int argc, char* argv[])
#endif
{
	FSUNUSED(argc);
	FSUNUSED(argv);

	try {
		openmorf::speller spl(FSTSTR("et.dct"));

		for (size_t i = 0; words[i]; i++) {
			std::wcout << words[i] << L" -- ";
			if (spl.spell(words[i])) {
				std::wcout << L"OK\n";
			} else {
				std::wcout << L"Vigane, soovitan:";
				std::vector<std::wstring> suggs = spl.suggest(words[i]);
				for (size_t j = 0; j < suggs.size(); j++) {
					std::wcout << L" " << suggs[j];
				}
				std::wcout << L"\n";
			}
		}

	} catch (const openmorf::exception &) {
		std::wcerr << L"Viga!\n";
	}
	return 0;
}
