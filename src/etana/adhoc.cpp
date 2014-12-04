#include "mrf-mrf.h"
#include "adhoc.h"


void MORF0::lisa_ad_hoc_gi(MRFTULEMUSED *tul, FSXSTRING *s6na)
    {
    //const CFSxC5* l;
    //l = ad_hoc.sonad.Get((const FSxCHAR *)(*s6na));
    const FSWCHAR* p=(const FSWCHAR *)*s6na;
    const FSxC5* l = ad_hoc.sonad.Get(p);
    if ( l )
        {
        tul->Add(l->lemma, l->lp, FSxSTR(""), l->sl, l->vorm);
        }
    }

void MORF0::lisa_ad_hoc(MRFTULEMUSED *tul, MRFTUL *t, int lgr, TYVE_INF *tyveinf, const FSXSTRING *lub_sl /*FSxCHAR *lubatavad_sl*/)
    {
    //CFSxI2C5I1C4 *ad_hoc_v;
    const FSxI2C5I1C4 *ad_hoc_v;
    FSXSTRING uustyvi, uusstr1;
    FSXSTRING verb_sl(FSxSTR("V"));

    for (ad_hoc_v=ad_hoc.vormid.Get((const FSxCHAR *)(t->vormid)); 
                                        ad_hoc_v; ad_hoc_v=ad_hoc.vormid.GetNext(/*(const FSxCHAR *)(t->vormid)*/))
        {

        if ( mrfFlags.Chk(MF_ALGV) && !(ad_hoc_v->on_algvorm))
            continue;   // see rida algvorminduse puhuks ei sobi 
        if ( !mrfFlags.Chk(MF_ALGV) && !(ad_hoc_v->pole_algvorm))
            continue;   // see rida mitte-algvorminduse puhuks ei sobi 
        if (t->lopp != ad_hoc_v->on_lopp)
            continue;   // vale lopuvariant
        if (t->sl != ad_hoc_v->on_sl)
            continue;   // vale sonaliik 
        if (!(TaheHulgad::OnLopus(&(t->tyvi), ad_hoc_v->kohustuslik_tyvelp)))
            continue;   // kohustuslik tyvelopp puudu
        if ( tul->GetTL( ad_hoc_v->eelmistel_keelatud_tyvelp, 
                              ad_hoc_v->uus_lp,
                              FSxSTR(""),
                              ad_hoc_v->uus_sl, 
                              ad_hoc_v->uus_vorm,
                              0) )
            continue;   // ad_hoc analyys juba olemas 
        if (*lub_sl == KI_LIIGID)
            if (verb_sl == ad_hoc_v->on_sl)
                  if (!ad_hoc.verbilopud.Get((FSxCHAR *)(const FSxCHAR *)ad_hoc_v->on_lopp))
                    continue;   // enamasti Verb+ki puhul ei maksa ad hoc S ja A teha 
        if (ad_hoc_v->lisatingimus == 1)
            {
            if (t->tyvi.ReverseFind((FSxCHAR) '=') > t->tyvi.ReverseFind((FSxCHAR) '_'))
                continue; // A lopus ei tohi olla sufiks 
            if (TaheHulgad::OnLopus(&(t->tyvi), FSxSTR("ne")) ||
                TaheHulgad::OnLopus(&(t->tyvi),FSxSTR("kindel")) ||
                TaheHulgad::OnLopus(&(t->tyvi),FSxSTR("rikas")))
                continue; // ...ega algvormis ja"relkomponent 
            }
        if (ad_hoc_v->lisatingimus == 2)
            {
            if (endingr( lgr, lopp_v ) == -1)
                continue; // nt. seis+vat != seis=ev+t 
            }
        if (ad_hoc_v->lisatingimus == 3)
            {
            if (endingr( lgr, lopp_v ) == -1) // nt. seis+vad != seis=ev+d 
                {
                if (endingr( GetLgNr(tyveinf, 0), lopp_v ) != -1)
                    { // kasva+vad -> k<asva=va+d
                    TaheHulgad::StrNCpy(&uusstr1, &(t->tyvi), 
                                (const FSxCHAR *)(TaheHulgad::lisaKr6nksudeStr));
// proovin ilma dptr-ta hakkama saada
// hjk 21.05.2002
//                    LgCopy(dptr, tyveinf, 1);
//                    LisaKdptr(dptr, uustyvi, uusstr1, 0 );
                    LisaKdptr(tyveinf, &uustyvi, &uusstr1, 0);
                    }
                else
                    continue;
                }
            else
                uustyvi = t->tyvi;
            }
        else
            uustyvi = t->tyvi;
        uustyvi += ad_hoc_v->uuele_tyvele_otsa;
        tul->Add((const FSxCHAR *)uustyvi, ad_hoc_v->uus_lp, FSxSTR(""), ad_hoc_v->uus_sl, ad_hoc_v->uus_vorm);
        }
    }

