
// Pole enam kasutusel???
/*
* kontr, kas S6na on tyvi1+vahesuf+tyvi2+[suf]+lp
* kontrollin ainult juhtumeid mis, mise, sus, suse, ja
* kontr samas ka, kas on tyvi1+lp+tyvi2+[suf]+lp
*/

#include "mrf-mrf.h"

int MORF0::lp_variant(KOMPONENT *tyvi1, KOMPONENT *tyvi, FSXSTRING *S6na, int pik, VARIANTIDE_AHEL **vahe_variant)
    {
    VARIANTIDE_AHEL *tmp; //ok
    KOMPONENT *tmptyvi=0, *vahesuf, *algus;
    int lnr=0;
    FSXSTRING vt_tyvi;
    char sobivad[SONAL_MAX_PIK];
    int tyyp=0;

    if (tyvi->k_pikkus < pik + 2) //* sellisele tyvi1+lp-le tyvi2 taha ei mahu 
        return ALL_RIGHT;

    vt_tyvi = (const FSxCHAR *)(tyvi->k_algus.Left(pik));
    switch (tyvi1->liitumistyyp)
        {
        case 14: //* A sg g, mille l�pus se v�i iku 
            {
            if (vt_tyvi == FSxSTR("ma"))
                tyyp = 14;
            else if (vt_tyvi == FSxSTR("ks"))
                { //* muid l�ppe ei lubagi 
                lnr = lpnr((const FSxCHAR *)vt_tyvi);
                tyyp = L_TYVE_TYYP + 6;  //* nagu S obliikva 
                }
            break;
            }
        case 15: //* A sg g, mille l�pus pole se ega iku 
            if (vt_tyvi == FSxSTR("ma"))
                {
                tyyp = 14;
                break;
                }
        case 17: //* B sg g 
            // 17 ja 19 k�ituvad identselt, seega ongi m�eldud 17st 19sse l�bikukkuma
        case 19: //* C sg g 
            {
            if (vt_tyvi == FSxSTR("lt") || vt_tyvi == FSxSTR("ks") || vt_tyvi == FSxSTR("le"))
                { //* muid l�ppe ei lubagi 
                lnr = lpnr((const FSxCHAR *)vt_tyvi);
                tyyp = L_TYVE_TYYP + 6;  //* nagu S obliikva 
                }
            break;
            }
        case 22: //* A(ne) 
            {
            if (vt_tyvi == FSxSTR("sus"))
                tyyp = 2; //* S sg n; NB! vrd ty1tyyp[] failis kjuhtum.cpp 
            else if (vt_tyvi == FSxSTR("suse"))
                tyyp = 4; //* S sg g NB! vrd ty1tyyp[] failis kjuhtum.cpp 
            break;
            }
        case L_TYVE_TYYP: //* S, P tyvi 
            {
            if (vt_tyvi == FSxSTR("kese") &&
	            ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1, 
                null_lopp, FSxSTR("S"), sg_g, sobivad, sizeof(sobivad) ))
                    tyyp = 7;
            else
                {
	            lnr = lpnr( (const FSxCHAR *)vt_tyvi );
	            if ((signed char)lnr == -1)    //* sellist l�ppu pole olemas
                    return ALL_RIGHT;
	            if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("S"), pl_g, sobivad, sizeof(sobivad) ))
                    tyyp = L_TYVE_TYYP + 3;
                else if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("S"), sg_p, sobivad, sizeof(sobivad) ))
                    tyyp = L_TYVE_TYYP + 4;
                else if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("S"), pl_p, sobivad, sizeof(sobivad) ))
                    tyyp = L_TYVE_TYYP + 4;
                else if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("S"), adt, sobivad, sizeof(sobivad) ))
                    tyyp = L_TYVE_TYYP + 5;
                else if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("S"), SUVA_VRM, sobivad, sizeof(sobivad) ))
                    tyyp = L_TYVE_TYYP + 6;
                else if (ssobivus( &(tyvi1->tylgr), (const FSxCHAR *)(tyvi1->sl), 1,
                    lnr, FSxSTR("P"), pl_g, sobivad, sizeof(sobivad) ) &&
                                tyvi1->k_algus == FSxSTR("nen")) // nen+de
                    tyyp = L_TYVE_TYYP + 3;
                else
                    tyyp = L_TYVE_TYYP; //* st ei sobi liitsonasse
                }
            break;
            }
        case L_TYVE_TYYP+1: //* verbi tyvi, millele sobiks ma 
            {
            if (vt_tyvi == FSxSTR("mis"))
                tyyp = 26; //* lyhenenud tyvi; tyve lopus s; 
            else if (vt_tyvi == FSxSTR("mise"))
                tyyp = 7; //* S sg g  
            else if (vt_tyvi == FSxSTR("ja"))
                tyyp = 3; //* S sg g;  
            else if (vt_tyvi == FSxSTR("jate")) // tegelikult =ja+te; see tuleb parandada variandid_tulemuseks() sees
                {
                lnr = lopp_te;
                tyyp = L_TYVE_TYYP + 3; //* S pl g;  
                }
            else if (vt_tyvi == FSxSTR("ma"))
                {
                lnr = lopp_ma;
                tyyp = L_TYVE_TYYP + 7;
                }
            else if (vt_tyvi == FSxSTR("mata"))
                {
                lnr = lopp_mata;
                tyyp = L_TYVE_TYYP + 7;  //* liitub nagu V+ma 
                }
            break;
            }
        case L_TYVE_TYYP+2: //* verbi tyvi, millele sobiks da, ta v�i a 
            {
			if (vt_tyvi == FSxSTR("da") || vt_tyvi == FSxSTR("ta") || vt_tyvi == FSxSTR("a"))
				{
				lnr = lpnr( (const FSxCHAR *)vt_tyvi );
				tyyp = L_TYVE_TYYP + 8;
				}
            break;
            }
        default:
            return ALL_RIGHT;
        }
	if (tyyp == 0)
		return ALL_RIGHT;
    tmp = lisa_1ahel(vahe_variant);
    tmptyvi = lisa_esimene(tmp);
    if (!tmptyvi)
        return CRASH;
    for (algus=tyvi1; algus->komp_eelmine; algus=algus->komp_eelmine);
    kopeeri_komp(tmptyvi, algus);
    for ( ; algus != tyvi1; algus=algus->komp_jargmine)
        {
        tmptyvi = lisa_1komp(&tmptyvi);
        if (!tmptyvi)
            return CRASH;
        kopeeri_komp(tmptyvi, algus);
        }
    vahesuf = lisa_1komp(&tmptyvi);
    if (!vahesuf)
        return CRASH;
    lisa_min_info(vahesuf, S6na, tyvi->nihe, pik);
    if (tyyp < L_TYVE_TYYP) //* oli vahesuf 
        lisa_psl_info(vahesuf, K_SUFF, suffnr( (const FSxCHAR *)(vahesuf->k_algus) ));
    else
        lisa_psl_info(vahesuf, K_LOPP, lnr);
    vahesuf->liitumistyyp = tyyp;
	vahesuf->sonastikust = 0;   // HJK 3.06.2004
    return ALL_RIGHT;
    }

int MORF0::edasiseks(VARIANTIDE_AHEL *variant, VARIANTIDE_AHEL **mille_taha, VARIANTIDE_AHEL **vahe_variant, VARIANTIDE_AHEL **uus_variant)
    {
    KOMPONENT *tmp1, *tmp2, *t1;
    
    *uus_variant = lisa_ahel(mille_taha, *vahe_variant);
    if (!(*uus_variant))
        return CRASH;
    mille_taha = uus_variant;
    tmp1 = esimene_komp(*uus_variant);
    tmp2 = esimene_komp(variant);
    for (; tmp1->komp_jargmine; tmp1 = tmp1->komp_jargmine)
        tmp2 = tmp2->komp_jargmine;
    //* kopeeri_komponendid(*uus_variant, tmp2);
    t1 = kop_kompid(&tmp1, tmp2);
    if (!t1)
        return CRASH;
    lisa_min_info(tmp1->komp_jargmine, &(tmp1->algsona), 
        tmp1->nihe + tmp1->k_pikkus, tmp2->k_pikkus - tmp1->k_pikkus);
    return ALL_RIGHT;
    }

int MORF0::kchk5(
    VARIANTIDE_AHEL **variandid, 
    FSXSTRING *S6na, int S6naPikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    int res;
    int  pik;
    VARIANTIDE_AHEL *mille_taha, *vt_piir, *uus_variant=0;
    CVARIANTIDE_AHEL cvahe_variant;
    KOMPONENT *tyvi1, *tyvi;

    mille_taha = viimane_prefita_variant(*variandid);  //* kuhu uus komponentide ahel paigutada
    vt_piir = mille_taha;     //* ... ja millest tagapool olevaid ahelaid ei selles programmis ei vt
    
    //* vt tyve1-sid
    for (VARIANTIDE_AHEL *variant=*variandid; variant; variant=variant->jargmine_variant)
	    {
        if (variant->eelmine_variant == vt_piir) //* jo'udsime selles programmis lisatud variandini
            break;
        tyvi1 = esimene_komp(variant);
        if (tyvi1->k_tyyp != K_TYVI) 
            continue;
        tyvi = tyvi1->komp_jargmine;
        if (!(tyvi->komp_jargmine))
            continue;
        //* keerulisemat struktuuri ei vt; ka mitut erin sufiksit ei luba, v.a. lt puhul; ??? 
        if (*sobivad_variandid &&  
                tyvi->komp_jargmine->k_tyyp == K_SUFF)
            {
            FSXSTRING sona;
            sona = (const FSxCHAR *)(S6na->Left(S6naPikkus));
            if (!TaheHulgad::OnLopus(&(sona), FSxSTR("lt")))
                break;
            }

        for (pik=1; pik < 6; pik++) //* vt k�iki vahesuf ja l�ppe
            {
            //* vahe_variandiks teeme tyvi1+vsuf v�i tyvi1+lp
            res = lp_variant(tyvi1, tyvi, S6na, pik, &cvahe_variant.ptr);
	        if (res > ALL_RIGHT)
	            return res; //* viga! 
            if (!cvahe_variant.ptr)
                continue;

            //* leiame tyvi2 
            res = liitsona(&cvahe_variant.ptr, tyvi, S6na, pik, sobivad_variandid, paha_koht,paha_koha_suurus);
	        if (res > ALL_RIGHT)
	            return res; //* viga! 

            if (!*sobivad_variandid) //* lisan vsuf-ga variandid ahelatesse edasiseks vaatamiseks 
                {
                res = edasiseks(variant, &mille_taha, &cvahe_variant.ptr, &uus_variant);
	            if (res > ALL_RIGHT)
	                return res; //* viga! 
                mille_taha = uus_variant;
                ahelad_vabaks(&cvahe_variant.ptr);
                }
            else
                break;
            }
        ahelad_vabaks(&cvahe_variant.ptr);
        }
    return ALL_RIGHT;
    }



