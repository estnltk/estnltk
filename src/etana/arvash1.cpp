
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
