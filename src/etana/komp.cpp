

//* liitsona komponentidega tegelevad alamprogrammid
//* 30.03.2001 HJK
//* 2002.03.20 klass �mberv��natud

#include <string.h>

#include "mrf-mrf.h"
#include "adhoc.h"

/*
* ahela esimese komponendi lisamine
*/
KOMPONENT *MORF0::lisa_esimene(VARIANTIDE_AHEL *kuhu)
    {
    KOMPONENT *komp;

    komp = lisa_1komp(&(kuhu->variant));
    if (!komp)
        return NULL;
    nulli_1komp(komp);
    return(komp);
    }

/*
* ahela esimese komponendi leidmine
*/
KOMPONENT *MORF0::esimene_komp(VARIANTIDE_AHEL *ahel)
    {
    return(ahel->variant);
    }

/*
* kopeeri komponentide ahel *kust ahela *kuhu sappa
*/
KOMPONENT *MORF0::kop_kompid(KOMPONENT **kuhu, KOMPONENT *kust)
    {
    KOMPONENT **t, *t1, *t2;

    t = kuhu;
    if (*t)
        for (; (*t)->komp_jargmine; t=&((*t)->komp_jargmine));
    for (t1=kust; t1; t1=t1->komp_jargmine)
        {
        t2 = lisa_1komp(t);
        if (!t2)
            return t2;
        kopeeri_komp(t2, t1);
        t = &t2;
        }
    return *kuhu;
    }

/*
*  lisa 1 (liit)sona komponent komponentide ahelasse komp-i taha
*/
KOMPONENT *MORF0::lisa_1komp(KOMPONENT **komp)
    {
    KOMPONENT *uusk;

    //uusk = (KOMPONENT *)malloc(sizeof(S_KOMPONENT));
    uusk = new KOMPONENT;
    //if (uusk)
    //    {
    nulli_1komp(uusk);
    if (!*komp)
        {
	    *komp = uusk;
	    uusk->komp_eelmine = 0;
	    uusk->komp_jargmine = 0;
        }
    else
        {
        if ((*komp)->komp_jargmine)
            (*komp)->komp_jargmine->komp_eelmine = uusk;
	    uusk->komp_jargmine = (*komp)->komp_jargmine;
        (*komp)->komp_jargmine = uusk;
        uusk->komp_eelmine = *komp;
        }
    //    }
    return(uusk);
    }

void MORF0::nulli_1komp(KOMPONENT *komp)
    {
    if (!komp)
        return;
//    komp->algsona = NULL;
    komp->algsona = FSxSTR("");
//    komp->k_algus = NULL;
    komp->nihe = 0;
    komp->k_algus = FSxSTR("");
    komp->k_pikkus = 0;
    komp->k_tyyp = 0;
//    komp->ty_lgrd_pikkus = 0;
    komp->jrk_nr = -1;            /* tyve puhul on -1 jama */
    komp->liitumistyyp = 0;
    komp->sl = FSxSTR(" ");
    (komp->sl)[0] = 0;
    komp->lgr = 0;                /* ?? */
    komp->lpnr = -1;
//    komp->liitumisinfo[0] = '\0'; /* pole loplik? */
    komp->liitumisinfo = FSxSTR(""); /* pole loplik? */
//    komp->algvorm[0] = '\0';
    komp->algvorm = FSxSTR("");
	komp->sonastikust = 1; // leitud p�his�nastikust
    }

void MORF0::kopeeri_komp(KOMPONENT *kuhu, KOMPONENT *kust)
    {
//    int i;

    if (!kuhu || !kust)
        return;
    kuhu->algsona = kust->algsona;
    kuhu->nihe = kust->nihe;
    kuhu->k_algus = kust->k_algus;
    kuhu->k_pikkus = kust->k_pikkus;
    kuhu->k_tyyp = kust->k_tyyp;
//    kuhu->ty_lgrd_pikkus = kust->ty_lgrd_pikkus;
//    for (i=0; i < kuhu->ty_lgrd_pikkus; i++)
//        kuhu->ty_lgrd[i] = kust->ty_lgrd[i];
    kuhu->jrk_nr = kust->jrk_nr;            
    kuhu->liitumistyyp = kust->liitumistyyp;            
//    kuhu->sl[0] = kust->sl[0];
    kuhu->sl = kust->sl;
    kuhu->tylgr = kust->tylgr; // tegelikult struktuuri kopeerimine
    kuhu->lgr = kust->lgr;                
    kuhu->lpnr = kust->lpnr;
//    strcpy(kuhu->liitumisinfo, kust->liitumisinfo); 
//    strcpy(kuhu->algvorm, kust->algvorm);
    kuhu->liitumisinfo = kust->liitumisinfo; 
    kuhu->algvorm = kust->algvorm;
	kuhu->sonastikust = kust->sonastikust;
    }

/*
* 1 variandile koha lisamine ahelase *ahel taha
*/
VARIANTIDE_AHEL *MORF0::lisa_1ahel(VARIANTIDE_AHEL **ahel)
    {
    VARIANTIDE_AHEL *uusahel;

    uusahel = (VARIANTIDE_AHEL *)malloc(sizeof(VARIANTIDE_AHEL));
    if (uusahel)
        {
        uusahel->variant = NULL;
	    if (!*ahel)
            {
		    *ahel = uusahel;
		    uusahel->jargmine_variant = 0;
		    uusahel->eelmine_variant = 0;
	        }
	    else
            {
            if ((*ahel)->jargmine_variant)
                (*ahel)->jargmine_variant->eelmine_variant = uusahel;
		    uusahel->jargmine_variant = (*ahel)->jargmine_variant;
            (*ahel)->jargmine_variant = uusahel;
		    uusahel->eelmine_variant = *ahel;
            }
        }
    return(uusahel);
    }

void MORF0::nulli_1variant(VARIANTIDE_AHEL **ahel)
    {
    if (!*ahel)
        return;
    (*ahel)->variant = NULL;
    }


/*
* kuhu peaks olema tyhi ahel
*/
VARIANTIDE_AHEL *MORF0::kopeeri_ahel(VARIANTIDE_AHEL *kuhu, VARIANTIDE_AHEL *kust)
    {
    KOMPONENT *t;

    t = kop_kompid(&(kuhu->variant), esimene_komp(kust));
    if (!t)
        return NULL;

/*    t1 = kuhu->variant;
    if (t1)
        for (; t1->komp_jargmine; t1=t1->komp_jargmine);
    for (t=kust->variant; t; )
        {
        if (t1==NULL && t1==kuhu->variant)
            t2 = lisa_esimene(kuhu);
        else
            t2 = lisa_1komp(&t1);
        nulli_1komp(t2);
        kopeeri_komp(t2, t);
        t = t->komp_jargmine;
        t1 = t2;
        }*/
    return kuhu;
    }

/*
* lisa ja kopeeri 1 ahel
*/
VARIANTIDE_AHEL *MORF0::lisa_ahel(VARIANTIDE_AHEL **mille_taha, VARIANTIDE_AHEL *kust)
    {
    VARIANTIDE_AHEL *uus_variant;

    uus_variant = lisa_1ahel(mille_taha);
    if (!uus_variant)
        return (uus_variant);
    if (!kopeeri_ahel(uus_variant, kust))
        return NULL;
    return (uus_variant);
    }

/*
* 1 komponentide ahelate ahela vabastamine
*/
void /*MORF0::*/ahelad_vabaks(VARIANTIDE_AHEL **ahel)
    {
    while (*ahel)
        {
        eemalda_1ahel(ahel);
        }
    assert(*ahel==NULL);
    }

/*
* 1 komponentide ahela vabastamine
*/
void /*MORF0::*/eemalda_1ahel(VARIANTIDE_AHEL **ahel)
    {
    VARIANTIDE_AHEL *uusahel=0;

    komp_vabaks(&((*ahel)->variant));
    if ((*ahel)->eelmine_variant)
        {
        (*ahel)->eelmine_variant->jargmine_variant = (*ahel)->jargmine_variant;
        uusahel = (*ahel)->eelmine_variant;
        }
    if ((*ahel)->jargmine_variant)
        {
        (*ahel)->jargmine_variant->eelmine_variant = (*ahel)->eelmine_variant;
        if (!uusahel)
            uusahel = (*ahel)->jargmine_variant;
        }
    free(*ahel);
    *ahel = uusahel;
    }

/*
* 1 komponentide ahela vabastamine
*/
void /*MORF0::*/komp_vabaks(KOMPONENT **komp)
    {
    KOMPONENT *t, *t1;

    for (t=*komp; t; )
        {
        t1 = t->komp_jargmine;
		delete t;
        t = t1;
        }
    *komp = 0;
    }

/*
* leiab viimase ahela 
*/
VARIANTIDE_AHEL *MORF0::viimane_variant(VARIANTIDE_AHEL *ahel)
    {
    VARIANTIDE_AHEL *variant;
    
    for (variant=ahel; variant->jargmine_variant; variant=variant->jargmine_variant);
    return variant;
    }
/*
* leiab viimase prefiksita algava ahela 
*/
VARIANTIDE_AHEL *MORF0::viimane_prefita_variant(VARIANTIDE_AHEL *ahel)
    {
    VARIANTIDE_AHEL *variant;
    KOMPONENT *esimene;
    
    for (variant=ahel; variant->jargmine_variant; variant=variant->jargmine_variant)
        {
        esimene = esimene_komp(variant);
        if (esimene->k_tyyp == K_PREF)
            return (variant->eelmine_variant);
        }
    esimene = esimene_komp(variant);
    if (esimene->k_tyyp == K_PREF)
        return (variant->eelmine_variant);
    return variant;
    }

/*
* lisa info, mis iga komp juures alati olemas on
*/
void MORF0::lisa_min_info(KOMPONENT *komp, FSXSTRING *algsona, int nihe, int k_pikkus)
    {
    komp->algsona = *algsona;
    komp->k_algus = (const FSxCHAR *)(algsona->Mid(nihe, k_pikkus));
    komp->k_pikkus = k_pikkus;
    komp->nihe = nihe;
    }

/*
* lisa info, mis pref, suf ka lopu puhul alati olemas on
*/
void MORF0::lisa_psl_info(KOMPONENT *komp, int tyyp, int jrk_nr)
    {
    komp->k_tyyp = tyyp;
    komp->jrk_nr = jrk_nr;
    }

void MORF0::lisa_ty_info(KOMPONENT *kuhu, TYVE_INF *grupid, int sl_ind, int mitmes )
    {
    FSXSTRING slsonalk;
    int i;

    memmove(&(kuhu->tylgr), grupid+mitmes, sizeof(TYVE_INF)); 
    kuhu->sl = (*sonaliik[sl_ind]).Mid(mitmes,1);

    kuhu->k_tyyp = K_TYVI;
    leia_algvorm(kuhu); // algvorm algoritmi jaoks
    //kuhu->liitumisinfo = (*sonaliik[sl_ind]);
    kuhu->liitumisinfo = (*sonaliik[sl_ind]).Mid(mitmes,1);
    slsonalk = (*sonaliik[sl_ind]);
    for (i=0; i < slsonalk.GetLength(); i++)
        {
        if (slsonalk[i] == MITTELIITUV_SL || slsonalk[i] == L_MITTELIITUV_SL || slsonalk[i] == W_SL)
            {
            if (GetLgNr(grupid, i) == GetLgNr(grupid, mitmes))
                {
                if (kuhu->algvorm != FSxSTR("lugu") )// && // vastik erand: lugu-loo, lood-loo, loog-loo
                   // !TaheHulgad::OnAlguses(&(kuhu->k_algus), FSxSTR("ohja")) && // ohi ei sobi, ohjad sobib...       
                   // !TaheHulgad::OnAlguses(&(kuhu->k_algus), FSxSTR("udeme")))  // ude ei sobi, udemed sobib...       
                    kuhu->liitumisinfo += slsonalk[i];
                }
            }
        }
    }

void MORF0::lisa_lp_info(KOMPONENT *kuhu, TYVE_INF *grupid, int mitmes, char lopunr )
    {
    kuhu->lgr = GetLgNr(grupid, mitmes);
    kuhu->lpnr = endingr( kuhu->lgr, lopunr );
    }

void MORF0::lisa_ty_ja_lp_info(VARIANTIDE_AHEL *ahel, TYVE_INF *grupid, int sl_ind, int mitmes, char lopunr) 
    {
    KOMPONENT *tyvi, *lopp;
    
    tyvi = esimene_komp(ahel);
    lopp = tyvi->komp_jargmine;
    lisa_ty_info(tyvi, grupid, sl_ind, mitmes);
    lisa_lp_info(lopp, grupid, mitmes, lopunr);
    }

void MORF0::lisa_suf_ja_lp_info(KOMPONENT *kuhu, TYVE_INF *grupid, int sl_ind, int mitmes, char lopunr) 
    {
    KOMPONENT *lopp;
    
    lopp = kuhu->komp_jargmine;
    lisa_ty_info(kuhu, grupid, sl_ind, mitmes);
    if (kuhu->algvorm.GetLength()==0)
        kuhu->algvorm = kuhu->k_algus;
    kuhu->k_tyyp = K_SUFF;
    lisa_lp_info(lopp, grupid, mitmes, lopunr);
    }


/*
* kontr, kas tyvi on juba sonastikus esitatud liitsonana
*/
int MORF0::on_liitsona(KOMPONENT *komp)
    {
    int idx;

    if (komp->k_tyyp == K_TYVI)
        {
        if (komp->sl[0])  /* tyvele vastab ka sonastikus midagi */
            {
            idx = (komp->tylgr).piiriKr6nksud-1;
            if (idx >= 0)
                return 1;  /* on liitsona */
            }
        }
    return 0;
    }

/*
* kontrollib, kas leidub teatud tyvi/suf+lopuga variant
*/
int MORF0::on_tylopuga(VARIANTIDE_AHEL *variandid, KOMPONENT *ty, KOMPONENT *lopp)
    {
    VARIANTIDE_AHEL *variant;
    KOMPONENT *komp;

    for (variant=variandid; variant; variant=variant->jargmine_variant)
        {
        for (komp=esimene_komp(variant); komp->komp_jargmine; komp=komp->komp_jargmine);
        if (komp->k_tyyp != lopp->k_tyyp)
            continue;
        if (komp->k_algus != lopp->k_algus)
            continue;
        if (komp->k_pikkus != lopp->k_pikkus)
            continue;
        if (ty == NULL) /* ty/suf pole vaja kontrollida */
            return 1;
        else
            {
            komp = komp->komp_eelmine;
            if (komp->k_tyyp != ty->k_tyyp)
                continue;
            if (komp->k_algus != ty->k_algus)
                continue;
            if (komp->k_pikkus != ty->k_pikkus)
                continue;
            if (komp->k_tyyp == K_SUFF)
                {
                if (komp->jrk_nr == ty->jrk_nr)
                    return 1;
                }
            else if (komp->k_tyyp == K_TYVI)
                {
                if (komp->sl[0] != ty->sl[0])
                    continue;
				if (komp->sonastikust == ty->sonastikust)
					{
                    if (SamadTYVE_INF(komp->tylgr, ty->tylgr)==true)
						return 1;  //võrdsed
					}
                }
            else
                continue;
            }
        }
    return 0;
    }

// asenda tyves 1 string teisega
void MORF0::asenda_tyves(VARIANTIDE_AHEL **variandid, const FSxCHAR *mis, const FSxCHAR *millega)
    {
    VARIANTIDE_AHEL *variant;
    KOMPONENT *komp;

    for (variant=*variandid; variant; variant=variant->jargmine_variant)
        {
        for (komp=esimene_komp(variant); komp->komp_jargmine; komp=komp->komp_jargmine)
            {
            if (komp->k_tyyp == K_TYVI)
                komp->k_algus.Replace(mis, millega, 1);
            }
        }
    }

/*
* leia komponendi algvorm (ilma lisakr�nksudeta; vajalik algoritmi t��ks, mitte v�ljastamiseks)
* return (algvormi pikkus)
 * NB! annab tagasi ainult ühe võimaliku algvormi;
*/
int MORF0::leia_algvorm(KOMPONENT *komp)
    {
    AVTIDX idx;
    bool ptr;
    FSXSTRING algv_tyvi;

    if (komp->k_tyyp != K_TYVI)
        return 0;
    // idx-s on tyvemuutuste grupi nr
    //idx.tab_idx = GetTabIdx(&(komp->tylgr), 0);
	//idx.blk_idx = GetBlkIdx(&(komp->tylgr), 0);
    assert(komp->k_algus != FSxSTR(""));
    
    algv_tyvi = komp->k_algus;

    ptr=DCTRD::OtsiTyvi(&(komp->tylgr.idx), null_lopp, sg_n, &algv_tyvi);
	if(ptr==false)
		{
		return 0;
		}
    komp->algvorm = algv_tyvi;
    return(komp->algvorm.GetLength());
    }
