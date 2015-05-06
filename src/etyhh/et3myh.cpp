#include <assert.h>
#include <stdio.h>

#include "post-fsc.h"
#include "etmrf.h"
#include "ahel2.h"
#include "tmplarray.h"
#include "loefailist.h"

#include "t3common.h"

void ET3UTF8AHEL::Start(const MRF_FLAGS_BASE_TYPE _flags_, const CFSFileName& dctName)
{
    assert(EmptyClassInvariant() == true);
    flags.Start(_flags_);
    meta.Start(dctName);
    int i;

    // ühestamismärgendite loend ühestaja andmefailist
    meta.Seek(DCTELEMID_T3TAGS);
    if (meta.ReadUnsigned<UB4, int>(&i) == false)
        throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    tags.Start(i, 0);
    for (i = 0; i < tags.idxMax; i++)
    {
        CFSAString* tag = tags.AddPlaceHolder();
        if (meta.ReadString(tag) == false)
            throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    }
    assert(tags.idxMax == tags.idxLast);
    // ühestamismärgendite esinemisarvud ühestaja andmefailist
    gramm1.Start(tags.idxMax);
    for (i = 0; i < gramm1.maxIdx1; i++)
    {
        if (meta.ReadUnsigned<UB4, int>(&(gramm1.Obj(i))) == false)
            throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    }
    
    // N-grammid ühestaja andmefailist
    meta.Seek(DCTELEMID_T3GRAMS);
    tabel.Start(tags.idxLast, tags.idxLast, tags.idxLast);
    for (int i1 = 0; i1 < tags.idxLast; i1++)
    {
        for (int i2 = 0; i2 < tags.idxLast; i2++)
        {
            for (int i3 = 0; i3 < tags.idxLast; i3++)
            {
                if (meta.ReadBuffer(&(tabel.Obj(i3, i1, i2)), sizeof (UKAPROB)) == false)
                    throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
            }
        }
    }

    // leksikon ühestaja andmefailist
    meta.Seek(DCTELEMID_T3LEX_WLST);
    if (meta.ReadUnsigned<UB4, int>(&i) == false)
        throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    lexArr.Start(i, 0);
    for (i = 0; i < lexArr.idxMax; i++)
    {
        LEXINF* lexInf = lexArr.AddPlaceHolder();
        if (meta.ReadUnsigned<UB4, int>(&(lexInf->n)) == false)
            throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
        if (meta.ReadString(&(lexInf->str)) == false)
            throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    }
    for (i = 0; i < lexArr.idxLast; i++)
    {
        meta.Seek2Pos(lexArr[i]->n);
        meta.ReadUnsigned<UB1, int>(&(lexArr[i]->n));
        assert(lexArr[i]->n > 0 && lexArr[i]->n < 15);
        lexArr[i]->tagIdxProb = new LEXINF::LEXINFEL[lexArr[i]->n];
        for (int j = 0; j < lexArr[i]->n; j++)
        {
            if (meta.ReadUnsigned<UB1, int>(&(lexArr[i]->tagIdxProb[j].tagIdx)) == false)
                throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
            if (meta.ReadBuffer(&(lexArr[i]->tagIdxProb[j].tagProb), sizeof (UKAPROB)) == false)
                throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
        }
    }

    // mitmesusklassid ühestaja andmefailist
    meta.Seek(DCTELEMID_T3M_KLASSID);
    int nKlassi;
    if (meta.ReadUnsigned<UB4, int>(&nKlassi) == false)
        throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
    mKlassid.Start(nKlassi, 0);
    assert(nKlassi == mKlassid.idxMax);
    for (i = 0; i < mKlassid.idxMax; i++)
    {
        int n;
        MKLASS* mk = mKlassid.AddPlaceHolder();
        if (meta.ReadUnsigned<UB1, int>(&n) == false)
            throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
        mk->Start(n);
        for (n = 0; n < mk->n; n++)
        {
            if (meta.ReadUnsigned<UB1, int>(&(mk->tagIdxProb[n].tagIdx)) == false)
                throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
            if (meta.ReadBuffer(&(mk->tagIdxProb[n].tagProb), sizeof (UKAPROB)) == false)
                throw VEAD(ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
        }
        assert(i < 1 || mKlassid[i - 1]->Compare(mKlassid[i]) < 0);
    }
    // lippude sättimine
    mitmesusKlassidesIgnoreeeri = SONA_ON_HARULDANE;
    mitmesusKlassKasutu = flags.ChkB(T3_MK_KASUTU);
    lexProbKasutu = flags.ChkB(T3_LEXPKASUTU);
}

void ET3UTF8AHEL::Run(AHEL2_UTF8& analyysid)
{
    int i, j;
    
    // Leiame morf analüüside==sõnade tegeliku arvu ahelas.
    // analyysid.idxLast-nSona==tag'ide arv massiivis analyysid
    int nSona;
    for (nSona = 0, i = 0; i < analyysid.idxLast; i++)
    {
        if (analyysid[i]->lipp & PRMS_MRF)
            nSona++;
    }
    if (nSona <= 0)
        return;
    
    // Leiutame iga sõna jaoks tema ühestamismärgendite tõenäosused
    // sõnede arv lauses * märgendite arv
    SA2<UKAPROB> sProb(-UKAPROBMAX, nSona, tags.idxLast);
    for (i = 0; i < nSona; i++)
    {
        MRFTULEMUSED_UTF8* m = analyysid.Lyli(i, PRMS_MRF)->ptr.pMrfAnal;
        assert(m != NULL);

        // Asendame mitmesõnalistes tühiku alakriipsuga, 
        // sest leksikonis on nad alakriipsuga
        CFSAString sona(m->s6na);
        PuhastaXMList<CFSAString, char>(sona, flags.ChkB(MF_XML));
        sona.Replace(" ", "_", CFSAString::REPLACE_ALL);
        LEXINF* lexInf = lexArr[&sona];
MORFI_BAASIL:
        if (lexProbKasutu == true || lexInf == NULL)
        {
            // ei tohi kasutada leksikonis vormi küljes olevaid tõenäosusi 
            // või ei olnud leksikonis

            // Leiame tuntud märgendite arvu ja indeksid
            TMPLPTRARRAYBIN<BASIC_TYPE_WITH_CMP<int>, int> tagIdxArr(m->idxLast, 0);
            bool oliTuttavaid = false;
ARVUTA_INDEKSID:
            for (j = 0; j < m->idxLast; j++)
            {
                int tagIdx = tags.GetIdx(&((*m)[j]->mrg1st));
                if (tagIdx >= 0)
                {
                    oliTuttavaid = true;
                    BASIC_TYPE_WITH_CMP<int>* tagIdxObj = tagIdxArr.AddPlaceHolder();
                    tagIdxObj->obj = tagIdx;
                }
            }
            if (oliTuttavaid == false)
            {
                // Polnud ühtegi tuttavat ühestamismärgendit, keerame kõik X'ideks.
                for (int j = 0; j < m->idxLast; j++)
                    // NB! Eeldame, et X on kindlasti ühestamismärgendite loendis.
                    (*m)[j]->mrg1st = "X";
                goto ARVUTA_INDEKSID;
            }
            tagIdxArr.SortUniq();

            MKLASS* mKlass = mKlassid.Get(&tagIdxArr);
            if (mitmesusKlassKasutu == false && mKlass != NULL)
            {
                // Tõenäosused leia varemarvutatud mitmesusklassidest.
                for (j = 0; j < mKlass->n; j++)
                    sProb.Obj(i, mKlass->tagIdxProb[j].tagIdx) =
                    mKlass->tagIdxProb[j].tagProb;
                mkLexiBaasil++; // mitmesusklass on arvutatud leksikoni baasil
            }
            else if (flags.ChkB(T3_MK_JAOTUSB) == false)
            {
                assert(mitmesusKlassKasutu == true || mKlass == NULL);
                // Kui leksikoni põhjal tehtud mitmesusklasse ei tohi kasutada
                // või ei leidnud sellist mitmesusklassi, 
                // pane kõigile võrdsed tõenäosused.
                // {P(m[i])=log(1/N)|i=0,...,N-1}
                assert(mitmesusKlassKasutu == true || mKlass == NULL);
                UKAPROB prob = (UKAPROB) (log(1.0 / (double) (tagIdxArr.idxLast)));
                for (int j = 0; j < tagIdxArr.idxLast; j++)
                    sProb.Obj(i, tagIdxArr[j]->obj) = prob;

                mkKoikVordsed++; //mitmesusklass laest, kõik võrdseks
            }
            else
            {
                assert(flags.ChkB(T3_MK_JAOTUSB) == true &&
                       (mitmesusKlassKasutu == true || mKlass == NULL));
                // arvutame mitmesusklassi tõenäosused lähtudes
                // sinna kuuluvat märgendite esimesarvust korpuses
                // {P(m[i]=log(cnt(m[i])/(cnt(m[0])+...+cnt(m[N-1]))/cnt(m[i])))|i=0,...,N-1}
                int sagKokku = 0;
                for (j = 0; j < tagIdxArr.idxLast; j++)
                    sagKokku += gramm1.Obj(tagIdxArr[j]->obj);

                double kokku = (double) sagKokku;
                for (int j = 0; j < tagIdxArr.idxLast; j++)
                    sProb.Obj(i, tagIdxArr[j]->obj) =
                        log((double) (gramm1.Obj(tagIdxArr[j]->obj)) / kokku);
            }
            assert(tagIdxArr.idxLast > 0);
            assert(m->idxLast >= tagIdxArr.idxLast);
        }
        else // sõnavorm oli leksikonis
        {
            assert(lexInf != NULL);
            for (j = 0; j < lexInf->n; j++)
            {
                int k;
                // leksikonist saadud üh-märgend
                CFSAString* marg = tags[lexInf->tagIdxProb[j].tagIdx];
                // kontrollime, et leksikonist saadud üh-märgend oleks 
                // morfist saadute hulgas
                for (k = 0; k < m->idxLast &&
                    marg->Compare((const char*) ((*m)[k]->mrg1st)) != 0; k++)
                    ;
                if (k >= m->idxLast)
                {
                    // leksikonist tuli selline anlüüs, mida morfist saadud 
                    // analüüside seas polnud võtame analüüsid morfist ja 
                    // tõenäosused mitteühesusklassidest
                    lexInf = NULL;
                    goto MORFI_BAASIL;
                }
            }
            // Leksikonist saadud analüüsid olid morfist saadud analüüside alamhulk
            lexCntK++;
            for (j = 0; j < lexInf->n; j++)
                sProb.Obj(i, lexInf->tagIdxProb[j].tagIdx) = lexInf->tagIdxProb[j].tagProb;
            mkLexiVormist++;
        }
        assert(m->idxLast > 0);
    }

    // Leiutame parima ühestamismärgendite kombinatsiooni selle lause jaoks
    SA3<UKAPROB> a(2, tags.idxLast, tags.idxLast);
    SA3<int> b(sProb.maxIdx1, tags.idxLast, tags.idxLast);
    UKAPROB maxa;
    UKAPROB ba = -UKAPROBMAX;
    int bi = 1, bj = 1;
    int k, l, cai, nai = 0;

    // massiivi a osaline initsialiseerimine
    for (j = 0; j < tags.idxLast; j++)
    {
        for (k = 0; k < tags.idxLast; k++)
        {
            a.Obj(0, j, k) = -UKAPROBMAX;
        }
    }
    a.Obj(0, 0, 0) = 0.0;
    maxa = 0.0;
    for (i = 0; i < sProb.maxIdx1; i++) // tsükkel üle lause sõnade
    {
        UKAPROB uusMaxa = -UKAPROBMAX;

        cai = i % 2;
        nai = (cai == 0 ? 1 : 0);

        // initsialiseeri järgmine veerg
        for (j = 0; j < tags.idxLast; j++)
        {
            for (k = 0; k < tags.idxLast; k++)
            {
                a.Obj(nai, j, k) = -UKAPROBMAX;
            }
        }
        maxa = -UKAPROBMAX;
        for (l = 0; l < tags.idxLast; l++)
        {
            UKAPROB sprob = sProb.Obj(i, l);
            if (sprob == -UKAPROBMAX)
            {
                continue;
            }
            for (j = 0; j < tags.idxLast; j++)
            {
                UKAPROB *aprob = &a.Obj(cai, j, 0);
                UKAPROB *tabelprob = &tabel.Obj(l, j, 0);
                for (k = 0; k < tags.idxLast; k++)
                {
                    UKAPROB prob;
                    if (aprob[k] < maxa)
                    {
                        continue;
                    }
                    prob = aprob[k] + tabelprob[k] + sprob;
                    if (prob > a.Obj(nai, k, l))
                    {
                        a.Obj(nai, k, l) = prob;
                        b.Obj(i, k, l) = j;
                        if (prob > uusMaxa)
                        {
                            uusMaxa = prob;
                        }
                    }
                }
            }
        }
        maxa = uusMaxa;
    }
    for (i = 0; i < tags.idxLast; i++)
    {
        for (j = 0; j < tags.idxLast; j++)
        {
            UKAPROB prob = a.Obj(nai, i, j) + tabel.Obj(0, i, j);
            if (prob > ba)
            {
                ba = prob;
                bi = i;
                bj = j;
            }
        }
    }

    // Kombunnime kokku massiivi parimatest märgenditest.
    // Esimene on viimase, teine eelviimase jne sõna märgend.
    TMPLPTRARRAY<PCFSAString> parimad(sProb.maxIdx1);
    for (i = sProb.maxIdx1 - 1; i >= 0; i--)
    {
        int temp = b.Obj(i, bi, bj);
        PCFSAString* mrg = tags[bj];
        assert(mrg != NULL);
        parimad.AddClone(*mrg);

        bj = bi;
        bi = temp;
    }

    assert(nSona == sProb.maxIdx1);
    for (i = 0; i < nSona; i++)
    {
        // Viskame morf analüüsidest valed märgendid välja
        MRFTULEMUSED_UTF8 &m = *(analyysid.Lyli(i, PRMS_MRF)->ptr.pMrfAnal);
        assert(&m != NULL);
        assert(m.idxLast > 0);
        for (j = m.idxLast - 1; j >= 0; j--)
        {
            if (parimad[nSona - 1 - i]->Compare(&(m[j]->mrg1st)) != 0)
                m.Del(j);
        }        
        // järjestame ja kustutame korduvad analüüsid
        m.SortUniq();
        assert(m.idxLast > 0);
    }


}

void ET3UTF8AHEL::Stop(void)
{
    flags.Stop();
    tags.Stop();
    tabel.Stop();
    lexArr.Stop();
    mKlassid.Stop();
    meta.Stop();
    InitClassVariables();
}

void ET3UTF8AHEL::DBLexJaMorf(const MRFTULEMUSED_UTF8* m, const LEXINF* lexInf)
{
    //PANEFAILI   out(FSTSTR("et3myh.db1.txt"), FSTSTR("wb"),PFSCP_UTF8);
}

//-------------------------------------------------------------------------

void ET3::Start(const MRF_FLAGS_BASE_TYPE flags, const CFSFileName& dctT3)
{
    assert(EmptyClassInvariant());
    ahelMyh.Start(0, 20);
    ET3UTF8AHEL::Start(flags, dctT3);
    if (ET3UTF8AHEL::flags.ChkB(MF_XML) == false)
        lauses = true;
    assert(ClassInvariant());
}

bool ET3::Set1(LYLI &lyli)
{ // sisendisse koopia
    assert(ClassInvariant());
    assert(jubaYhestatud == false);
    return Set1(new LYLI_UTF8(lyli)); // UC --> utf8
}

bool ET3::Set1(LYLI_UTF8 &lyli)
{ // sisendisse koopia
    assert(jubaYhestatud == false);
    return Set1(new LYLI_UTF8(lyli));
}

bool ET3::Set1(LYLI_UTF8 *pLyli)
{ // sisendisse viidatud lüli 
    assert(pLyli != NULL);
    assert(jubaYhestatud == false);
    ahelMyh.AddPtr(pLyli);
    return ArvestaLauseKonteksti(*pLyli);
}

LYLI *ET3::Flush(void)
{
    LYLI *pLyli = new LYLI();
    try
    {
        if (Flush(*pLyli) == true)
            return pLyli;
        delete pLyli;
        return NULL;
    }
    catch (...)
    {
        delete pLyli;
        throw;
    }
}

bool ET3::Flush(LYLI& lyli)
{
    if (lauses == true)
        return NULL;
    if (jubaYhestatud == false)
    {
        Yhesta();
        jubaYhestatud = true;
    }
    if (ahelMyh.idxLast <= 0)
    {
        jubaYhestatud = false;
        return NULL;
    }
    VIIDAKEST<LYLI_UTF8> p(ahelMyh.LyliPtrOut(0));
    if (p.ptr == NULL)
        return false;
    lyli = *p.ptr;
    return true;
}

void ET3::Clr(void)
{
    ahelMyh.DelAll();
    jubaYhestatud = false;
    lauses = false;
}

void ET3::Stop(void)
{
    ahelMyh.Stop();
    ET3UTF8AHEL::Stop();
    InitClassVariables();
}

bool ET3::ArvestaLauseKonteksti(LYLI_UTF8 &lyli)
{
    if ((lyli.lipp & PRMS_TAGBOS) == PRMS_TAGBOS)
        lauses = true;
    else if ((lyli.lipp & PRMS_TAGEOS) == PRMS_TAGEOS)
        lauses = false;
    return !lauses;
}

void ET3::Yhesta(void)
{
    ET3UTF8AHEL::Run(ahelMyh);
}

