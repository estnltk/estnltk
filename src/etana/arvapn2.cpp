
/*
* proovib arvata pa'risnime
* millel lopp apostroofiga 
*/

#include "mrf-mrf.h"

int MORF0::arvapn2(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    int i;
    int maha;
    FSXSTRING tyvi;
    FSXSTRING lopp;
    FSXSTRING sl;
    FSXSTRING vormid;
    const FSxC5I1 *lopu_info;

    i = S6na->ReverseFind(APOSTROOF);
    if (i == -1)
        return ALL_RIGHT;
    if (S6naPikkus - i > PN_ENDLEN)  // O'Connorist
        return ALL_RIGHT;
    if (i < S6naPikkus-1 && TaheHulgad::OnAeiu((*S6na)[i+1]))
        maha=1; // Paige'iks tyvi=Paige lopp=ks
    else
        maha=0;
    if (mrfFlags.Chk(MF_ALGV))
        tyvi = S6na->Left(i);
    else
        tyvi = S6na->Left(i+1);
    lopp = S6na->Mid(i+1+maha);
    if (TaheHulgad::SuurAlgustaht(S6na))
        sl = LIIK_PARISNIMI;
    else
        sl = LIIK_YLDNIMI;
//    if (lopp == FSxSTR("d"))        // d-loppu vt eraldi
//        vormid = FSxSTR("pl n, sg p, ");
    if (lopp.GetLength() == 0)   // 0-loppu vt eraldi
        {
        if (maha == 0 && sl == LIIK_YLDNIMI) // nt fuckin', tolgend'
            return ALL_RIGHT;
        lopp = FSxSTR("0");
        tulemus->Add(tyvi, lopp, FSxSTR(""), sl, FSxSTR("sg g, "));
        if (maha)
            tulemus->Add(tyvi, lopp, FSxSTR(""), sl, FSxSTR("sg p, "));
        }
    else   // muud lopud
        {
        for (lopu_info = oletajaDct.pn_lopud_jm.Get((const FSxCHAR *)lopp); lopu_info; 
                                             lopu_info = oletajaDct.pn_lopud_jm.GetNext())
            {
            if (lopu_info->tyyp == 1) // sobib p�risnimele
                tulemus->Add(tyvi, lopp, FSxSTR(""), sl, lopu_info->vorm);
            }
        }
    return ALL_RIGHT;
    }

