
#include "cxxbs3.h"

void DCTRD::Close(void)
	{
	CacheClose();       // vabastab m�lu k�shi alt
    VabastaViidad();    // vabasta �lej��nud m�lu
    dctFile.Close();
	}
