
#include "etmrf.h"
#include "etmrfverstr.h"
#include "post-fsc.h"
#include "loefailist.h"

void ETMRFA::Start(const CFSString &path, const MRF_FLAGS_BASE_TYPE flags)
{
    if (EmptyClassInvariant() == false)
    {
        Stop();
    }
    CFSString pohiSonastikuPikkNimi, pohiSonastikuNimi;
    pohiSonastikuNimi = flags & MF_KR6NKSA
        ? FSTSTR("et.dct") /*FSTSTR("et.ks.dct")*/
        : FSTSTR("et.dct");
    CFSFileName ps, ls, is;

    if (Which(&pohiSonastikuPikkNimi, &path, &pohiSonastikuNimi) == false)
    {
        throw (VEAD(ERR_MORFI_PS6N, ERR_OPN, __FILE__, __LINE__, 
                            "Ei saanud põhisõnastiku avamisega hakkama"));
    }
    ps = pohiSonastikuPikkNimi;

    CFSString mrfusrdctpathname, mrfusrdctname;
    if (mrfusrdctname = FSTSTR("et.usr.dct"),
        Which(&mrfusrdctpathname, &path, &mrfusrdctname) == false)
    {
        if (mrfusrdctname = FSTSTR("et.usr.dct.utf8"),
            Which(&mrfusrdctpathname, &path, &mrfusrdctname) == false)
        {
            if (mrfusrdctname = FSTSTR("et.usr.dct.uc"),
                Which(&mrfusrdctpathname, &path, &mrfusrdctname) == false)
            {
                mrfusrdctpathname = FSTSTR("");
            }
        }
    }
    ls = mrfusrdctpathname;
    Start(flags, ps, ls);
    assert(ClassInvariant());
}

void ETMRFA::Start(const MRF_FLAGS_BASE_TYPE flags,
                   const CFSFileName& dctMain, const CFSFileName& dctUser)
{
    if (EmptyClassInvariant() == false)
        Stop();
    mrfFlags->Set(flags);
    MORF0::Start(&dctMain, &a);
    if (dctUser.IsEmpty() == false) // abisõnastiku nimi olemas
    {
        // Kui abisõnstikku ei leia, siis ei kasuta.
        // Selle puudumise üle ei pahanda
        MRFAUDCT::Start(dctUser); //jama korral throw();
    }
    assert(ClassInvariant());
}

void ETMRFA::SetMaxTasand(const int _maxTasand_)
{
    assert(ClassInvariant());
    maxTasand = _maxTasand_;
}

bool ETMRFA::Set(const FSXSTRING &buf)
{
    assert(ClassInvariant());
    typedef TMPLPTRARRAY<FSXSTRING> TMPLPTRARRAY_PCFSWS;
    TYKELDATUDPCFSSTRING<FSXSTRING, FSXSTRING, TMPLPTRARRAY_PCFSWS> tykid(buf,
                                                                          TaheHulgad::wWhiteSpace);
    bool ret = false;
    for (int i = 0; i < tykid.idxLast; i++)
    {
        if (mrfFlags->ChkB(MF_XML) == true)
        {
            int posLeft = 0;
            while ((posLeft = tykid[i]->Find((FSWCHAR) '<', posLeft)) >= 0)
            {
                int posRight;
                if ((posRight = tykid[i]->Find((FSWCHAR) '>', posLeft + 1)) >= 0)
                {
                    posLeft = posRight + 1; // märgendi samas sõnas, otsime sama
                    continue; // sõna seest järgmist alustavat
                }
                // märgendi jätkub peale tühikut, peab kokku tagasi tõstma
                int j;
                for (j = i + 1;; j++)
                {
                    if (j >= tykid.idxLast)
                        throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA,
                                   __FILE__, __LINE__, "$Revision: 1287 $",
                                   "XML-margend jookseb yle reapiiri");
                    *(tykid[i]) += FSWSTR(" ");
                    *(tykid[i]) += *(tykid[j]);
                    if ((posRight = tykid[i]->Find((FSWCHAR) '>', posLeft + 1)) > 0)
                    {
                        *(tykid[j]) = *(tykid[i]);
                        posLeft = posRight + 1;
                        i = j;
                        break; // otsime sabast veel märgendeid
                    }
                }
            }
        }
        tykid[i]->Trim();
        if(tykid[i]->GetLength()>0)
            ret |= Set1(*(tykid[i]));
    }
    return ret;
}

bool ETMRFA::Set1(const FSXSTRING& wstr)
{
    return Set1(new LYLI(wstr, SisendStrId(wstr)));
}

bool ETMRFA::Set1(LYLI &lyli)
{
    return Set1(new LYLI(lyli));
}

bool ETMRFA::Set1(LYLI *pLyli)
{
    a.AddPtr(pLyli);
    // jätame meelde kas oleme lause sees või lausest väljas
    if ((pLyli->lipp & PRMS_TAGBOS) == PRMS_TAGBOS)
        sisendisLausePooleli = true;
    else if ((pLyli->lipp & PRMS_TAGEOS) == PRMS_TAGEOS)
        sisendisLausePooleli = false;
    if (mrfFlags->ChkB(MF_XML) == true)
    {
        // XMLi korral lausest välja jäävaid sõnu ei analüüsi
        if (sisendisLausePooleli == false && (pLyli->lipp & PRMS_SONA) == PRMS_SONA)
            pLyli->lipp = PRMS_TAGSTR;
    }
    // loendame, mitu sõna analüüsimata
    if ((pLyli->lipp & PRMS_SONA) == PRMS_SONA)
        ++nSona;
    // ühestaja sisend peab olema lausestatud, teeme lause kaupa
    if (mrfFlags->ChkB(MF_YHESTA) == true)
        return sisendisLausePooleli == true ? false : true;
    else // ainult morf
        return nSona >= 3; // piisava varu korral saab tulemusi välja võtta
}

LYLI_FLAGS ETMRFA::SisendStrId(const CFSWString& wstr)
{
    if (mrfFlags->ChkB(MF_IGNOREBLK) == true)
    {
        // ignoreeri <ignoreeri> ... </ignoreeri> blokki
        if (ignoreBlokis == true) // ignoreeritavas blokis sees
        {
            if (wstr.Compare(FSWSTR("</ignoreeri>")) == 0)
                ignoreBlokis = false;
            return PRMS_TAGSTR; // on märgend või igmore-blokis olev tekst
        }
        if (ignoreBlokis == false) // pole ignoreeritavas blokis sees
        {
            if (wstr.Compare(FSWSTR("<ignoreeri>")) == 0)
            {
                // ignoreeritava bloki algus
                ignoreBlokis = true;
                return PRMS_TAGSTR; // on märgend
            }
        }
    }
    if (mrfFlags->ChkB(MF_IGNORETAG) == true || mrfFlags->ChkB(MF_XML) == true)
    {
        if (wstr[0] == FSWCHAR('<') && wstr[wstr.GetLength() - 1] == FSWCHAR('>'))
        {
            // kontrollime kas 1 märgend või mitu märgendit koos
            // nende vahele jääva sõnaga

            int posRight = wstr.Find((FSWCHAR) '>', 1) + 1;
            while (wstr[posRight] != 0) // '>' taga pole EOS
            {
                if (wstr[posRight] != (FSWCHAR) '<')
                    return PRMS_SONA; // märgend(id) sõnaga kokkukleepunud
                // järjekordse märgendi algus
                if ((posRight = wstr.Find((FSWCHAR) '>', posRight + 1)) < 0)
                    throw VEAD(ERR_X_TYKK, ERR_MINGIJAMA,
                               __FILE__, __LINE__, "$Revision: 1287 $",
                               "Vigane tippsulgude balanss");
                posRight++;
            }
            LYLI_FLAGS tagId;
            if (wstr == FSWSTR("<s>")) // lause algus
                tagId = PRMS_TAGBOS;
            else if (wstr == FSWSTR("</s>")) // lause lõpp
                tagId = PRMS_TAGEOS;
            else if (wstr == FSWSTR("<p>")) // lõigu algus
                tagId = PRMS_TAGBOP;
            else if (wstr == FSWSTR("</p>")) // lõigu lõpp
                tagId = PRMS_TAGEOP;
            else if (wstr == FSWSTR("<EOF/>")) // faili lõpp
                tagId = PRMS_TAGEOF;
            else if (wstr == FSWSTR("<EOP/>")) // lõiguvahe
                tagId = PRMS_TAGPSEP;
            else
                tagId = PRMS_TAGSTR; // mingi muu märgend           
            return tagId; // koosneb (ainult) märgendi(te)st
        }
    }
    return PRMS_SONA; // seda ei ignoreeri (pole märgend)
}

LYLI *ETMRFA::Get(void)
{
    if(mrfFlags->ChkB(MF_YHESTA) == true)
        return GetYhh();
    return GetMrf();  
}

LYLI *ETMRFA::GetMrf(void)
{
    assert(mrfFlags->ChkB(MF_MRF) == true || mrfFlags->ChkB(MF_SPELL));
    return nSona > 2 ? Flush() : NULL;  
}

LYLI *ETMRFA::GetYhh(void)
{
    assert(mrfFlags->ChkB(MF_YHESTA) == true);
    return FlushYhh(true); 
}

LYLI *ETMRFA::Flush(void)
{
    if(mrfFlags->ChkB(MF_YHESTA) == true)
        return FlushYhh(false);
    else
        return FlushMrf();
}

LYLI *ETMRFA::FlushYhh(bool lubaPoolikutLauset)
{
    assert(mrfFlags->ChkB(MF_YHESTA) == true);
    if(yhh.idxLast <= 0)        
    {   // ühestaja väljundahel tühi, katsume sinna morfist midagi leida
               
        // ots peal, morfist ei saanud ka midagi
        LYLI *pLyli = a.Lyli(0, A2_SUVALINE_LYLI);
        if(pLyli == NULL)
            return NULL;

        // väljajpoole lausemärgendeid peaksid jääma ainult TAGid
        // nood uhame niisama välja
        if((pLyli->lipp & PRMS_TAG)!=PRMS_TAG)
            throw VEAD(ERR_MORFI_MOOTOR, ERR_NOMEM, __FILE__, __LINE__, 
                                                "Valesti lausestatud sisend");
        // pole lause algusmärgend
        if((pLyli->lipp & PRMS_TAGBOS)!=PRMS_TAGBOS)
        {
            assert((pLyli->lipp & PRMS_TAG)==PRMS_TAG);
            return a.LyliPtrOut();// väljapool lausemärgendeid. aimnult TAGid
            //return FlushMrf();
        }
        // oli lausealgusmärgend, otsime üles esimese lauselõpumärgendi
        assert((pLyli->lipp & PRMS_TAGBOS)==PRMS_TAGBOS);
        int indeks;
        pLyli = a.Lyli(0, PRMS_TAGEOS, &indeks); 
        if(pLyli==NULL)
        {
            if(lubaPoolikutLauset == true)
                return NULL; // GetYhh-is lubame poolikut lauset
            // FlushYhh-is ei luba poolkut lauset
            throw (VEAD(ERR_MORFI_MOOTOR, ERR_NOMEM, __FILE__, __LINE__, 
                                                    "Lause lõpumärgend puudu"));
        }
        // korjame ühestaja väljundahelasse morf analüüsid lause 
        // algusmärgendist lõpumärgendini
        //assert(indeks>1);
        yhh.Start(indeks+1, 0);
        do  {
            pLyli = FlushMrf();
            assert(pLyli!=NULL);
            yhh.AddPtr(pLyli);            
        } while((pLyli->lipp & PRMS_TAGEOS)!=PRMS_TAGEOS);
        if (mrfFlags->ChkB(MF_LISAPNANAL)==true)
        {
            MargistaJustkuiLauseAlgused(yhh);
            LisaPNimeAnalyysid(yhh);
            //PANEFAILI out(PFSCP_UTF8); for(int i=0; i< yhh.idxLast; i++) out.Pane(yhh[i],MF_DFLT_MORFY|MF_YHELE_REALE);  //DB
        }
    }
    return yhh.LyliPtrOut(); 
}


LYLI *ETMRFA::FlushMrf(void)
{
    int idx;

    LYLI *pLyli = a.Lyli(0, A2_SUVALINE_LYLI, &idx);
    if (pLyli == NULL) // kui sisendahel tühi peab sõnade loendur olema nullis
    {
        assert(nSona == 0);
        assert(ClassInvariant());
        return NULL; // tühi
    }
    assert(nSona >= 0);

    if ((pLyli->lipp & PRMS_TAG) == PRMS_TAG) // TAG, seda ei morfa
    {
        return a.LyliPtrOut(idx); // Tõstame TAGi morfi sisendahelast mälu vabastamata välja
    }
    // vaja morfata
    assert((pLyli->lipp & PRMS_SONA) == PRMS_SONA);
    MRFTULEMUSED morfAnal;
    FSXSTRING sissePuhastatud(*pLyli->ptr.pStr);
    PuhastaXMList<FSXSTRING, FSWCHAR > (sissePuhastatud, mrfFlags->ChkB(MF_XML));
    assert(nSona > 0);
    if (MRFAUDCT::chkmin(pLyli->ptr.pStr, &sissePuhastatud, &morfAnal) == false) //polnud abisõnastikus; jama korral throw()
    {
        MORF0::chkmin(pLyli->ptr.pStr, &sissePuhastatud, &morfAnal, maxTasand); //vaatame põhisõnastikku
        if (morfAnal.on_tulem() == true) // suutis analüüsida
        {
            morfAnal.eKustTulemused = eMRF_AP; //TODO::kas ei tule juba chkmin()-ist

            // MF_LISAPNANAL lippu kasutab vaikimisi ainult ühestaja,
            // seda teeme omaette tsüklis peale morfi ja enne ühestamist
            //if (mrfFlags->Chk(MF_LISAPNANAL)) //arvestades asukohta lauses lisame
            //    LisaPNimeAnalyysid(&morfAnal); // vajadusel võimalikud pärisnime-analüüsid
        }
        else //ei suutnud põhisõnastiku baasil analüüsida
        {
            arvamin(&sissePuhastatud, &morfAnal); //katsume oletada
            morfAnal.eKustTulemused = eMRF_AO; //TODO::kas ei tule juba arvamin()-ist
        }
    }
    if (mrfFlags->ChkB(MF_YHMRG) == true) //lisame analüüsidele ühestajamärgendid
        FsTags2YmmTags(&morfAnal);
    if (mrfFlags->ChkB(MF_LEMMA) == true) //lisame analüüsidele lemmad
        morfAnal.LeiaLemmad();
    morfAnal.SortUniq();
    // Tõstame morfi lüli sisendahelast ahelast välja, mälu ei vabasta
    a.LyliPtrOut(idx);
    pLyli->Start(morfAnal, pLyli->lipp & PRMS_JUSTKUI_LAUSE_ALGUS ?
                 PRMS_MRF | PRMS_JUSTKUI_LAUSE_ALGUS : PRMS_MRF);
    assert(morfAnal.mitmeS6naline <= nSona);
    nSona -= morfAnal.mitmeS6naline; // vähendab loendajat...
    assert(ClassInvariant()); // ...analüüsitud sõnade võrra...
    return pLyli;
}

void ETMRFA::ArvestaValjundisLauseKonteksti(void)
{
    int idx;
    LYLI *pLyli = a.Lyli(0, A2_SUVALINE_LYLI, &idx);
    if (pLyli == NULL)
    {
        assert(nSona == 0);
        return; // tühi
    }
    // jätame meelde kas oleme lause sees või lausest väljas
    if ((pLyli->lipp & PRMS_TAGBOS) == PRMS_TAGBOS)
        valjundisLausePooleli = true;
    else if ((pLyli->lipp & PRMS_TAGEOS) == PRMS_TAGEOS)
        valjundisLausePooleli = false;
}

void ETMRFA::Clr(void)
{
    a.DelAll();
    yhh.DelAll();
    nSona = 0;
    sisendisLausePooleli = false;
    valjundisLausePooleli = false;
}

const char* ETMRFA::GetVerProg(void)
{
    return etMrfVersionString;
}

void ETMRFA::Stop(void)
{
    Clr();
    MRFAUDCT::Stop();
    MORF0::Stop();
}

ETMRFA::~ETMRFA(void)
{
    ETMRFA::Stop();
}

bool ETMRFA::EmptyClassInvariant(void)
{
    return
    maxTasand == 100
        && nSona == 0
        && MORF0::EmptyClassInvariant()
        && MRF2YH2MRF::EmptyClassInvariant()
        && MRFAUDCT::EmptyClassInvariant()
        ;
}

bool ETMRFA::ClassInvariant(void)
{
    bool ret =
        mrfFlags != NULL
        && a.ClassInvariant()
        && MORF0::ClassInvariant()
        && MRF2YH2MRF::ClassInvariant()
        //&& MRFAUDCT::ClassInvariant() // See ei pea olema avatud
        ;
    return ret;
}

//private
// kui suurtäheline sõna võiks olla tegelt lause alguses, nt. otseses kõnes, siis
// lyli->lipp |= PRMS_JUSTKUI_LAUSE_ALGUS; // ahela lülile lause algusmärgend külge

void ETMRFA::MargistaJustkuiLauseAlgused(AHEL2 &ahel, int lauseAlgusIdx)
{
    assert(mrfFlags->ChkB(MF_YHESTA) == true);
    if (mrfFlags->ChkB(MF_LISAPNANAL) == false)
        return; // pole vaja üldse rabeledagi
    int sonaNr = -1, indeks;
    LYLI *jooksev, *eelmine, *yle_eelmine;

    for (int idx = lauseAlgusIdx;
        (jooksev = ahel.Lyli(idx, A2_SUVALINE_LYLI)) != NULL &&
        (jooksev->lipp & PRMS_TAGEOS) != PRMS_TAGEOS; idx++)
    {
        if ((jooksev->lipp & PRMS_MRF) != PRMS_MRF)
            continue; // jätame vahele, kui ei ole morf analüüs
        ++sonaNr;
        MRFTULEMUSED *pMorfJooksev = jooksev->ptr.pMrfAnal;
        if (TaheHulgad::suurtht.Find(pMorfJooksev->s6na[0]) == -1) // ei alga suurega
            continue; // siis pole ka huvitav

        if (sonaNr == 0) // esimene sõna
        {
            jooksev->lipp |= PRMS_JUSTKUI_LAUSE_ALGUS;
            continue;
        }

        //eelmine = a.Lyli(sonaNr - 1, PRMS_MRF);
        if (sonaNr > 0) // eelnev sõna olemas
        {
            eelmine = ahel.LyliN(idx, -1, PRMS_MRF, &indeks);
            assert(indeks >= lauseAlgusIdx);
            MRFTULEMUSED *pMorfEelmine = eelmine->ptr.pMrfAnal;
            if ((*pMorfEelmine)[0]->sl == FSxSTR("Z")) // eelmine oli kirjavahemärk
            {
                if ((*pMorfEelmine)[0]->tyvi == FSxSTR(",")) // , on normaalne
                    continue;
                if ((*pMorfEelmine)[0]->tyvi == FSxSTR(";")) // ; on normaalne
                    continue;
                if ((*pMorfEelmine)[0]->tyvi == FSxSTR("."))
                {
                    int lyh = 0; // oletan, et . pole lühendi järgne

                    if (sonaNr > 1) // üle-eelmine sõna olemas
                    {
                        yle_eelmine = ahel.LyliN(idx, -2, PRMS_MRF, &indeks);
                        assert(indeks >= lauseAlgusIdx);
                        MRFTULEMUSED *pMorfYle_Eelmine = yle_eelmine->ptr.pMrfAnal;
                        for (int i = 0; i < pMorfYle_Eelmine->idxLast; i++)
                        {
                            if ((*pMorfYle_Eelmine)[i]->sl == FSxSTR("Y")) // lyhend .
                                lyh = 1;
                        }
                        if (lyh == 1) // lyhend . on normaalne
                            continue;
                    }
                }
                if ((*pMorfEelmine)[0]->tyvi == FSxSTR(".") ||
                    (*pMorfEelmine)[0]->tyvi == FSxSTR(")"))
                {
                    // võib-olla eespool pole muud kui numbrid vms
                    // mis tähistab loendi algust ?
                    int loend = 0; // oletan, et pole loendi algustähis
                    for (int i=-2; i+sonaNr >= 0; i--)
                    {
                        yle_eelmine = ahel.LyliN(idx, i, PRMS_MRF, &indeks);
                        assert(indeks >= lauseAlgusIdx);
                        if (yle_eelmine->ptr.pMrfAnal->s6na.SpanIncluding(FSxSTR("1234567890.()")) == yle_eelmine->ptr.pMrfAnal->s6na)
              //          if (TaheHulgad::PoleMuudKui((const CFSWString*)&(yle_eelmine->ptr.pMrfAnal->s6na), (const CFSWString*) &(FSxSTR("1234567890.()"))))
                            loend = 1;
                        else
                            loend = 0;
                    }
                    if (loend == 0) // eespool on (ka) midagi muud kui loendi tähis
                        continue;
                }
                jooksev->lipp |= PRMS_JUSTKUI_LAUSE_ALGUS;
            }
        }
    }
}

void ETMRFA::LisaPNimeAnalyysid(AHEL2 &ahel, int lauseAlgusIdx)
{
    assert(mrfFlags->ChkB(MF_YHESTA) == true);
    if (mrfFlags->ChkB(MF_LISAPNANAL) == false)
        return; // pole vaja üldse rabeledagi
    LYLI *pLyli;

    for (int idx = lauseAlgusIdx;
        (pLyli = ahel.Lyli(idx, A2_SUVALINE_LYLI)) != NULL &&
        (pLyli->lipp & PRMS_TAGEOS) != PRMS_TAGEOS; idx++)
    {
        if ((pLyli->lipp & PRMS_MRF) == PRMS_MRF)
            LisaPNimeAnalyys(*pLyli);
    }
}

void ETMRFA::LisaPNimeAnalyys(LYLI &lyli)
{
    if ((lyli.lipp & PRMS_MRF) != PRMS_MRF)
        return; // pole morf analüüs
    if (lyli.ptr.pMrfAnal->eKustTulemused != eMRF_AP)
        return; // analüüs ei tulnud põhisõnastikust
    if (mrfFlags->ChkB(MF_LISAPNANAL) == false)
        return;
    bool analyyseLisatud = false;
    MRFTULEMUSED *pMorfAnal = lyli.ptr.pMrfAnal;
    assert(pMorfAnal != NULL);
    int i, j, pik, viimane = pMorfAnal->idxLast;
    MRFTUL tmpMrfTul, *tmPtr, *mrfTul;
    int kriips, i1, i2;

    pik = pMorfAnal->s6na.GetLength();
    if (pik >= STEMLEN)
        return;
    if (TaheHulgad::suurtht.Find(pMorfAnal->s6na[0]) == -1)
        return; // ei alga suurega
    //if (TaheHulgad::AintSuuredjaNrjaKriipsud(&(pMorfAnal->s6na))) 
    //    continue;        // ainult suured ja nr ja kriipsud ongi
    // äkki on nt. Dudajevi-meelne ?

    i1 = pMorfAnal->s6na.ReverseFind((FSxCHAR) '-');
    i2 = pMorfAnal->s6na.ReverseFind((FSxCHAR) '/');
    kriips = i1 > i2 ? i1 : i2; // kriips on viimase - või / indeks
    if (kriips == pik) // sona-
        kriips = -1; // kriipsu olemasolu pole t�htis
    if (kriips != -1)
        if (TaheHulgad::suurtht.Find(pMorfAnal->s6na[kriips + 1]) == -1)
            return; // nt. Dudajevi-meelne
    if (kriips == -1) // kriipsuga sõnu nagu Vana-Kuuse siin ei kontrolli
    {
        for (i = 0; i < viimane && (*pMorfAnal)[i]->sl != LIIK_PARISNIMI; i++) //kontrollime kas juba pärisnime-analüüs olemas
            ;
        if (i < viimane)
        {
            assert((*pMorfAnal)[i]->sl == LIIK_PARISNIMI);
            return;
        }
        //{
        //mrfTul = (*pMorfAnal)[i];
        //if (mrfTul->sl == LIIK_PARISNIMI) // ongi
        //    continue;
        //}
    } //ei leidunud pärisnime-analüüsi
    // nud, tud _V_ sõnadele ja analoogil. liitsõnadele ei lisa pärisnime analüüsi 
    for (i = 0; i < viimane; i++)
    {
        mrfTul = (*pMorfAnal)[i];
        if (mrfTul->lopp == FSxSTR("nud") || mrfTul->lopp == FSxSTR("tud"))
            return;
        if (TaheHulgad::OnLopus(&(mrfTul->tyvi), FSxSTR("=nud")))
            return;
        if (TaheHulgad::OnLopus(&(mrfTul->tyvi), FSxSTR("=tud")))
            return;
        if (TaheHulgad::OnLopus(&(mrfTul->tyvi), FSxSTR("=dud")))
            return;
        FSXSTRING losona = mrfTul->tyvi;
        losona.MakeLower();
        if (TaheHulgad::PoleMuudKui(&losona, &(TaheHulgad::kaash)))
            return;
    }

    //vaatame, kas tuleks lisada
    FSXSTRING tmpsona = FSxSTR("X");
    FSXSTRING ette;
    ette = pMorfAnal->s6na.Left(kriips + 1); //
    tmpsona += pMorfAnal->s6na.Mid(kriips + 1);

    for (i = 0; i < viimane; i++)
    {
        mrfTul = (*pMorfAnal)[i];

        if (mrfTul->sl.FindOneOf(LIIK_KAANDSONA) == -1) // pole noomen
        {
            if ((lyli.lipp & PRMS_JUSTKUI_LAUSE_ALGUS))
                continue; // on lause alguses 
            if (TaheHulgad::AintSuuredjaNrjaKriipsud(&(pMorfAnal->s6na)))
                continue; // on läbiva suurtähega 
        }
        if (mrfTul->sl.FindOneOf(FSxSTR("PYN")) != -1)
            continue; // on ebatõenäoline pärisnimekandidaat 
        if (mrfTul->sl.FindOneOf(LIIK_SACU) != -1)
        { // oli Metsale    mets+le //_S_ sg all, //
            tmpMrfTul.Start(*mrfTul);
            TaheHulgad::AlgusSuureks(&(tmpMrfTul.tyvi));
            tmpMrfTul.sl = LIIK_PARISNIMI;
            analyyseLisatud = true;
            // nüüd on Metsale    Mets+le //_H_ sg all, //
            //tmpMrfTul'is oleva analüüsi lisamine-{{
            if ((tmPtr = pMorfAnal->AddClone(tmpMrfTul)) == NULL)
            {
                Clr();
                throw (VEAD(ERR_MORFI_MOOTOR, ERR_NOMEM, __FILE__, __LINE__, "$Revision: 1287 $"));
            }
        }
        // vaja veel oletada pärisnime analüüsi

        // kontr, kas Xsõna on mingi produktiivsesse muuttüüpi kuuluv sõna
        // näiteks XMetsale -> Metsa+le
        MRFTULEMUSED tulemus;
        if (Barvaww(&tulemus, &tmpsona, tmpsona.GetLength(), LIIK_PARISNIMI) == false)
            throw (VEAD(ERR_MORFI_MOOTOR,
                        ERR_NOMEM,
                        __FILE__, __LINE__, "$Revision: 1287 $"));
        if (tulemus.on_tulem() == false)
            continue;
        // vt kõiki tulemusi; igaühelt võta eest X maha...
        for (j = 0; j < tulemus.idxLast; j++)
        {
            if (tulemus[j]->tyvi[0] != (FSxCHAR) 'X') // seda ei saa olla...
                continue;
            tulemus[j]->tyvi = tulemus[j]->tyvi.Mid(1);
            TaheHulgad::AlgusSuureks(&(tulemus[j]->tyvi));
        }
        tulemus.LisaTyvedeleEtte((const FSxCHAR *) ette);
        // vt kõiki tulemusi; lisa sobivad siia õigesse struktuuri
        for (j = 0; j < tulemus.idxLast; j++)
        {
            // if (TaheHulgad::suurtht.Find(tulemus[j]->tyvi[0]) == -1)
            //    continue;   // ei alga suure tähega
            if (tulemus[j]->tyvi.Find(FSxSTR("=")) != -1) // tuletamine on siin kahtlane
                continue;
            analyyseLisatud = true;
            if ((tmPtr = pMorfAnal->AddClone(*(tulemus[j]))) == NULL)
            {
                Clr();
                throw (VEAD(ERR_MORFI_MOOTOR,
                            ERR_NOMEM,
                            __FILE__, __LINE__, "$Revision: 1287 $"));
            }
        }
    }
    if (analyyseLisatud == true)
    {
        if (mrfFlags->ChkB(MF_YHMRG) == true) //lisame analüüsidele ühestajamärgendid
            FsTags2YmmTags(pMorfAnal);
        if (mrfFlags->ChkB(MF_LEMMA) == true) //lisame analüüsidele lemmad
            pMorfAnal->LeiaLemmad();
        pMorfAnal->SortUniq();
    }
}

//TODO:: testi MRFAUDCT::Start() funktsiooni

void MRFAUDCT::Start(
                     const CFSFileName &dctFileName)
{
    VOTAFAILIST mrfusrdctfile;
    FSXSTRING rida;

    Stop();
    TMPLPTRARRAYSRT<MRFTULEMUSED>::Start(20, 20);
    PFSCODEPAGE codepage;
    switch (dctFileName[dctFileName.GetLength() - 1])
    {
    case FSTCHAR('8'):
        codepage = PFSCP_UTF8;
        break;
    case FSTCHAR('c'):
        codepage = PFSCP_UC;
        break;
    default:
        codepage = PFSCP_BALTIC;
        break;
    }
    mrfusrdctfile.Start(dctFileName, FSTSTR("rb"), codepage, NULL,
                        false, false, false);
    while (mrfusrdctfile.Rida(rida) == true)
    {
        MRFTULEMUSED tmp;
        rida.Trim();
        if (rida.GetLength() <= 0)
            continue; //"^$" - ignoreeri tühje ridasid
        if (rida[0] == (FSWCHAR) '#' && rida[1] == (FSWCHAR) ' ' && rida[2] != (FSWCHAR) ' ')
            continue; // "^# [^ ].*$" - ignoreeri kommentaare
        try
        {
            tmp.Strng2Strct(&rida);
        }
        catch(VEAD &viga)
        {
            TMPLPTRARRAYSRT<MRFTULEMUSED>::Stop();
            throw VEAD(ERR_MORFI_LS6N,ERR_ROTTEN, viga.file, viga.line, 
                       "Vigane kasutajasõnastik", viga.msg, viga.msgBuf.w);
        }
        assert(tmp.ClassInvariant());
        AddClone(tmp);
    }
    Sort();
}

//TODO:: testi MRFAUDCT::chkmin() funktsiooni

bool MRFAUDCT::chkmin(
                      const FSXSTRING *sisse,
                      const FSXSTRING* sissePuhastatud,
                      MRFTULEMUSED *tul)
{
    MRFTULEMUSED *tulAbi;
    FSXSTRING sona, sonaTrimmitud, sonaPisi, sonaPisiTrimmitud;
    sona = *sissePuhastatud;
    TaheHulgad::AsendaMitu(&sona, TaheHulgad::uni_kriipsud,
                           TaheHulgad::amor_kriipsud);

    if ((tulAbi = Get(&sona)) == NULL) //polnud esialgsel kujul
    {
        //proovime ilma ees&tagasodita
        sonaTrimmitud = sona;
        sonaTrimmitud.TrimLeft(TaheHulgad::s_punktuatsioon);
        sonaTrimmitud.TrimRight(TaheHulgad::punktuatsioon);
        if (sonaTrimmitud == sona || (tulAbi = Get(&sonaTrimmitud)) == NULL)
        {
            sonaPisi = sona;
            sonaPisi.MakeLower();
            if (sonaPisi != sona)
            {
                //sisaldas suurt�hte(sid), proovime väiketähelisena
                if ((tulAbi = Get(&sonaPisi)) == NULL)
                {
                    if (sonaTrimmitud != sona)
                    {
                        //proovime veel väiketäheliseks tehtut ilma ees&tagasidita
                        sonaPisiTrimmitud = sonaPisi;
                        sonaPisiTrimmitud.TrimLeft(TaheHulgad::s_punktuatsioon);
                        sonaPisiTrimmitud.TrimRight(TaheHulgad::punktuatsioon);
                        tulAbi = Get(&sonaPisiTrimmitud);
                    }
                }
            }
        }
    }
    tul->DelAll();
    if (tulAbi == NULL) //polnud lisasõnastkus
    {
        tul->s6na = FSWSTR("");
        tul->tagasiTasand = 0;
        tul->mitmeS6naline = 1;
        tul->keeraYmber = false;
        tul->eKustTulemused = eMRF_XX;
        return false;
    }
    //saime lisasõnastikust
    tul->Start(*tulAbi);
    //tul->s6na=*sisse;
    tul->s6na = *sisse;
    tul->tagasiTasand = 0;
    tul->mitmeS6naline = 1;
    tul->keeraYmber = false;
    tul->eKustTulemused = eMRF_AL; // analüüsid lisasõnastikust
    return true;
}
