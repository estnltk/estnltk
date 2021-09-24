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

#define STRICT
#include <memory.h>
#include <string.h>
#include <stdlib.h>

#include "tmk2t.h"
#include "cxxbs3.h"
// konstrueerib lopp-ile ja vorm-ile vastava vormitüve
// kasutab seejuures sõnastikust pärinevat infot 
bool DCTRD::OtsiTyvi(    // NULL==�heski l�pugrupis polnud vajalikke vorme
	const AVTIDX *idx,
    const int lopp,
    const int vorm,
    FSXSTRING *tyvi)
    {
    int j, n;
    MKTc *rec;
    rec=tyveMuutused[idx->tab_idx];
    if(rec==NULL)
        {
        return false;
        }
    if((j=tyvi->GetLength()-rec->mkt1c[idx->blk_idx].tyMuut.GetLength())<0)
        {
        return false; // jama 
        }
    for(n=0; n < rec->n; n++)
        {
        if(LopugruppSisaldabVormi(rec->mkt1c[n].lgNr, lopp, vorm)==0)
            {
            (*tyvi)[j]=0;
            *tyvi += rec->mkt1c[n].tyMuut;
            return true; // korda l�ks
            }
        }
    return false;  // polnud vajalike vormidega l�pugruppi    
    }

bool SamadTYVE_INF(const TYVE_INF& tyveInf1, const TYVE_INF& tyveInf2)
{
    if( tyveInf1.piiriKr6nksud==tyveInf2.piiriKr6nksud &&
            tyveInf1.lg_nr==tyveInf2.lg_nr &&
            tyveInf1.lisaKr6nksud==tyveInf2.lisaKr6nksud &&
            tyveInf1.idx.blk_idx==tyveInf2.idx.blk_idx &&
            tyveInf1.idx.tab_idx==tyveInf2.idx.tab_idx)
        return true;
    return false;
}
