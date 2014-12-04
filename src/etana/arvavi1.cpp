
/*
* kontrollib, kas S6nas on keskel kirjavahem�rk v�i suurta'ht, millega
* algab tavaline sona (vo'ib olla tyhik ununenud)
* n�iteks:
* SANDREVenemaa, ProSpordist, ServiceKusagil
*
* K.a, tsaari-Venemaa ei sobi 
*
* proovib ka asendada 3 �hesug t�hte kahega ja siis anal��sida
*/
#include "mrf-mrf.h"

int MORF0::arvavi1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus)
    {
    int i;
    //int k=0, k1=0, k2=0;
    int res = ALL_RIGHT;
    int tagasitasand;
    FSXSTRING S6na3;

    S6na3 = *S6na;
    for (i=S6na3.GetLength()-3; i > 1; i--) // otsin viimast kirjavahem�rki s�na seest
        {
        if ((TaheHulgad::punktuatsioon.Find(S6na3[i]) != -1 &&
            TaheHulgad::kaldjakriips.Find(S6na3[i]) == -1) ||
            S6na3[i] == (FSxCHAR)'.')
            {
            if (S6na3.Mid(i+1) != FSxSTR("ee") && S6na3.Mid(i+1) != FSxSTR("EE"))
                S6na3 = S6na3.Mid(i+1);
            break;
            }
        }
     for (i=S6na3.GetLength()-3; i > 0; i--) // otsin suurt algust�hte s�na seest
        {
        if (TaheHulgad::suurtht.Find(S6na3[i]) != -1 &&
            TaheHulgad::suurnrthtkriips.Find(S6na3[i-1]) == -1 && // pole akron��m + lp
            TaheHulgad::suurnrthtkriips.Find(S6na3[i+1]) == -1 && // pole ARK-100
            TaheHulgad::kaldjakriips.Find(S6na3[i-1]) == -1) // pole tsaari-Venemaa
            {
            S6na3 = S6na3.Mid(i);
            break;
            }
        }
    if (S6na3 == *S6na && S6naPikkus > 3) // polnud vigasid; liiga l�hikesi ei vt
        {
        for (i=S6na3.GetLength()-3; i >= 0; i--) // otsin s�na seest 3 �hesug t�hte
            {
            if (S6na3[i] == S6na3[i+1] && S6na3[i] == S6na3[i+2])
                {
                S6na3.Delete(i, 1);
	            res = chkx( tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand );
	            return res;
                }
            }
        }
    if (S6na3 == *S6na ) // polnud vigasid
        {        // �kki on nt 21miljoni
        for (i=0; i < S6naPikkus; i++)
            {
            if (TaheHulgad::number.Find((*S6na)[i]) == -1)
                break; 
            }
        S6na3 = S6na3.Mid(i);
        }
    if (S6na3 != *S6na)
        {
        res = chkwrd(tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand, KOIK_LIIGID);
	    if (res != ALL_RIGHT)
	        return res;
        if (!tulemus->on_tulem() && TaheHulgad::OnSuur(&S6na3, 0) 
            && !TaheHulgad::AintSuuredjaNrjaKriipsud(&S6na3))
            {
            S6na3.MakeLower();
            res = chkwrd(tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand, KOIK_LIIGID);
            }
        }
//    res = chkx( tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand );
	if (res != ALL_RIGHT)
	    return res;
    if (tulemus->on_tulem())
        {
        FSXSTRING ette;

        i = S6na3.GetLength();
        ette = S6na->Left(S6naPikkus - i);
        ette += FSxSTR("_");
        tulemus->LisaTyvedeleEtte((const FSxCHAR *)ette);
        return ALL_RIGHT;
        }
    // v�ib olla olid suured-v�iksed t�hed segamini?
    S6na3 = *S6na;
    S6na3.MakeLower();
    S6na3[0] = (*S6na)[0];
	res = chkx( tulemus, &S6na3, S6na3.GetLength(), 100, &tagasitasand );
    return res;
    }
