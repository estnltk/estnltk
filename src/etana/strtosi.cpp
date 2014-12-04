
// String m�rgiga t�isarvuks.

#include "mrflags.h"
#include "tloendid.h"

int Xstr_2_int // ==0:pole numbrit; >0: niimitmest baidist tehti m�rgiga t�isarv;
	(
	int           *i,	// saadud m�rgiga t�isarv
	const FSxCHAR *xstr // l�htestring
	)
	{
	int n=0, x;
    bool miinus;

    if(*xstr == (FSxSTR("-"))[0])
        {
        miinus = true;
        n++;
        }
    else
        {
        miinus = false;
        if(*xstr == (FSxSTR("+"))[0])
            {
            n++;
            }
        }
    if(TaheHulgad::number.Find(xstr[n]) == -1)
        {
        return 0;   // pole number
        }
    for(x=0; xstr[n] && TaheHulgad::number.Find(xstr[n]) >= 0; n++)
		{
		x = 10 * x + (xstr[n]-(FSxSTR("0"))[0]);
		}
    *i = miinus ? -x : x;

    return n;       // n baiti teisendasime t�isarvuks
	}
