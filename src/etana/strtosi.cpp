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
