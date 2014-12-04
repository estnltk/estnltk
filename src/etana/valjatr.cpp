
#include "mrf-mrf.h"

// 990322-{{
// leia see tüvi (algvorm või vormitüvi; hääldusmärkidega või ilma),
// mida tuleks välja näidata
// tagasi annab ka tüvega seotud info ja seda dptr-s

FSXSTRING *
MORF0::OigeTyveInf(
                   const TYVE_INF *tyveInf, // sisend; selle tüve lõpugrupp jms
                   int *mitmesTyveInf, // nii sisend kui väljund; siia paneb mitmes dpr-ist
                   //	const int mituTyveInfi, // sisend; alati =1
                   //	const AVTIDX *idx,
                   const FSxCHAR *snaliik, // sisend; lubatavad sõnaliigid (stringina))
                   const int lopp, // sisend; lubatav lõpp (õigemini jrk nr lõppude loendis)
                   const int vorm, // sisend; lubatav vorm (õigemini jrk nr vormide loendis)
                   FSXSTRING *tyvi) // väljund
{
    int slTabIdx;
    bool ptr;
    int k, jj;
    FSXSTRING veel1tyvi;
    char sobivad[SONAL_MAX_PIK];

    veel1tyvi = (const FSxCHAR *) (*tyvi);
    ptr = DCTRD::OtsiTyvi(
                          &(tyveInf->idx), // tyvemuutuste grupi nr
                          lopp,
                          vorm,
                          tyvi);
    if (ptr == false)
    {
        return NULL;
    }
    // MF_POOLITAJA lipu arvestamine??? pole vaja...
    // kontrollitakse mingeid tingimusi ja seejuures pole tähtis, et
    // mitmesTyveInf oleks õige number ??? s.t. ta võiks olla alati ka 0 ???
    if (mrfFlags.Chk(MF_KR6NKSA) ||
            (tyveInf[*mitmesTyveInf].piiriKr6nksud && veel1tyvi != (const FSxCHAR *) (*tyvi)))
    {
        // tuleb dptr-isse algvormi j�rgi v�tta
        if (cXXfirst(tyvi, &slTabIdx) != ALL_RIGHT)
        {
            return NULL;
        }
        k = ssobivus(dptr, (const FSxCHAR *) (*sonaliik[slTabIdx]), sonaliik[slTabIdx]->GetLength(),
                     lopp, snaliik, (int) vorm, sobivad, sizeof (sobivad));
        if (k)
        {
            for (jj = 0; jj < SONAL_MAX_PIK; jj++) /* teen koigi sobivate variantide ahelad */
            {
                if (sobivad[jj] == 0) // sobimatu sõnaliik, lõpp v vorm
                    continue;
                if (dptr[jj].idx.tab_idx != tyveInf->idx.tab_idx) // sobimatu tyvemuutuse grupp
                    continue;
                *mitmesTyveInf = jj; /* valin 1. vo'imaliku */
                break;
            }
        }
    }
    else // mingit muutust tüves pole; tyveInf ja mitmesTyveInf jäävad samaks; ainult dptr tuleb õigeks panna
    {
        memmove(dptr, tyveInf, sizeof (TYVE_INF));
    }
    return tyvi;
}
// }}-990322

void
MORF0::variandid_tulemuseks(MRFTULEMUSED *tul, const FSxCHAR *lubatavad_sonaliigid, VARIANTIDE_AHEL **ahel)
{
    assert(tul != NULL && lubatavad_sonaliigid != NULL && ahel != NULL);
    unsigned int i;
    MRFTUL tulemus;
    KOMPONENT *komp;
    unsigned int llnr, ffnr;
    FSXSTRING al = ALGV_LIIK; // algvormi otsimist v�udev s�naliik
    FSXSTRING vt_tyvi;
    FSXSTRING kronksutyvi;
    FSXSTRING loplik_tyvi;
    FSXSTRING algv_tyvi;
    FSXSTRING tl; // taandliik
    FSXSTRING lub_sl(lubatavad_sonaliigid);
    int mtmes;
    FSXSTRING *ptr;
    int lgr = 0; /* kas on ikka sobiv ?? */
    TYVE_INF ad_hoc_tyveinf; /* ad hoc vormide lisamiseks... */
    int j;

    for (VARIANTIDE_AHEL *variant = *ahel; variant; variant = variant->jargmine_variant)
    {
        FSXSTRING t_tyvi(FSxSTR("")), t_sl(FSxSTR("")), t_lopp(FSxSTR("")), t_vormid(FSxSTR(""));
        FSXSTRING vt_tyvi(FSxSTR("")), kronksutyvi(FSxSTR("")), loplik_tyvi(FSxSTR("")), algv_tyvi(FSxSTR(""));

        for (komp = esimene_komp(variant); komp; komp = komp->komp_jargmine)
        {
            if (komp->sl[0])
                t_sl = komp->sl;
            if (komp->k_tyyp == K_LOPP)
            {
                if (komp->k_pikkus > 0 && TaheHulgad::OnAlguses(&(komp->k_algus), FSxSTR("jate")))
                {
                    if (mrfFlags.Chk(MF_SPELL)) // spellimisel ei lisa mingit eristajat
                        t_tyvi += FSxSTR("jate");
                    else
                        t_tyvi += FSxSTR("=ja+te");
                    continue;
                }
                if (komp->komp_jargmine) /* pole viimane lopp */
                {
                    if (mrfFlags.Chk(MF_SPELL)); // spellimisel ei lisa mingit eristajat
                    else
                        t_tyvi += FSxSTR("+");
                }
                if (komp->komp_jargmine) /* nt ve+tte_hype */
                    t_tyvi += komp->k_algus;
                else
                {
                    if (komp->k_pikkus)
                        t_lopp += komp->k_algus;
                    else
                        t_lopp += FSxSTR("0");
                    lgr = komp->lgr; /* vaja lisa_ad_hoc jaoks */
                    llnr = (groups[lgr].gr_algus << 8) | groups[lgr].gr_lopp;
                    llnr = llnr + komp->lpnr;
                    for (i = 0; i < homo_form; i++) /*vt lopu vormihom*/
                    {
                        ffnr = fgr[homo_form * llnr + i];
                        if (!ffnr)
                            break;
                        t_vormid += vormideLoend[ ffnr ];
                        t_vormid += FSxSTR(", ");
                    }
                }
            }
            else if (komp->k_tyyp == K_PREF)
            { /* kronksundus 22.01.2002 */
                if (komp->komp_eelmine)
                    t_tyvi += FSxSTR("_");
                dptr[0].lisaKr6nksud = prfix[komp->jrk_nr].lisaKr6nksud;
                dptr[0].piiriKr6nksud = prfix[komp->jrk_nr].piiriKr6nksud;
                LisaKdptr(dptr, &kronksutyvi, &(komp->k_algus) /*vt_tyvi*/, 0);

                t_tyvi += kronksutyvi;
            }
            else if (komp->k_tyyp == K_SUFF)
            {
                t_tyvi += komp->k_algus.Left(sufix[komp->jrk_nr].mitutht); // et = või _ ees oleks ilusa kujuga tüvi
                tl = taandliik[ sufix[komp->jrk_nr].tsl ];
                if (tl.Find((FSxCHAR) 'F') != -1)
                    if (mrfFlags.Chk(MF_SPELL)); // spellimisel ei lisa sufiksi eristajat
                    else
                        t_tyvi += FSxSTR("=");
                else
                    t_tyvi += FSxSTR("_"); /* j�relkomponent */
                // kronksundus; sarnane juhuga, kui komp->k_tyyp == K_TYVI 
                //if (komp->sl[0])  // tyvele vastab ka sonastikus midagi 
                /*
                        if (tl.Find((FSxCHAR) 'F') == -1) // ja'relkomponent 
                {
                    LisaKdptr(&(komp->tylgr), &kronksutyvi, &(komp->k_algus), 0);
                }
                else // tyvi kuidagi kukku pusserdatud, nt oletamisel 
                    kronksutyvi = komp->k_algus;
                */
                // igaks juhuks pane kronksutyvi-sse midagi;
                // võib-olla on sufiks kuidagi kukku pusserdatud, nt oletamisel 
                kronksutyvi = komp->k_algus;
                if (!komp->komp_jargmine->komp_jargmine) // viimane sufiks 
                {
                    LisaKdptr(&(komp->tylgr), &kronksutyvi, &(komp->k_algus), 0);
                    ad_hoc_tyveinf = komp->tylgr;
                    // algvormindus 
                    loplik_tyvi = t_tyvi;
                    algv_tyvi = kronksutyvi;
                    if (mrfFlags.Chk(MF_ALGV)) // algvormindus 
                    {
                        // leia algvormiga seotud info
                        j = suffnr( (const FSxCHAR *)komp->algvorm );
                        // allpoololevaid tingimusi ei peakski kontrollima, 
                        // sest nad peaksid alati kehtima, kui sõnastik on õigesti tehtud
                        if (j != -1)    // sufiksi algvorm olemas
                        {               // ... ja on ikka sama paradigma sõna
                            if (komp->tylgr.idx.tab_idx == sufix[j].suftyinf[0].idx.tab_idx)
                                ad_hoc_tyveinf = sufix[j].suftyinf[0];
                        } 
                        LisaKdptr(&(ad_hoc_tyveinf), &algv_tyvi, &(komp->algvorm), 0);
                
                    }
 
                    /* sufiksi-spetsiifiline probleem */
                    loplik_tyvi += algv_tyvi.Mid(sufix[komp->jrk_nr].mitutht);
                }
                t_tyvi += kronksutyvi.Mid(sufix[komp->jrk_nr].mitutht);
            }
            else /* komp->k_tyyp == K_TYVI */
            {
                if (komp->komp_eelmine)
                    t_tyvi += FSxSTR("_");
                if (komp->sonastikust != 0) // HJK 17.05.2004 tyvele vastab ka sonastikus midagi
                {
                    ASSERT(t_sl.GetLength() > 0);
                    //LgCopy(dptr, &(komp->tylgr), 1);
                    //memmove(dptr, &(komp->tylgr), sizeof(TYVE_INF));
                    LisaKdptr(&(komp->tylgr), &kronksutyvi, &(komp->k_algus), 0);
                    /* kolmanda va'lte ma'rk satub m�nikord tyve lo~ppu, kui see on tyvi+suf liitekoht */
                    if (TaheHulgad::OnLopus(&kronksutyvi, FSxSTR("<")))
                        kronksutyvi.TrimRight(FSxSTR("<"));
                }
                else /* tyvi kuidagi kukku pusserdatud, nt oletamisel */
                    kronksutyvi = komp->k_algus;
                if (!komp->komp_jargmine->komp_jargmine) /* viimane tyvi */
                {
                    ad_hoc_tyveinf = komp->tylgr;
                    /* algvormindus */
                    loplik_tyvi = t_tyvi;
                    algv_tyvi = kronksutyvi;
                    vt_tyvi = komp->k_algus; /* vajalik tegelt ainult mitmes�naliste jaoks, sest nad on s�nastikus tyhiku asemel = m�rgiga */
                    TaheHulgad::AsendaMitu(&vt_tyvi, FSxSTR(" "), FSxSTR("="));
                    if (komp->sonastikust != 0) // HJK 17.05.2004 tyvele vastab ka sonastikus midagi
                    {
                        ASSERT(t_sl.GetLength() > 0);
                        if (mrfFlags.Chk(MF_ALGV) &&
                                // komp->sl[0] &&  /* tyvele vastab ka sonastikus midagi */
                                al.Find(t_sl) != -1)
                        {
                            mtmes = 0;
                            if (t_sl == FSxSTR("V"))
                            {
                                ptr = OigeTyveInf(&(komp->tylgr), &mtmes,
                                                  (const FSxCHAR *) t_sl, lopp_ma, ma,
                                                  &vt_tyvi);
                                if (ptr)
                                    LisaKdptr(dptr, &algv_tyvi, &vt_tyvi, mtmes);
                                /* a'ra puhuks */
#if defined (FSCHAR_UNICODE)
                                if (algv_tyvi == FSxSTR("\x00E4r"))
#else
#error Defineeri  FSCHAR_UNICODE
#endif
                                    algv_tyvi += FSxSTR("a");
                            }
                            else /* noomen */
                            {
                                ptr = OigeTyveInf(&(komp->tylgr), &mtmes,
                                                  (const FSxCHAR *) t_sl, null_lopp, sg_n,
                                                  &vt_tyvi);

                                if (ptr == NULL)
                                    // ei l"aind korda sellist tyve leida,
                                    // tuleb miskit ad hoc: sg gen
                                    ptr = OigeTyveInf(&(komp->tylgr), &mtmes,
                                                      (const FSxCHAR *) t_sl, null_lopp, sg_g,
                                                      &vt_tyvi);
                                if (ptr != NULL)
                                    /*kr6nksud.*/ LisaKdptr(dptr, &algv_tyvi, &vt_tyvi, mtmes);
                                else /* if(ptr==NULL) */
                                    // ei l"aind korda sellist tyve leida,
                                    // tuleb miskit ad hoc: pl nom
                                {
                                    ptr = OigeTyveInf(&(komp->tylgr), &mtmes,
                                                      (const FSxCHAR *) t_sl, lopp_d, pl_n,
                                                      &vt_tyvi);
                                    if (ptr != NULL)
                                    {
                                        /*kr6nksud.*/LisaKdptr(dptr, &algv_tyvi, &vt_tyvi, mtmes);
                                        algv_tyvi += FSxSTR("d");
                                    }
                                }
                            }
                            TaheHulgad::AsendaMitu(&algv_tyvi, FSxSTR("="), FSxSTR(" "));
                        }
                    }
                    loplik_tyvi += algv_tyvi;
                }
                t_tyvi += kronksutyvi;
            }
        }
        if (t_sl == FSxSTR("B")) /* 'B' on ainult sisemiseks kasut */
            t_sl = FSxSTR("A");
        if (t_sl == FSxSTR("W")) /* seda ei luba, sest on homon. vastava 'S'-ga */
            continue;
        ASSERT(t_sl.GetLength() > 0);
        if (lub_sl.Find(t_sl) == -1)
            continue; /* sonaliik polnud lubatavate hulgast */
        if (mrfFlags.Chk(MF_SPELL))
        {
            //printf("%s:%3d ", __FILE__, __LINE__);
            tul->Add((const FSxCHAR *) t_tyvi, (const FSxCHAR *) t_lopp, FSxSTR(""), (const FSxCHAR *) t_sl, (const FSxCHAR *) t_vormid); /* 1. sobiv variant */
            return;
        }
        /* ad hoc  lisan m�ned anal��sivariandid */
        /* lisa_ad_hoc eeldab, et analyysid on juba kchk1-s j�rjestatud nii, et pikemate l�ppudega variandid on tagapool */
        tulemus.tyvi = t_tyvi;
        tulemus.lopp = t_lopp;
        tulemus.sl = t_sl;
        tulemus.vormid = t_vormid;
        lisa_ad_hoc(tul, &tulemus, lgr, &ad_hoc_tyveinf, &lub_sl); /*NB on kuidagi seotud tyvekujuga: ei tohiks vist olla algvormis...*/
        if (t_sl != FSxSTR("D") || tul->Get_sl(FSxSTR("D")) == -1) /* inetu; pole veel leitud =lt+0 //_D_ // */
        {
            //printf("%s:%3d ", __FILE__, __LINE__);
            tul->Add((const FSxCHAR *) loplik_tyvi, (const FSxCHAR *) t_lopp, FSxSTR(""), (const FSxCHAR *) t_sl, (const FSxCHAR *) t_vormid);
        }
    }
    /* ad hoc lu"hendite variandi lisamine */
    if (*ahel != NULL)
    {
        komp = esimene_komp(*ahel);
        if (lub_sl != KI_LIIGID)
            lisa_ad_hoc_gi(tul, &komp->algsona);
    }
}
