
/*
* kontr, kas S6na on tyvi1+liitsona
*/

#include "mrf-mrf.h"

int MORF0::kchk6(
    VARIANTIDE_AHEL **variandid, 
    FSXSTRING *S6na, 
    int S6naPikkus, 
    VARIANTIDE_AHEL **sobivad_variandid, 
    char *paha_koht,
    const int paha_koha_pikkus
    )
    {
    int res;

    int  pik;
    int kk;
    VARIANTIDE_AHEL *variant, *tmp, *sobiv_variant; //ok
    CVARIANTIDE_AHEL cvahe_variant, cls_variant;
    KOMPONENT *tyvi, *tyvi1, *sobivty, *sobivlp;
    KOMPONENT *tmpkomp1, *tmpkomp2;
    KOMPONENT *essa, **esi;
    int ty1_tyyp;
    //char *u_paha_koht=0; TV080723
    FSXSTRING u_S6na, vt_tyvi;
    int u_S6naPikkus;

    for (variant=*variandid; variant; variant=variant->jargmine_variant)
	    {
        char u_paha_koht[(STEMLEN+1)*(STEMLEN+1)];
        tyvi1 = esimene_komp(variant);
        ty1_tyyp = 0;
        if (tyvi1->k_tyyp == K_PREF) 
            {
            FSXSTRING tl;
            tl = taandliik[ prfix[tyvi1->jrk_nr].sl ];
            if ( tl.Find((FSxCHAR) 'V') !=-1 )  
                ty1_tyyp = 13;
            else if (tl.Find((FSxCHAR) 'S') != -1)  
                ty1_tyyp = 12;
            }
        else
            ty1_tyyp = ty11tyyp(tyvi1->liitumistyyp);
        if (!ty1_tyyp) /* ty1 ei sobi nii keerulise liitsona algusse */
            continue;
        tyvi = tyvi1->komp_jargmine;
        if (!(tyvi->komp_jargmine))
            continue;
        if (tyvi->k_tyyp == K_LOPP) 
            continue;
        if (tyvi->k_tyyp == K_SUFF) 
            continue;
        if (tyvi->k_pikkus < 5) /* ty2+ty3 ei mahu */
            continue;
        if (tyvi1->k_pikkus + tyvi->k_pikkus < 9) /* ty1+ty2+ty3 ei mahu */
            continue;

        /* keerulisemat struktuuri ei vt; ka mitut erin sufiksit ei luba, v.a. lt puhul; ??? */
        if (*sobivad_variandid &&  
                tyvi->komp_jargmine->k_tyyp == K_SUFF)
            {
            FSXSTRING sona;
            sona = (const FSxCHAR *)(S6na->Left(S6naPikkus));
            if (!TaheHulgad::OnLopus(&(sona), FSxSTR("lt")))
                break;
            }

        pik = minipik(&(tyvi->k_algus));
        if (tyvi->k_pikkus < pik + 2)
            continue;
        //int sty = tyvi->k_pikkus-2;
        /* otsi sellest kohast algavat liitsona ty1+ty2 */
        /* uue liitsona jaoks andmed paika */
        u_S6naPikkus = S6naPikkus - tyvi1->k_pikkus; 
        //TV080723 u_paha_koht = init_hjk_cxx(u_S6naPikkus, 
        //    u_paha_koht, sizeof(u_paha_koht));
        //if (!u_paha_koht)
        //    return CRASH;
        //TV080723 u_paha_koht = uus_paha(S6naPikkus,paha_koht,u_S6naPikkus,u_paha_koht);
        //if (!u_paha_koht)
        //    return CRASH;
        init_hjk_cxx(u_S6naPikkus, 
            u_paha_koht, sizeof(u_paha_koht));
        uus_paha(S6naPikkus,paha_koht,u_S6naPikkus,
                            u_paha_koht, sizeof(u_paha_koht));
        u_S6na = (const FSxCHAR *)(S6na->Mid(tyvi1->k_pikkus));
        cls_variant.ptr = lisa_1ahel(&cls_variant.ptr);
        if (!cls_variant.ptr)
            return CRASH;
        esi = &(cls_variant.ptr->variant);
        tmpkomp2 = kop_kompid(esi, tyvi);
        if (!tmpkomp2)
            return CRASH;
        for (tmpkomp1=*esi; tmpkomp1; tmpkomp1=tmpkomp1->komp_jargmine)
            {
            tmpkomp1->algsona = u_S6na;
            tmpkomp1->nihe -= tyvi1->k_pikkus;
            }
        if (ty1_tyyp == 12 && !TaheHulgad::OnAlguses(&u_S6na, FSxSTR("ise"))) /* prefiks; "ise" ei sobi */
            {
            res = kchk30(&cls_variant.ptr, &u_S6na, u_S6naPikkus, &cvahe_variant.ptr, u_paha_koht,sizeof(u_paha_koht));
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        if (!cvahe_variant.ptr) 
            {
            res = kchk4(&cls_variant.ptr, &u_S6na, u_S6naPikkus, &cvahe_variant.ptr, 
                u_paha_koht,sizeof(u_paha_koht));
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        if (!cvahe_variant.ptr) 
            {
            if (ty1_tyyp == 12 && !TaheHulgad::OnAlguses(&u_S6na, FSxSTR("ise"))) /* prefiks */
                {
                res = kchk33(&cls_variant.ptr, &cvahe_variant.ptr, u_paha_koht, sizeof(u_paha_koht));
                if (res > ALL_RIGHT)
	                return res; /* viga! */
                }
            }
        if (!cvahe_variant.ptr) 
            {
            res = kchk5(&cls_variant.ptr, &u_S6na, u_S6naPikkus, &cvahe_variant.ptr, u_paha_koht, sizeof(u_paha_koht));
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        if (cvahe_variant.ptr) /* ty1 taga v�ibki olla liits�na */
            {
            for (tmp=cvahe_variant.ptr; tmp; tmp=tmp->jargmine_variant) 
                { 
                esi = &(tmp->variant);
                if ((*esi)->liitumistyyp == L_TYVE_TYYP) /* liitsona on S suva-vorm */
                    if ((*esi)->komp_jargmine->liitumistyyp != L_TYVE_TYYP + 3) /* polegi S pl g */
                        continue;
                if ((*esi)->k_tyyp == K_PREF &&  /* ... + pref */
                    (ty1_tyyp == 12 || ty1_tyyp == 4)) /* ty1 on pref v�i S sg g */
                    ; /* pref + pref/S sg g sobivad alati */
                else
                    {
                    kk = ty11ty11(ty1_tyyp, ty11tyyp((*esi)->liitumistyyp));
                    if (!kk) /* liitsona ei sobi ty1-ga */
                        continue;
                    }
                // kontrolli s�nastikust saadud info abil, kas v�ib olla liits�na tagumine ots
                // HJK juuni 2006
                if (((*esi)->liitumisinfo).Find(L_MITTELIITUV_SL) != -1) // HJK 6.06.2006 et igasugu l�his�nad ei saaks osaleda
                    continue;
                vt_tyvi = tyvi1->k_algus;
                vt_tyvi += (*esi)->k_algus;
                if (viletsls(&vt_tyvi)) /* lubamatu liitsona */
                    continue;
                for (tmpkomp1=*esi; tmpkomp1; tmpkomp1=tmpkomp1->komp_jargmine)
                    { /* teisenda tagasi esialgse s�na taoliseks */
                    tmpkomp1->algsona = *S6na;
                    tmpkomp1->nihe += tyvi1->k_pikkus;
                    }
                /* vt et juba leitud analyysi ei lisataks uuesti */
                for (tmpkomp1=*esi; tmpkomp1->komp_jargmine; tmpkomp1=tmpkomp1->komp_jargmine);
                sobivlp = tmpkomp1;
                sobivty = tmpkomp1->komp_eelmine;
                if (on_tylopuga(*sobivad_variandid, sobivty, sobivlp)) /* selline tyvi/suf+lp juba sobivate hulgas */
                    continue;
                /* s�na anal��situd! */
                sobiv_variant = lisa_1ahel(sobivad_variandid);
                if (!sobiv_variant)
                    return CRASH;
                essa = lisa_esimene(sobiv_variant);
                kopeeri_komp(essa, tyvi1);
                tmpkomp2 = kop_kompid(&essa, *esi);
                if (!tmpkomp2)
                    return CRASH;
                }
            }
        ahelad_vabaks(&cvahe_variant.ptr);
        ahelad_vabaks(&cls_variant.ptr);
        /* s�nainfo tagasi �igeks */
        // TV080723 paha_koht = uus_paha(u_S6naPikkus, u_paha_koht, S6naPikkus, paha_koht);
        //if (!paha_koht)
        //    return CRASH;
        uus_paha(u_S6naPikkus, u_paha_koht, S6naPikkus, 
            paha_koht, paha_koha_pikkus);
        //close_hjk_cxx(u_paha_koht);
	    }
    return ALL_RIGHT;
    }
