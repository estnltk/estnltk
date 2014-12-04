
#include "mrf-mrf.h"

void MORF0::arvamin(
    const FSXSTRING *sisse, // sisends6na
    MRFTULEMUSED *tul)    
    {
    if (!mrfFlags.Chk(MF_OLETA))  // ei tulegi oletada
        return;
	int res;

    FSXSTRING sona= *sisse;    
    TaheHulgad::AsendaMitu(&sona, TaheHulgad::uni_kriipsud, TaheHulgad::amor_kriipsud);

    tul->tagasiTasand=0;
	tul->mitmeS6naline = 1;    // s.t. oletame 1 s�na, mitte v�ljendeid
    tul->keeraYmber = false;
    tul->eKustTulemused=eMRF_AO; // anal��sid oletajast
    tul->DelAll();

    if (sisse->GetLength() >= STEMLEN) // tegelt seda juba chkmin() kontrollis
	    {
        tul->Add((const FSxCHAR *)*sisse, FSxSTR(""), FSxSTR(""), FSxSTR("Z"), FSxSTR("")); // parema puudusel
        return;
	    }
	res = arvax( tul, &sona );
	if (res != ALL_RIGHT)
        {
        tul->eKustTulemused=eMRF_XX;
        tul->s6na = FSxSTR("");
        throw(VEAD(ERR_MG_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__, "$Revision: 542 $")); //jama!
        }
    }

