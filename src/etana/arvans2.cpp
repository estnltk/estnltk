/*
* proovib arvata nimisona ja verbi
* varem on leitud l�pud 
* algoritm: kontrollib, kas m�ni lopp v�ib olla eesti k s�na l�pp
*/
#include "mrf-mrf.h"
#include "post-fsc.h"

int MORF0::arvans2(MRFTULEMUSED *tulemus, FSXSTRING *sonna, int S6naPikkus, VARIANTIDE_AHEL **variandid, const FSxCHAR *lubatavad_sl)
    {
    FSxCHAR eel, yel, yyl;
    VARIANTIDE_AHEL *variant, *viimane; // ainult selleks, et ts�keldada �le etteantud ahela 'variandid'
    KOMPONENT *k_tyvi, *k_lopp;
    FSXSTRING S6na, tyvi, lopp, vorm, *algvorm, otsitav_vorm, otsitav_lopp, tmpsona, sl;
    const FSxC5I1 *t;
    bool sobiks_nimeks;
    int tyvepik;
    FSXSTRING lub_sl;
    int i;

    lub_sl = lubatavad_sl;
    sobiks_nimeks = oletajaDct.sobiks_nimeks(sonna);
    if (!sobiks_nimeks)
        {
        int tahtedeArvSonas, tahtedeProtsentSonas;
        for(tahtedeArvSonas=0, i=0; i<S6naPikkus; i++)
            {
            if(TaheHulgad::OnTaht(sonna, i))
                tahtedeArvSonas++;
            }
        tahtedeProtsentSonas=100*tahtedeArvSonas/S6naPikkus;
        if(tahtedeProtsentSonas < 80)
            return ALL_RIGHT; // s�nas liiga v�he t�hti

        if (TaheHulgad::protsendinumber.Find((*sonna)[S6naPikkus-1]) != -1)
            return ALL_RIGHT; // s�na l�ppeb numbriga
        if (TaheHulgad::OnSuur(sonna, 0))
            {
            S6na = sonna->Right(3);
            if (TaheHulgad::AintSuuredjaNrjaKriipsud(&S6na))
	            return ALL_RIGHT;   // pole midagi peale suurta'htede, nr ega kriipsude
            if (TaheHulgad::OnProtsendinumber(&S6na))
                return ALL_RIGHT; // sona lopus liiga va'he t�hti
            for (i=0; i < S6na.GetLength(); i++)
                {
                if (TaheHulgad::OnSuur(&S6na, i))
                    return ALL_RIGHT; // sona lopus liiga va'he va'iketa'hti
                }
            sobiks_nimeks = true;
            }
        }
    S6na = *sonna;
    S6na.MakeLower();
    if (sobiks_nimeks)
        TaheHulgad::AlgusSuureks(&S6na);    // ei tea milleks see hea on?

    for (viimane=*variandid; viimane->jargmine_variant; viimane=viimane->jargmine_variant);
    for (variant=viimane; variant; variant=variant->eelmine_variant)
        {
        k_tyvi = esimene_komp(variant);
        if (k_tyvi->komp_jargmine->k_tyyp != K_LOPP)
            continue;
        if (k_tyvi->k_pikkus < 3)
            continue;       // tyvi olgu va'hemalt 3 ta'hte 
        k_lopp = k_tyvi->komp_jargmine;
        tyvi = k_tyvi->k_algus;
        lopp = k_lopp->k_algus;
        tyvepik = k_tyvi->k_pikkus;

	    eel = tyvi[tyvepik-1];
        yel = tyvi[tyvepik-2];
        yyl = tyvi[tyvepik-3];
        if (tulemus->on_tulem() && tulemus->Get_sl(LIIK_VERB) != -1) // verbi anal��s juba oletatud
            {
            if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("eeri")) ||
                TaheHulgad::OnLopus(&(tyvi), FSxSTR("eeru")) ||
                TaheHulgad::OnLopus(&(tyvi), FSxSTR("tse")))  
                return ALL_RIGHT; // vist pole nimisona
            if (tulemus->Get_vormid(FSxSTR("ma, ")) != -1 ||
                tulemus->Get_vormid(FSxSTR("da, ")) != -1 ||
                tulemus->Get_vormid(FSxSTR("b, ")) != -1)
                return ALL_RIGHT; // vist pole nimisona
            }
        if (!sobiks_nimeks)
            {
            if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("ii")) && k_lopp->k_pikkus > 0)
                continue;  // vist pole tyve lp
            if (lopp == FSxSTR("t"))
                {
                if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("is")))
                    continue;  // trombonis+t
//                if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("las"))); // somaallas+t
//                else if (TaheHulgad::OnTaishaalik(yel))
//                    continue;  // trombonis+t 
                }
            if (lopp == FSxSTR("ni"))
                {
                if (eel==yel && TaheHulgad::OnTaishaalik(yel))
                    continue;  // vist pole tyve lp 
                }
            if (lopp == FSxSTR("i"))
                {
                if (TaheHulgad::OnAeiu(yel) && eel == (FSxCHAR)'s'); // ersalas+i
                else continue;  // ei sobi lopuks 
                }
            if (lopp == FSxSTR("e"))
                {
                if (TaheHulgad::OnTaishaalik(yyl) && TaheHulgad::OnTaishaalik(yel) && TaheHulgad::OnKaashaalik(eel)); // VVKe
                else if (TaheHulgad::OnKaashaalik(yel) && TaheHulgad::OnKaashaalik(eel) && eel != (FSxCHAR)'n') // KKe
                    {
                    if (tyvepik > 3 && tyvi[tyvepik-4] == yyl)
                        continue;    // ...aars+e ei sobi  
                    }
                else 
                    continue; // ei sobi lopuks 
                }
            }
        SILP s;
        s.silbita(&tyvi);
        if (s.silpe() == 0)          // liiga l�hike t�vi vm jama
            continue;
        //s.silbivalted();
        for (t=oletajaDct.pn_lopud_jm.Get((const FSxCHAR *)k_lopp->k_algus); t; 
                                                    t=oletajaDct.pn_lopud_jm.GetNext())
            {
            // m�ned s�nad ei saa olla muud kui sg n
            if (TaheHulgad::OnLopus(&(k_tyvi->algsona), FSxSTR("lane")))
                break;
            if (t->eeltahed->Find(eel) == -1) // l�pule eelnev t�ht ei sobinud
                continue;
            if (sobiks_nimeks && t->tyyp != 1)  // oletatavasti p�risnimi; siis see l�pp ei sobi
                continue;
            vorm = t->vorm;
            otsitav_lopp = t->tabeli_lopp;
            otsitav_vorm = t->tabeli_vorm;
            if (sobiks_nimeks)
                {
                // kas on soome p�risnimi?
                if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("se")) && vorm.Find(FSxSTR("sg ")) != -1)
                    {
                    if (soome_pn_se(&tyvi, tyvepik, &s)) // se -> nen
                        {
                        tmpsona = tyvi.Left(tyvepik-2);
                        tmpsona += FSxSTR("nen");
                        if (k_lopp->k_pikkus == 0)
                            tulemus->Add((const FSxCHAR *)tmpsona, FSxSTR("0"), FSxSTR(""), LIIK_PARISNIMI, (const FSxCHAR *)vorm);
                        else
                            tulemus->Add((const FSxCHAR *)tmpsona, (const FSxCHAR *)lopp, FSxSTR(""), LIIK_PARISNIMI, (const FSxCHAR *)vorm);
                        //if (s.silpe() > 2) 
                        //    continue;  // siis tavalisi anal��se ei proovigi?
                        }
                    }
                else if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("s")) && lopp == FSxSTR("t"))
                    {
                    if (soome_pn_s(&tyvi, tyvepik)) // s -> nen
                        {
                        tmpsona = tyvi.Left(tyvepik-1);
                        tmpsona += FSxSTR("nen");
                        tulemus->Add((const FSxCHAR *)tmpsona, (const FSxCHAR *)lopp, FSxSTR(""), LIIK_PARISNIMI, (const FSxCHAR *)vorm);
                        //continue;  proovi tavalisi anal��se ka?
                        }
                    }
                if (s.silpe() == 1 &&
                    oletajaDct.harvad_lopud_1.Get((FSxCHAR *)(const FSxCHAR *)lopp))
                    continue;             // mingi ad hoc filter
                }
            if (t->tyyp == 3) // verbi l�pp
                {
                if (lub_sl.Find(LIIK_VERB) == -1)
                    continue;  // ei sobi verbiks
                if (TaheHulgad::matemaatika.Find(k_tyvi->algsona[0]) != -1) // alguses nr vms matas�mbol
                    continue;  // ei sobi verbiks
                }
            for (algvorm=oletajaDct.sobiv_algv(&tyvi, &otsitav_lopp, &otsitav_vorm); algvorm; algvorm=oletajaDct.jargmine_sobiv_algv())
                {
                if (t->tyyp != 3) // vt ainult noomeneid
                    {
                    if (!oletajaDct.pn_sobiv_kirje())
                        continue;
                    //if (!sobiks_nimeks && FSxSTRCMP(oletajaDct.ot_viimane_kirje.sonaliik, LIIK_PARISNIMI)==0)
                    if (!sobiks_nimeks && FSxSTRCMP(oletajaDct.ot_viimane_kirje.sonaliik, LIIK_PARISNIMI)==0)
                        continue; // tabelist tuli mall, mis sobib ainult p�risnimele, aga siin on �ldnimi
                    }
                if (k_lopp->k_pikkus == 0)
                    lopp = FSxSTR("0");
                if (!mrfFlags.Chk(MF_ALGV))
                    algvorm = &tyvi;
                else
                    {
                    if (sobiks_nimeks) // p�risnimi
                        {
                        SILP ss;
                        ss.silbita(algvorm);
                        if (!sobiks_sg_n(algvorm, algvorm->GetLength(), &ss))
                            continue;
                        if (TaheHulgad::OnLopus(algvorm, FSxSTR("ne"))) // ne-l�pulisi p�risnimesid on tegelt v�he
                            {
                            if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("se")) && !eesti_pn_se(&tyvi, tyvepik, &s))
                                continue;
                            if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("s")) && !eesti_pn_s(&tyvi, tyvepik))
                                continue;
                            }
                        }
                    else if (t->tyyp != 3) // �ldnimi
                        if (!sobiks_sg_n_ns(algvorm, algvorm->GetLength()))
                            continue;
                    }
                if (sobiks_nimeks)
                    sl = LIIK_PARISNIMI;
                else
                    //sl = oletajaDct.ot_viimane_kirje.sonaliik;
                    sl = oletajaDct.ot_viimane_kirje.sonaliik;
                tulemus->Add((const FSxCHAR *)(*algvorm), (const FSxCHAR *)lopp, FSxSTR(""), (const FSxCHAR *)sl, (const FSxCHAR *)vorm); 
                if (t->tyyp == 3) // on verb...
                    {
                    continue;
                    }
                // nimis�na
                //tmpsona = oletajaDct.ot_viimane_kirje.tyypsona;
                tmpsona = oletajaDct.ot_viimane_kirje.tyypsona;
                if (TaheHulgad::OnLopus(&tmpsona, FSxSTR("lane"))) 
                    return ALL_RIGHT;      // muud variandid oleks sodi
                if (TaheHulgad::OnLopus(&tmpsona, FSxSTR("vere"))) 
                    return ALL_RIGHT;      // muud variandid oleks sodi
                if (lopp == FSxSTR("lt") && TaheHulgad::OnAeiu(eel) && sl != LIIK_PARISNIMI)
                    tulemus->Add((const FSxCHAR *)(*sonna), FSxSTR("0"), FSxSTR(""), FSxSTR("D"), FSxSTR("")); 
                }
            }
        if (tulemus->on_tulem())
            {
            if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("se")))
                {
                if (lopp == FSxSTR("id") || 
                    lopp == FSxSTR("le") ||
                    lopp == FSxSTR("lt") ||
                    lopp == FSxSTR("sse") ||
                    lopp == FSxSTR("st") ||
                    lopp == FSxSTR("ks") ||
                    lopp == FSxSTR("ga")) 
                    return ALL_RIGHT;      // muud variandid oleks sodi
                }
            if (TaheHulgad::OnAlguses(&lopp, FSxSTR("de")) && lopp != FSxSTR("des") && lopp.GetLength() > 2)
                {
                return ALL_RIGHT;      // muud variandid oleks sodi
                }
            }
        if (k_lopp->k_pikkus == 0)    // 0-l�pp
            {
            if (sobiks_nimeks)
                {
                if (sobiks_sg_n(&tyvi, tyvepik, &s) || !tulemus->on_tulem())
                    tulemus->Add((const FSxCHAR *)tyvi, FSxSTR("0"), FSxSTR(""), LIIK_PARISNIMI, FSxSTR("sg n, ")); 
                }
            else
                {
                if (sobiks_sg_n_ns(&tyvi, tyvepik) || !tulemus->on_tulem())
                    {
                    if (TaheHulgad::OnLopus(&(tyvi), FSxSTR("line")) || 
                        (TaheHulgad::OnLopus(&(tyvi), FSxSTR("ne")) && TaheHulgad::OnKaashaalik(tyvi[tyvi.GetLength()-3])))
                        tulemus->Add((const FSxCHAR *)tyvi, FSxSTR("0"), FSxSTR(""), LIIK_A, FSxSTR("sg n, ")); 
                    else
                        tulemus->Add((const FSxCHAR *)tyvi, FSxSTR("0"), FSxSTR(""), LIIK_YLDNIMI, FSxSTR("sg n, ")); 
                    }
                }
            }
       }
//    tulemus->SortUniq();  // sest tabelist tuleb samu algvorme mitmest kirjest...
    return ALL_RIGHT;
    }


// kas nimis�na sobiks �ldse sg n vormi?
bool MORF0::sobiks_sg_n_ns( FSXSTRING *sona, int sonapikkus)
    {
    FSXSTRING tmp;
    SILP s;
    int jj;
    FSxCHAR eel, yel, yyl;
    bool sobib_nimetav;

    s.silbita(sona);
    jj = s.silpe();
    if (jj == 0)          // liiga l�hike t�vi vm jama
        return false;
    if (mrfFlags.Chk(MF_GENE))
        return true;    // ei julge sobivuses kaheldagi 
    if (sonapikkus < 3)
        return true;    // 2-ta'heline voib alati olla nimetavas kaandes 
    if (jj == 1) 
        return true;    // 1-silbiline voib alati olla nimetavas kaandes 
	eel = (*sona)[sonapikkus-1];
    yel = (*sona)[sonapikkus-2];
    yyl = (*sona)[sonapikkus-3];
    sobib_nimetav = sobiks_sg_n( sona, sonapikkus, &s); // nagu pa'risnimedega 
    if (jj > 2)
        {
        if (TaheHulgad::OnLopus(sona, FSxSTR("iid")))  // premysliid 
            return true;
        else if (TaheHulgad::OnLopus(sona, FSxSTR("id")))
            return false;
        else if (TaheHulgad::OnLopus(sona, FSxSTR("le")) && TaheHulgad::OnTaishaalik(yyl))
            return false;
        else if (TaheHulgad::OnLopus(sona, FSxSTR("ga")) && TaheHulgad::OnTaishaalik(yyl))
            return false;
        else if (eel == (FSxCHAR)'i')
            {
            if (sonapikkus > 3 && (*sona)[sonapikkus-4]==yyl && 
                TaheHulgad::OnTaishaalik(yyl) && TaheHulgad::OnKaashaalik(yel))
                return false; // ...iini, ...aadi jms 
            }
        }
    else if (sonapikkus < 4)
        return sobib_nimetav; // ei muuda varemleitud sobib_nimetavat 
    if (TaheHulgad::OnLopus(sona, FSxSTR("ist")))
        sobib_nimetav = true;
    else if (TaheHulgad::OnLopus(sona, FSxSTR("konda")))
        sobib_nimetav = false;
    else if (TaheHulgad::OnLopus(sona, FSxSTR("konna")))
        sobib_nimetav = false;
    else if (TaheHulgad::OnLopus(sona, FSxSTR("sed")))
        sobib_nimetav = false;
    else if (TaheHulgad::OnLopus(sona, FSxSTR("kad")))
        sobib_nimetav = false;
    else if (TaheHulgad::OnLopus(sona, FSxSTR("se")))
        {
        tmp = sona->Left(sonapikkus-2);
        SILP ss;
        ss.silbita(&tmp);
        if (ent_tyvi(&tmp, sonapikkus-2, ss.silpe())) // aarse, entse vms
            sobib_nimetav = false;
        }
    else 
        {
        tmp = sona->Right(4);
        if (oletajaDct.ns_tylopud.Get((FSxCHAR *)(const FSxCHAR *)tmp)) 
            sobib_nimetav = false;  /*...andi jms */
        }
    return sobib_nimetav;
    }



