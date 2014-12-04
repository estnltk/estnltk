
/*
* kontr, kas S6na on tyvi1+tyvi2+lp
*/

#include "mrf-mrf.h"

int MORF0::kchk4(
    VARIANTIDE_AHEL **variandid, 
    FSXSTRING *S6na, int S6naPikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_suurus)
    {
    int res;
    int  sty, cnt;
    int  pik;
    VARIANTIDE_AHEL *mille_taha, *tmp, *vt_piir, *uus_variant; //ok
    CVARIANTIDE_AHEL cvahe_variant;
    KOMPONENT *tyvi, *tyvi1, *esimene, *uustyvi;
    FSXSTRING vt_tyvi;
    KOMPONENT komp, *essa;
    int vaja_jatkata = 0;
    TYVE_INF tmp_dptr[SONAL_MAX_PIK];

    mille_taha = viimane_prefita_variant(*variandid);  /* kuhu uus komponentide ahel paigutada */
    vt_piir = mille_taha;     /* ... ja millest tagapool olevaid ahelaid ei selles programmis ei vt */
    
    tyvi1 = &komp;
    pik = minipik(S6na);
    sty = S6naPikkus-1;
    /* otsi tyve1 */
    for (; pik < sty; pik++)         
	    {
//{
//printf("DB:%s:%d\n", __FILE__,__LINE__);
//MRFTULEMUSED dbTul;
//variandid_tulemuseks(&dbTul, KOIK_LIIGID, sobivad_variandid);
//}

	    if (sobiks_ne(S6na, pik)) /* eelistan lyhenenud varianti, nt lokaal- */
		    {
            vt_tyvi = (const FSxCHAR *)(S6na->Left(pik));
            vt_tyvi += FSxSTR("ne");
            res = cXXfirst(vt_tyvi, pik+2, &cnt);
            if (res > ALL_RIGHT)  /* viga! */
	            return res;
		    if (res == POLE_YLDSE || res == POLE_SEDA)  /* -ne lisamine oli lollus */
	            res = hjk_cXXfirst(S6na, 0, pik, &cnt, paha_koht,paha_koha_suurus);
		    }
        else
	        res = hjk_cXXfirst(S6na, 0, pik, &cnt, 
                    paha_koht, paha_koha_suurus); /* m�rgi ka pahad tyve-otsimise kohad */
        if (res > ALL_RIGHT)  /* viga! */
	        return res;
	    if (res == POLE_YLDSE) /* sellise algusega tyve pole yldse */
	        break;
        if (res == POLE_SEDA)  /* sellist tyve pole olemas */
	        continue;

	    /* mingi tyvi1 leitud */
        nulli_1komp(tyvi1);
        lisa_min_info(tyvi1, S6na, 0, pik);
        lisa_psl_info(tyvi1, K_TYVI, 0);
        /* leiame tyvi1 liitumis-liigid */
        LgCopy(tmp_dptr, dptr, cnt);
        res = juht1(tyvi1, tmp_dptr, cnt, &cvahe_variant.ptr);
	    if (res > ALL_RIGHT)
	        return res; /* viga! */
        if (!cvahe_variant.ptr)  
            continue;  /* liitsonasse sobivat tyvi1 polnud */

        /* tore oleks ka sufiksite algusi arvestada, et sealt ei peaks tyve2-sid otsima... */
        for (VARIANTIDE_AHEL *variant=*variandid; variant; variant=variant->jargmine_variant)
	        {
            if (variant->eelmine_variant == vt_piir) /* jo'udsime selles programmis lisatud variandini */
                break;
            tyvi = esimene_komp(variant);
            if (tyvi->k_tyyp == K_PREF) 
                continue;
            if (tyvi->k_pikkus < pik + 2) /* sellisele tyvi1-le tyvi2 taha ei mahu */
                {
                //if (tyvi->k_algus[tyvi->k_pikkus-1] != (FSxCHAR)'\x00F6') // � tantsu_�+id
                if (!((tyvi->k_pikkus == pik + 1) && tyvi->k_algus[tyvi->k_pikkus-1] == (FSxCHAR)0xF6)) // � tantsu_�+id
                    continue;
                }
            /* keerulisemat struktuuri ei vt; ka mitut erin sufiksit ei luba, v.a. lt puhul; ??? */
            if (*sobivad_variandid && !vaja_jatkata && 
                    tyvi->komp_jargmine->k_tyyp == K_SUFF)
                {
                FSXSTRING sona;
                sona = (const FSxCHAR *)(S6na->Left(S6naPikkus));
                if (!TaheHulgad::OnLopus(&(sona), FSxSTR("lt")))
                    break;
                }

            /* leiame tyvi2 */
            res = liitsona(&cvahe_variant.ptr, tyvi, S6na, pik, sobivad_variandid, paha_koht,paha_koha_suurus);
//{
//printf("DB:%s:%d\n", __FILE__,__LINE__);
//MRFTULEMUSED dbTul;
//variandid_tulemuseks(&dbTul, KOIK_LIIGID, sobivad_variandid);
//}
	        if (res > ALL_RIGHT)
	            return res; /* viga! */

            if (*sobivad_variandid) /* mingi ty1-ga leidub sobiv kombinatsioon */
                {
                continue;
                }

            /* lisan tyvi1-ga variandid ahelatesse */
            for (tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant) /* vt tyvi1 tyype */
                { 
                uus_variant = lisa_ahel(&mille_taha, variant);
                if (!uus_variant)
                    return CRASH;
                mille_taha = uus_variant;
                esimene = esimene_komp(uus_variant);
                uustyvi = lisa_1komp(&esimene);
                if (!uustyvi)
                    return CRASH;
                kopeeri_komp(uustyvi, esimene);
                essa = esimene_komp(tmp);
                lisa_min_info(uustyvi, &(esimene->algsona), 
                    esimene->nihe + essa->k_pikkus, esimene->k_pikkus - essa->k_pikkus);
                kopeeri_komp(esimene, essa);
                }
            }
        ahelad_vabaks(&cvahe_variant.ptr);
        if (*sobivad_variandid) /* mingi ty1-ga leidub sobiv kombinatsioon */
            {
            if (TaheHulgad::OnKaashaalik((*S6na)[pik-1]) && TaheHulgad::OnAeiu((*S6na)[pik]) )/* nt kriitik_avastus */
                vaja_jatkata = 1;      /* vt veel ty1-sid */
            else
                break; /* rohkem ty1-sid ei proovi */
            }
	    }
    return ALL_RIGHT;
    }
