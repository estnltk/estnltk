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
/*
* proovib sh ja zh asendada ja siis uuesti anal��sida;
*
*/
#include "mrf-mrf.h"

int MORF0::arvash1(MRFTULEMUSED *tulemus, FSXSTRING *S6na)
    {
    int res;
    int tagasitasand;
    FSXSTRING S6na3;

    S6na3 = *S6na;
    TaheHulgad::ShZh2Susisev(&S6na3);
    if (S6na3 == *S6na)    // polnud valel kujul susisevaid 
        return ALL_RIGHT;
	res = chkx( tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand );
	if (res != ALL_RIGHT)
	    return res;
    if (tulemus->on_tulem())
        {
        // paneme sh tagasi 
        tulemus->Susisev2ShZh();
	    }
    return ALL_RIGHT;
    }
