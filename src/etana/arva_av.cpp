/*
* proovib arvata pa'risnime algvormi
*/
#include "post-fsc.h"
#include "mrf-mrf.h"
#include "post-fsc.h"

void FSxGOTAB::Start(
    //const CFSxOTAB* rec
    const FSxOTAB* rec
    )
    {
    a_tylp=rec->a_tylp;
    meta=rec->meta;
    sonaliik=rec->sonaliik;
    min_silpe=rec->min_silpe;
    max_silpe=rec->max_silpe;
    tyypsona=rec->tyypsona;
    //assert(sonaliik[1]==(FSxCHAR)'\0');
    }

int FSxGOTAB::Compare(
    const FSxGOTAB *e2,
    const int sortOrder
    )
    {
    FSUNUSED(sortOrder);
	int v;
    
    v = FSxSTRCMP( a_tylp, e2->a_tylp);
    if (v==0)
        v = FSxSTRLEN(e2->meta) - FSxSTRLEN(meta); // pikem meta on eespool
    if (v==0)
        v = FSxSTRCMP( meta, e2->meta);
    if (v==0)
        {  // muutumatu silpide arvuga mallid ettepoole
        if (min_silpe == max_silpe)
            {
            if (e2->min_silpe == e2->max_silpe)
                v = min_silpe - e2->min_silpe; // kahest muutumatust v�iksem ettepoole
            else
                v = -1;  // e1 ettepoole
            }
        else if (e2->min_silpe == e2->max_silpe)
            v = 1;
        else
            v = min_silpe - e2->min_silpe;
        }
    if (v==0)
        v = max_silpe - e2->max_silpe;
    if (v==0)
        v = FSxSTRCMP( tyypsona, e2->tyypsona);
    return v;
    }

int FSxGOTAB::Compare(
    const FSxCHAR *key,
    const int sortOrder
    )
    {
	FSUNUSED(sortOrder);
    return FSxSTRCMP(a_tylp, key);
    }

FSXSTRING *OLETAJA_DCT::sobiv_algv(FSXSTRING *tyvi, FSXSTRING *lp, FSXSTRING *vorm)
    {
    //CFSxOTAB *t;
    const FSxOTAB *t;
    FSXSTRING *str;

    otsitav_tyvi = *tyvi;
    otsitav_vorm = *vorm;
    //for (t=oletaja_tabel.Get((const FSxCHAR *)*lp); t; 
    //                            t=oletaja_tabel.GetNext(/*(const FSxCHAR *)*lp*/))
    for (t=oletaja_tabel.Get((const FSxCHAR *)*lp); t; t=oletaja_tabel.GetNext())
        {
        if (!t)
            return (NULL);    // sellist l�ppu polnud
        str = konstrui_tyvi(&otsitav_tyvi, vorm, t);
        if (str)              // �nnestus algv t�vi konstrueerida
            {
            ot_viimane_kirje = *t;
            return(str);
            }
        }
    return (NULL);  // �kski tabeli rida ei sobinud
    }

FSXSTRING *OLETAJA_DCT::jargmine_sobiv_algv(void)
    {
    const FSxOTAB *t;
    FSXSTRING *str;

    for (t=oletaja_tabel.GetNext(); t; t=oletaja_tabel.GetNext())
        {
 
        if (!t)
            return (NULL);    // sellist l�ppu polnud
        if (FSxSTRCMP(t->vorm, ot_viimane_kirje.vorm) > 0)
            return (NULL);     // pole m�tet edasi neid l�ppe vaadata
        str = konstrui_tyvi(&otsitav_tyvi, &otsitav_vorm, t);
        if (str)              // �nnestus algv t�vi konstrueerida
            {
            ot_viimane_kirje = *t;
            return(str);
            }
        }
    return (NULL);  // �kski tabeli rida ei sobinud
    }

FSXSTRING *OLETAJA_DCT::konstrui_tyvi(FSXSTRING *tyvi, FSXSTRING *vorm, const FSxOTAB *t)
    {
    int k;
    FSXSTRING tmp1;

    tmp1 = t->vorm;
    if (tmp1 != *vorm)
        return (NULL);    // otsitav vorm ei sobi
    if (!TaheHulgad::OnLopus(tyvi, t->u_tylp))
        return (NULL);    // algvormile lisatav t�vel�pp ei sobi
    a_tyvi = *tyvi;
    a_tyvi = a_tyvi.Left(a_tyvi.GetLength() - FSxSTRLEN(t->u_tylp));
    tmp1 = t->a_tylp;
    tmp1 = tmp1.Right(t->n);
    a_tyvi += tmp1;  // algvormi t�vi valmis
    if (!TaheHulgad::OnLopus(&a_tyvi,t->a_tylp))
        return (NULL);    // algvormile lisatav t�vel�pp ei sobi
    if (a_tyvi.GetLength() < 3)
        return (NULL);    // liiga l�hike
    // kas algv tyvele h��likuklassid sobivad?
    k = FSxSTRLEN(t->meta);
    if (k)
        {
        FSXSTRING tmp;
        int i;

        tmp = a_tyvi.Left(a_tyvi.GetLength() - FSxSTRLEN(t->a_tylp));
        tmp = tmp.Right(k);
        if (tmp.GetLength() != k)  // string liiga l�hike vms jama
            return (NULL);
        tmp.MakeLower();
        for (i=0; i < k; i++)
            {
            if ((t->meta[i] == (FSxCHAR)'V' && TaheHulgad::OnTaishaalik(tmp[i])) || tmp[i] == (FSxCHAR)'y')
                continue;
            if (t->meta[i] == (FSxCHAR)'L' && TaheHulgad::OnLmnr(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'P' && TaheHulgad::OnKpt(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'D' && TaheHulgad::OnKaashaalik(tmp[i]) && (tmp[i]) != (FSxCHAR)'s')
                continue;
            if (t->meta[i] == (FSxCHAR)'C' && TaheHulgad::OnKaashaalik(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'B' && TaheHulgad::OnKaashaalik(tmp[i]) && !TaheHulgad::OnKpt(tmp[i]))
                continue;
            return NULL;
            }
        }
    // silbita a_tyvi
    SILP s;
    s.silbita(&a_tyvi);
    if (s.silpe() == 0)          // liiga l�hike t�vi vm jama
        return (NULL);
    s.silbivalted();
    k = s.silpe() - s.viimane_rohuline_silp();
    ASSERT(k > 0);
    // kas a_tyvi silbid sobivad?
    if (k < t->min_silpe || k > t->max_silpe)
        return (NULL);  // vale silpide arv
    if (FSxSTRCMP(t->sonaliik, LIIK_VERB)==0)
        {
        if (TaheHulgad::OnLopus(&a_tyvi, FSxSTR("ne")) && s.silpe() > 3)
            return (NULL);
        }
    // teatud juhtudel v�lte arvestamine
    if (!FSxSTRCMP(t->tyypsona, FSxSTR("ragin")))
        { // sobivad ainult 2-silbilised 1. v�ltes s�nad 
        if (s.silpe() == 2 && k == 2 && s.silbid[0]->valde == 1)
            ; // OK
        else
            return (NULL);
        }
    // et v�ltida asju nagu ��vli -> ��vl
    if (k == 1 && TaheHulgad::OnLopus(&a_tyvi, FSxSTR("l")) &&
        !TaheHulgad::OnLopus(&a_tyvi, FSxSTR("ll")) &&
        !TaheHulgad::OnLopus(&a_tyvi, FSxSTR("rl")) &&
        !TaheHulgad::OnLopus(&a_tyvi, FSxSTR("hl")))
        {
        if (s.silbid[s.viimane_rohuline_silp()]->valde == 3 &&
            TaheHulgad::OnKaashaalik(a_tyvi[a_tyvi.GetLength()-2]))
            return (NULL);
        }
    // itaalia nimed
    if (TaheHulgad::OnLopus(&a_tyvi, FSxSTR("cc")) && TaheHulgad::OnLopus(tyvi, FSxSTR("cci")))
        return (NULL);
    return (&a_tyvi);
    }
// p�risnimele sobimatute muutumismallide elimineerimiseks
bool OLETAJA_DCT::pn_sobiv_kirje(void)
    {
    assert(ot_viimane_kirje.tyypsona);
    if (!FSxSTRCMP(ot_viimane_kirje.tyypsona, FSxSTR("praene")))
        return false;
    if (!FSxSTRCMP(ot_viimane_kirje.tyypsona, FSxSTR("heeringas")))
        return false;
    if (!FSxSTRCMP(ot_viimane_kirje.tyypsona, FSxSTR("kreemjas")))
        return false;
    return true;
    }
// return true, kui s�na v�iks suurt�helisuse poolest olla p�risnimi
bool OLETAJA_DCT::sobiks_nimeks(FSXSTRING *sisendsona)
    {
    //FSXSTRING S6na;
    int S6naPikkus, i;

    if (!sobiks_sonaks(sisendsona))
        return false;
    S6naPikkus = sisendsona->GetLength();
    // ei saa suurt�helisust niisama lihtsalt kontrollida, 
    // sest pole k�ikv�imalike ime-suurt�htede loendit 
    if (!TaheHulgad::OnSuur(sisendsona, 0) && !TaheHulgad::OnSuur(sisendsona, 1)) // pole Nimi ega eNimi
        return false;  // 1. v�i ��rmisel juhul 2. t�ht oli v�ike
    for (i=S6naPikkus-1; i > 0; i--)
        {
        if (!TaheHulgad::OnPisi(sisendsona, i))
            break;
        }
//    S6na = *sisendsona;
//    S6na.TrimRight(TaheHulgad::vaiketht);
//    spik = S6na.GetLength();
    if ( i > S6naPikkus-3 )  // liiga l�hike ots
        {
        if (TaheHulgad::OnAlguses(sisendsona, FSxSTR("Mc")) || 
                TaheHulgad::OnAlguses(sisendsona, FSxSTR("Mac")))
            return true;
        if (!TaheHulgad::OnSuur(sisendsona, i-1)) // ja pole nt NoWe
            return false;
        }
    return true;
    }
// return true, kui v�iks t�htede poolest olla mingi normaalne s�na, mida lingvistiliselt anal��sida
bool OLETAJA_DCT::sobiks_sonaks(FSXSTRING *sisendsona)
    {
    FSXSTRING S6na;
    int S6naPikkus, i;

    S6naPikkus = sisendsona->GetLength();
    if (S6naPikkus < 3)
        return false;
    for (i=0; i < S6naPikkus; i++)
        {
        if (!TaheHulgad::OnTaht(sisendsona, i) && 
            TaheHulgad::amor_kriipsud.Find((*sisendsona)[i]) == -1)
            return false;
        }
    for (i=0; i < S6naPikkus; i++)
        {
        if (!TaheHulgad::OnSuur(sisendsona, i))
            break;
        }
    if (i == S6naPikkus) // ainult suured t�hed
        {
        if (i < 5)          // pigem akron��m
            return false;
        else
            return true;
        }
    return true;
    }

const FSxCHAR *OLETAJA_DCT::sobiv_analoog(FSXSTRING *tyvi, FSXSTRING *sonaliik)
    {
    FSxGOTAB *t;
    const FSxCHAR *str;
    FSXSTRING tylp;
    int i;

    otsitav_g_tyvi = *tyvi;
    otsitav_sonaliik = *sonaliik;

    for (i=tyvi->GetLength()-1; i >=0; i-- ) // algul otsime t�vel�pu j�rgi
        {
        tylp = tyvi->Right(i);
        otsitav_tylp = tylp;
        for (t=gene_oletaja_tabel.Get((const FSxCHAR *)tylp); t; t=gene_oletaja_tabel.GetNext((const FSxCHAR *)tylp))
            {
            if (!t)
                return (NULL);    // sellist t�vel�ppu polnud
            str = leia_analoog(&otsitav_g_tyvi, &otsitav_sonaliik, t);
            if (str)              // �nnestus analoog leida
                {
                return(str);
                }
            }
        }
    // �kski tabeli rida ei sobinud
    if (otsitav_sonaliik == LIIK_PARISNIMI)
        {
        otsitav_sonaliik = LIIK_YLDNIMI;
        for (i=tyvi->GetLength()-1; i >=0; i-- ) // algul otsime t�vel�pu j�rgi
            {
            tylp = tyvi->Right(i);
            otsitav_tylp = tylp;
            for (t=gene_oletaja_tabel.Get((const FSxCHAR *)tylp); t; t=gene_oletaja_tabel.GetNext((const FSxCHAR *)tylp))
                {
                if (!t)
                    return (NULL);    // sellist t�vel�ppu polnud
                str = leia_analoog(&otsitav_g_tyvi, &otsitav_sonaliik, t);
                if (str)              // �nnestus analoog leida
                    {
                    return(str);
                    }
                }
            }
        }
    return (NULL);  // �kski tabeli rida ei sobinud
    }

const FSxCHAR *OLETAJA_DCT::jargmine_sobiv_analoog(void)
    {
    FSxGOTAB *t;
    const FSxCHAR *str;

    for (t=gene_oletaja_tabel.GetNext((const FSxCHAR *)otsitav_tylp); t; t=gene_oletaja_tabel.GetNext((const FSxCHAR *)otsitav_tylp))
        {
 
        if (!t)
            return (NULL);    // sellist t�vel�ppu polnud
        str = leia_analoog(&otsitav_g_tyvi, &otsitav_sonaliik, t);
        if (str)              // �nnestus analoog leida
            {
            return(str);
            }
        }
    return (NULL);  // �kski tabeli rida ei sobinud
    }

const FSxCHAR *OLETAJA_DCT::leia_analoog(FSXSTRING *tyvi, FSXSTRING *sonaliik, const FSxGOTAB *t)
    {
    int k;
    FSXSTRING tylp;
    FSXSTRING tmp1;

    // kas s�naliik on �ige?
    if (t->sonaliik != *sonaliik)
        return (NULL);
    // kas algv tyvele h��likuklassid sobivad?
    k = FSxSTRLEN(t->meta);
    if (k)
        {
        FSXSTRING tmp;
        int i;

        tmp = tyvi->Left(tyvi->GetLength() - FSxSTRLEN(t->a_tylp));
        tmp = tmp.Right(k);
        if (tmp.GetLength() != k)  // string liiga l�hike vms jama
            return (NULL);
        tmp.MakeLower();
        for (i=0; i < k; i++)
            {
            if ((t->meta[i] == (FSxCHAR)'V' && TaheHulgad::OnTaishaalik(tmp[i])) || tmp[i] == (FSxCHAR)'y')
                continue;
            if (t->meta[i] == (FSxCHAR)'L' && TaheHulgad::OnLmnr(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'P' && TaheHulgad::OnKpt(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'D' && TaheHulgad::OnKaashaalik(tmp[i]) && (tmp[i]) != (FSxCHAR)'s')
                continue;
            if (t->meta[i] == (FSxCHAR)'C' && TaheHulgad::OnKaashaalik(tmp[i]))
                continue;
            if (t->meta[i] == (FSxCHAR)'B' && TaheHulgad::OnKaashaalik(tmp[i]) && !TaheHulgad::OnKpt(tmp[i]))
                continue;
            return NULL;
            }
        }
    // silbita tyvi
    SILP s;
    s.silbita(tyvi);
    if (s.silpe() == 0)          // liiga l�hike t�vi vm jama
        return (NULL);
    s.silbivalted();
    k = s.silpe() - s.viimane_rohuline_silp();
    ASSERT(k > 0);
    // kas a_tyvi silbid sobivad?
    if (k < t->min_silpe || k > t->max_silpe)
        return (NULL);  // vale silpide arv
    if (FSxSTRCMP(t->sonaliik, LIIK_VERB)==0)
        {
        if (TaheHulgad::OnLopus(tyvi, FSxSTR("ne")) && s.silpe() > 3)
            return (NULL);
        }
    if (FSxSTRCMP(t->sonaliik, LIIK_VERB)==0)
        if (*sonaliik != LIIK_VERB)
            return(NULL);
    // teatud juhtudel v�lte arvestamine
    if (!FSxSTRCMP(t->tyypsona, FSxSTR("ragin")))
        { // sobivad ainult 2-silbilised 1. v�ltes s�nad 
        if (s.silpe() == 2 && k == 2 && s.silbid[0]->valde == 1)
            ; // OK
        else
            return (NULL);
        }
    return (t->tyypsona);
    }
