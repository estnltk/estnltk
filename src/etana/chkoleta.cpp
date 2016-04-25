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

