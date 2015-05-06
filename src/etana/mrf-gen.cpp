#include "etmrf.h"
#include "tmk2t.h"

//-----------------------

bool ETMRFAS::Set(
    const FSXSTRING &wstr
    )
    {
    if(mrfFlags->ChkB(MF_GENE)==false)
        return ETMRFA::Set(wstr);  // morf analüüs
    else
        return ETMRFAS::Set1(wstr); // morf süntees
    }

bool ETMRFAS::Set1(const FSXSTRING &wstr)
    {
    if(mrfFlags->ChkB(MF_GENE)==false)
        return ETMRFA::Set1(wstr);
    // süntees
    FSXSTRING trimmitud(wstr);
    trimmitud.Trim();
    if(trimmitud.GetLength()<=0)
        return false;

    LYLI_FLAGS tagId=SisendStrId(trimmitud);
    aGene.LisaSappa<FSXSTRING>(trimmitud, tagId);
    return true; // süntees alati ühekauapa
    }

bool ETMRFAS::Set1(LYLI &lyli)
{
    if(mrfFlags->ChkB(MF_GENE)==true)
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    return ETMRFA::Set1(lyli);
}
    
bool ETMRFAS::Set1(LYLI *pLyli)
{
    if(mrfFlags->ChkB(MF_GENE)==true)
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    return ETMRFA::Set1(pLyli);
}

LYLI *ETMRFAS::Get(void)
    {
    if(mrfFlags->ChkB(MF_GENE)==false)
        return ETMRFA::Get();
    // läheb genetamiseks
    return ETMRFAS::Flush();
    }

LYLI *ETMRFAS::Flush(void)
    {
    if(mrfFlags->ChkB(MF_GENE)==false)
        return ETMRFA::Flush(); //analüüs

    // läheb sünteesiks
    FSXSTRING gTyvi, gKigi, gSl, gVormid;
    FSXSTRING gnaidis;  // sõna, mis peaks genetavas paradigmas olema, nt palk puhul palgi või palga
    int pos3;
    int pos1, pos2;
    MRFTULEMUSED geneOut;
    int idx;
    LYLI* tmpGeneLyliPtr=aGene.Lyli(0,A2_SUVALINE_LYLI,&idx);
    if(tmpGeneLyliPtr==NULL)
        return NULL; // ei saanud ahelast midagi
    // saime ahelast midagi...
    if((tmpGeneLyliPtr->lipp & PRMS_SONA)!=PRMS_SONA)// Kui pole lemme+vorm (on TAG vms)...
        return aGene.LyliPtrOut(idx); //...tõstame mälu vabastamata ahelast välja
                                      // ja anname genemata tagasi
    // lemma+vorm, tuleb geneda
    // jätame ta esialgu sünteesiahelasse ja teeme seal mida vaja
    geneStr=*(tmpGeneLyliPtr->ptr.pStr); //seda hakkame genema: 'tüvi' //_sl_ vormid//kigi'
    if(geneStr.GetLength() <= 0)
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    geneStr.Trim();
    if((pos1=geneStr.Find(FSxSTR(" //_"))) <= 0)
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    gTyvi=geneStr.Left(pos1);
    // näidise olemasolu puhuks
    pos2 = gTyvi.Find(FSxSTR(" ("));
    pos3 = gTyvi.Find(FSxSTR(")"));
    if (pos2 != -1 && pos3 > pos2+4 && pos3==gTyvi.GetLength()-1) // näidis leitigi
        {
        gnaidis = gTyvi.Mid(pos2+2, pos3-pos2-2);
        gTyvi=geneStr.Left(pos2);
        }
    if(geneStr.GetLength() < pos1+5 || geneStr[pos1+5]!=(FSxCHAR)'_')
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    gSl=geneStr.Mid(pos1+4,1);
    if((pos2=geneStr.Find(FSxSTR(" //"), pos1+5))<=0)
        throw(VEAD(ERR_GEN_MOOTOR,ERR_ARGVAL,__FILE__,__LINE__));
    if(pos1+5 < pos2)
        {
        gVormid=geneStr.Mid(pos1+6, pos2-pos1-6);
        gVormid.Trim();
        }
    // else vormid==""
    gKigi=geneStr.Mid(pos2+3, geneStr.GetLength()-pos2-3);
    gKigi.Trim();

    //if(Synt1(geneOut, &gTyvi, &gSl, &gVormid, &gKigi)==false)
    if(SyntDetailne(geneOut, &gTyvi, &gnaidis, &gSl, &gVormid, &gKigi)==false)
        {
        // jama või ei õnnestunud sünteesida
        }
    tmpGeneLyliPtr->Start(geneOut, PRMS_MRF);
    geneStr=FSxSTR("\0");
    return aGene.LyliPtrOut(idx); // tõstame genetud asjaga lüli
                                  // mälu vabastamata ahelast välja
    }

void ETMRFAS::Clr(void)
    {
    ETMRFA::Clr();
    aGene.DelAll();
    geneStr=FSxSTR("\0");
    //delete retGeneLyliPtr;
    //retGeneLyliPtr=NULL;
    }

bool ETMRFAS::Synt(MRFTULEMUSED &valja, const MRFTUL &sisse, const FSXSTRING naidis)
    {
    // sünteesime nõutud vormid, prr kasutab seda
    return SyntDetailne(valja, &sisse.tyvi, &naidis, &sisse.sl, &sisse.vormid,
                                                                    &sisse.kigi);
    }

// endine synt1 HJK 04.04.2014

bool ETMRFAS::SyntDetailne(      
    MRFTULEMUSED   &valja,
    const FSXSTRING  *pGeneSona,
    const FSXSTRING  *pnaidis,
    const FSXSTRING  *pGeneLiik,
    const FSXSTRING  *pGeneVormid,
    const FSXSTRING  *pGeneKigi)
    {
    assert(&valja!=NULL && pGeneSona!=NULL && pnaidis!=NULL && pGeneVormid!=NULL && pGeneKigi!=NULL);
    //MRFTULEMUSED *mrfTul;
    int n;

    valja.Stop();
    valja.Start(5,5);

    valja.s6na  = *pGeneSona;
    if (pnaidis->GetLength() > 0)
    {
        valja.s6na += FSxSTR(" (");
        valja.s6na += *pnaidis;
        valja.s6na += FSxSTR(")");
    }
    valja.s6na += FSxSTR(" //_");
    valja.s6na += *pGeneLiik;
    valja.s6na += FSxSTR("_ ");
    valja.s6na += *pGeneVormid;
    valja.s6na += FSxSTR(" // ");
    valja.s6na += *pGeneKigi;

    adHocString=FSxSTR("");
    valja.eKustTulemused = eMRF_XX; // see peaks tegelt olema pValja tekitamise kohas... HJK aprill 2005
                                    // Ei. See ütleb, et vaikimisi me ei tea kust analüüs pärit.
                                    // Seal, kus me tulemuse saime, asendame selle
                                    // konstandiga, kust tulemus tegelikult tuli.
                                    // Nii et päeva lõpuks peaks olema eMRF_XX asemel
                                    // midagi muud. Aga igaks juhuks initsialiseerime
                                    // ta selliselt. 
    MRF_FLAGS_BASE_TYPE geneLipud = mrfFlags->Get();
    FSXSTRING mrfAnal;
    // vaja morfida, kusjuures liiga pikad oleksid valed ja lühendeid üldse ei oleta
    mrfFlags->On(MF_MRF|MF_PIKADVALED|MF_LYHREZH);
    mrfFlags->Off(MF_KR6NKSA);
    // tsükeldame üle tyhikuga eraldet sonade
    // (ei tea kas seda tegelikult kunagi juhtub ka?)
    int vasak=0, parem=0;
    FSXSTRING GeneSona1, tmp;
    n = 0;
    tmp = *pGeneSona;
    tmp.Trim();
    for (; tmp.GetLength() > 0; tmp = tmp.Mid(vasak))
        {
        parem = tmp.Find((FSxCHAR)' ');
        if (parem == -1)
            parem = tmp.GetLength(); // viimase lõpus polnud tyhikut
        GeneSona1=tmp.Left(parem);
        GeneSona1.Trim(); // igaks juhuks, kes kurat teab
        vasak=parem+1;
        ETMRFA::Set1(GeneSona1); // morfi magasini
        n++;
        }
    LYLI morfistLyli;   
    if(ETMRFA::Flush(morfistLyli)==false) // morfi magasinist
        {
        ETMRFA::Clr();
        mrfFlags->Set(geneLipud); // taastame endised lipud
        return false;
        }
    assert( morfistLyli.lipp & PRMS_MRF );
   // mrfTul=morfistLyli.ptr.pMrfAnal;
    if(morfistLyli.ptr.pMrfAnal->on_tulem()) // õnnestus analüüsida
        {
        if(morfistLyli.ptr.pMrfAnal->mitmeS6naline != n)
            {
            // pole õige mitmesõnaline
            //delete pLyli;
            ETMRFA::Clr();
            mrfFlags->Set(geneLipud); // taastame endised lipud
            return false;
            }
        }
    if (a.idxLast != 0) 
        {
        // nt. taheti geneda mitmesõnalist, aga seda ei õnnestunud analüüsida
        //delete pLyli;
        ETMRFA::Clr();
        mrfFlags->Set(geneLipud); // taastame endised lipud
        return false;
        }
    mrfFlags->Set(geneLipud); // taastame endised lipud
    if(morfistLyli.ptr.pMrfAnal->on_tulem()) // õnnestus analüüda
        {
        bool rs;
        //mrfTul=morfistLyli.ptr.pMrfAnal;
        FSXSTRING gv = *pGeneVormid;
        gv.Trim();
        if(gv==FSWSTR("*,"))
            {
            gv= FSWSTR("adt, b, d, da, des, ge, gem, gu, ")
                FSWSTR("ks, ksid, ksime, ksin, ksite, ")
                FSWSTR("ma, maks, mas, mast, mata, me, ")
                FSWSTR("n, neg, neg ge, neg gem, neg gu, neg ks, neg nud, neg nuks, neg o, neg vat, ")
                FSWSTR("nud, nuks, nuksid, nuksime, nuksin, nuksite, nuvat, ")
                FSWSTR("o, pl ab, pl abl, pl ad, pl all, pl el, pl es, ")
                FSWSTR("pl g, pl ill, pl in, pl kom, pl n, pl p, pl ter, pl tr, ")
                FSWSTR("s, sg ab, sg abl, sg ad, sg all, sg el, sg es, sg g, sg ill, sg in, sg kom, ")
                FSWSTR("sg n, sg p, sg ter, sg tr, ")
                FSWSTR("sid, sime, sin, site, ")
                FSWSTR("ta, tagu, taks, takse, tama, tav, tavat, te, ti, tud, tuks, tuvat, v, vad, vat,");
            }
        rs = Gene2Detailne(&valja, morfistLyli.ptr.pMrfAnal, pnaidis, pGeneLiik, &gv, pGeneKigi);
        if (rs == false)
            return false;
        if (valja.idxLast > 0) // õnnestus sünteesida
            return true;
        // ei suutnud sünteesida ...
        if (morfistLyli.ptr.pMrfAnal->eKustTulemused == eMRF_AP) // tulemus põhisõnastikust
            { // ilmselt oli sisendsõna mingi tuntud sõna mitte-algvorm
            if (morfistLyli.ptr.pMrfAnal->s6na.Right(3) == FSxSTR("nud") ||
                morfistLyli.ptr.pMrfAnal->s6na.Right(3) == FSxSTR("tud") ||
                morfistLyli.ptr.pMrfAnal->s6na.Right(3) == FSxSTR("dud"))
                return ArvaGene2(&valja, morfistLyli.ptr.pMrfAnal, pGeneLiik, &gv, pGeneKigi);
            else
                return false;
            }
        // analüüs oletatud või abisõnastikust
        if (mrfFlags->Chk(MF_OLETA))
            {
            // oli nt blabla-sõna, s.t. et lõpus on tavaline tuntud sõna
            // või oli blablalik, s.t. lõpus on regulaarne sufiks
            return ArvaGene2(&valja, morfistLyli.ptr.pMrfAnal, pGeneLiik, &gv, pGeneKigi);
            }
        }
    // tundmatu sõna
    return false;
    }

bool ETMRFAS::Gene2Detailne(       // -1==siiber; 0==ok
    MRFTULEMUSED   *pValja,
    MRFTULEMUSED   *pMrfTul,
    const FSXSTRING  *pnaidis,
    const FSXSTRING  *pGeneLiik,
    const FSXSTRING  *pGeneVormid,
    const FSXSTRING  *pGeneKigi)
    {
    char algv_lopp;
    int algv_vorm;
	int viimne;
    
    FSXSTRING gene_liik = KOIK_LIIGID;  // igaks juhuks
    FSXSTRING genetud_tyvi, gene_t1, gene_t2, ette, kigi;
    int i, sgn=0, k1, k2;
    bool r;
    FSxCHAR vi;
 
    if (pMrfTul->Get_vormid(FSxSTR("sg n,")) != -1)
         sgn = 1; // analyyside hulgas leidub sg n 
    i = pMrfTul->Get_vormid(FSxSTR("ma,"));
    if (i != -1 && pMrfTul->Get_vormid(FSxSTR("tama,")) != i)
         sgn = 1; // analyyside hulgas leidub ma 
    if (*pGeneLiik == FSxSTR("*"))
        gene_liik = KOIK_LIIGID;
    else
        gene_liik = (const FSxCHAR*)*pGeneLiik;
    // vt kõiki algvorme
    //
    kigi = FSxSTR("");
    for (i=0; i < pMrfTul->idxLast; i++)
        {
        if (gene_liik.Find((*pMrfTul)[i]->sl) == -1)
            continue;           // polnud sobiv sõnaliik
        if ((*pMrfTul)[i]->vormid.Find(FSxSTR("?")) != -1 || (*pMrfTul)[i]->vormid.Find(FSxSTR(",")) == -1) // muutumatu s�na
            {
            if (sgn == 0 ||                         // analüüside hulgas polegi käänduvat sõna või ...
                pGeneVormid->GetLength() == 0 ||    // tahetaksegi muutumatut sõna
                pGeneVormid->Find(FSxSTR("sg n")) >=0 )  // käsitaksegi ainsuse nimetavat
                {   // et enne //_*_ // et //_*_ // ja enne //_*_ sg n, // enne //_*_ sg g, // oleks kooskõlas
                genetud_tyvi = pMrfTul->rec[i]->tyvi;
                genetud_tyvi.Remove((FSxCHAR)'_');
                genetud_tyvi.Remove((FSxCHAR)'=');
                genetud_tyvi.Remove((FSxCHAR)'+');
                vi = genetud_tyvi[genetud_tyvi.GetLength()-1];
                if (pGeneKigi->GetLength()>0)
                    {
                    if (!TaheHulgad::OnHelitu(vi))
                        kigi = FSxSTR("gi");
                    else
                        kigi = FSxSTR("ki");
                    }
                pValja->Add(
                    (const FSxCHAR *)genetud_tyvi, 
                    FSxSTR(""),  // 0-l�pu puhul 0 ei lisa 
                    (const FSxCHAR *)kigi, // 
                    (*pMrfTul)[i]->sl, 
                    (*pMrfTul)[i]->vormid);  

                continue;
                }
            }

         if ( (*pMrfTul)[i]->vormid.Find(FSxSTR("sg n,"))!= -1 )
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            algv_lopp = null_lopp;
            algv_vorm = sg_n;
            }
        else if ((*pMrfTul)[i]->vormid.Left(3) == FSxSTR("ma,")) 
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            algv_lopp = lopp_ma;
            algv_vorm = ma;
            }
        else if ( omastavanr(&((*pMrfTul)[i]->tyvi)) != -1 )
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            algv_lopp = null_lopp;
            algv_vorm = sg_g;
            }
        else if (!sgn && (*pMrfTul)[i]->vormid.Find(FSxSTR("pl n,"))!= -1)
            {  
            algv_lopp = lopp_d;
            algv_vorm = pl_n;
            // HJK 2008: igaks juhuks (kui eelnenud analüüsil on tehtud tyve asemel lemma)
            if ( (*pMrfTul)[i]->tyvi.Right(1) == FSxSTR("d") ) // nt Madalmaad; votad lopust maha
                (*pMrfTul)[i]->tyvi = (*pMrfTul)[i]->tyvi.Left((*pMrfTul)[i]->tyvi.GetLength()-1);
            }
        else if (!sgn && 
			// null-lopp !!! 
			(*pMrfTul)[i]->sl == LIIK_VERB &&
			((*pMrfTul)[i]->tyvi == FSxSTR("ei") || 
			(*pMrfTul)[i]->tyvi == FSxSTR("\x00E4ra")))  // ei, ära puhuks
            {
            algv_lopp = null_lopp;
            FSXSTRING tmpstr;
            tmpstr = (*pMrfTul)[i]->vormid;
            if (TaheHulgad::OnLopus(&tmpstr, FSxSTR(", ")))
		tmpstr = tmpstr.Left(tmpstr.GetLength()-2);
            algv_vorm = vormnr((const FSxCHAR *)tmpstr);
            }
        else
            {
            continue;               // seda rohkem ei vt, sest pole algvorm
            }
        gene_t1 = (*pMrfTul)[i]->tyvi;
	// algul geneme terveid sõnu (lootes, et ka liitsõnad on sõnastikus sees)
	gene_t2 = gene_t1;
	gene_t2.Remove((FSxCHAR)'_');
	gene_t2.Remove((FSxCHAR)'+');
	gene_t2.Remove((FSxCHAR)'=');
	ette = FSxSTR("");
	viimne = pValja->idxLast; 
 	r = GeneMTVDetailne(pValja, &ette, &gene_t2, pnaidis, &gene_liik, pGeneVormid, algv_lopp, algv_vorm, pGeneKigi );
        if (r == false)
            return false;
	if (pValja->idxLast > viimne) // midagi leitigi 
            {
            pValja->eKustTulemused = eMRF_SP; // tulemused põhisõnastikust
            continue; 
            }
        k1 = gene_t1.ReverseFind((FSxCHAR)'_')+1;
        k2 = gene_t1.ReverseFind((FSxCHAR)'=')+1;
	if (k1==k2)  // pole ei _ ega =, seega oli lihtsõna
            continue;
        if (k2 < k1) // viimane komponent oli osasõna
            {
            if (mrfFlags->Chk(MF_EITULETALIIT)) // tuleb arvestada tervet sõna, koos _
		continue;      // ... aga see ei õnnestunud
            }
//------
	else // viimane komponent oli järelliide
            {
            gene_t2 = gene_t1.Mid(k2);
            ette = gene_t1.Mid(0, k2);
            ette.Remove((FSxCHAR)'_');
            ette.Remove((FSxCHAR)'=');
	    ette.Remove((FSxCHAR)'+');
	    r = GeneSTV(pValja, &ette, &gene_t2, /*&((*pMrfTul)[i]->sl),*/ &gene_liik, pGeneVormid, algv_lopp, algv_vorm, pGeneKigi ); 
	    if (r == false)
		return false;
	    if (pValja->idxLast > viimne) // midagi leitigi 
		continue; 
            }
	// viimane komponent oli osasõna
	for (k1=gene_t1.Find((FSxCHAR)'_'); k1!=-1; k1=gene_t1.Find((FSxCHAR)'_', k1+1)) // võta järjest eestpoolt osi ära, kuni midagi järel pole
	    {
	    k1 += 1;
	    gene_t2 = gene_t1.Mid(k1);
	    ette = gene_t1.Mid(0, k1);
	    ette.Remove((FSxCHAR)'_');
	    ette.Remove((FSxCHAR)'=');
	    ette.Remove((FSxCHAR)'+');
	    gene_t2.Remove((FSxCHAR)'_');
	    gene_t2.Remove((FSxCHAR)'=');
	    gene_t2.Remove((FSxCHAR)'+');
	    r = GeneMTVDetailne(pValja, &ette, &gene_t2, pnaidis, &gene_liik, pGeneVormid, algv_lopp, algv_vorm, pGeneKigi );
	    if (r == false)
		return false;
	    if (pValja->idxLast > viimne) // midagi leitigi 
                {
                pValja->eKustTulemused = eMRF_SP; // tulemused põhisõnastikust
		break; 
                }
	    }
        }
    pValja->SortUniq();
    return true;
    }

// NB ei keera vastavalt suur-lipule pärast
//

bool ETMRFAS::GeneMTVDetailne( 
    MRFTULEMUSED *pValja,
    FSXSTRING *gPrf,       // käib tüve ette
    const FSXSTRING *gTyviAlgne,      
    const FSXSTRING *pnaidis,
    const FSXSTRING *sl,		   // sonaliigid, millesse kuuluvaid sõnu tahetakse
    const FSXSTRING *geneVormid, // genetavate vormide loend 
    const int algv_lopp,   // 0, -ma voi -d 
    const int algv_vorm,   // sg_g, sg_n, ma või pl_n 
    const FSXSTRING  *pGeneKigi)
    {
    int i, idx, res, k1, k2, nSonaLiiki;
    //bool suur=false;
    FSXSTRING *sonaLiigid;
    FSXSTRING gTyviUus;
    FSXSTRING genetud_tyvi, gene_t1, gene_t2, ette, gTyvi;
    TYVE_INF tmp_dptr[SONAL_MAX_PIK];
    TYVE_INF naidise_dptr[SONAL_MAX_PIK];
    int naidise_idx=0, mitu_naidise_homon=0;

    // leia näidissõna muutumisviis 
    if (pnaidis->GetLength() > 0)
        {
        res=cXXfirst((const FSxCHAR*) *pnaidis, pnaidis->GetLength(), &naidise_idx);
        if(res == 0) // s.t. leidis mis vaja
            { 
            sonaLiigid = sonaliik[naidise_idx];
            mitu_naidise_homon = sonaLiigid->GetLength();
            memmove(naidise_dptr, dptr, SizeOfLg2(mitu_naidise_homon));
            }
        }
    gTyvi = *gTyviAlgne;
    gene_t2 = *gTyviAlgne;
    if (gTyvi.Find(FSxSTR(" "))!=-1)
        gTyvi.Replace(FSxSTR(" "), FSxSTR("="), 1);
    res=cXXfirst(&gTyvi,&idx);
    if(res == POLE_SEDA || res == POLE_YLDSE)
        {
        // - ja / sisald. sonade jaoks HJK 20.05.98

        k1 = gTyviAlgne->ReverseFind((FSxCHAR)'-')+1;
        k2 = gTyviAlgne->ReverseFind((FSxCHAR)'/')+1;
        if (k2 > k1)
            k1 = k2;
        if (k1 > 0)
            {
            // Võtame tagumise otsa järgi
            gene_t2 = gTyviAlgne->Mid(k1);
            ette = gTyviAlgne->Mid(0, k1);
            res=cXXfirst(((const FSxCHAR*)gene_t2), gene_t2.GetLength(), &idx);
            if(res == POLE_SEDA || res == POLE_YLDSE)
                {
                if (TaheHulgad::SuurAlgustaht(&gene_t2))
                    {
                    // viimane sõna suurtäheline
                    // teeme v?ikseks ja proovime uuesti
                    gene_t2.MakeLower();
                    res = cXXfirst(&gene_t2, &idx);
                    }
                }
            if(res == 0)
                {
                *gPrf += ette;
                gPrf->Remove((FSxCHAR)'+'); // eemaldame asjatud +_=
                gPrf->Remove((FSxCHAR)'_');
                gPrf->Remove((FSxCHAR)'=');
                }
            }
        else // sellist tyve pole, ja sõnas polnud ka - ega /
            { // proovin jõuga analüüsida analoogiliselt sõnadega, millel on samasugune lõpp e sufiks
            return GeneSTV(pValja, gPrf, gTyviAlgne, sl, geneVormid, algv_lopp, algv_vorm, pGeneKigi);
            }
        }
 
    if(res == POLE_SEDA || res == POLE_YLDSE) // seda ei saa olla
        return true;
    sonaLiigid=sonaliik[idx];
    nSonaLiiki=sonaLiigid->GetLength();
    memmove(tmp_dptr, dptr, SizeOfLg2(nSonaLiiki)); // tõsta dptr kõrvale, sest ta soditakse mujal ära

    for(i=0; i < nSonaLiiki; i++)
        {
        // vaja kontrollida, kas on ikka vajaliku algvormi tüvi
        gTyviUus = gene_t2;
        if(OtsiTyvi(&(tmp_dptr[i].idx), 
                        algv_lopp, algv_vorm, &gTyviUus)==false)
            continue; //polnud sobiv tüvi
        if(gTyviUus == gene_t2) // õige algvormi tüvi
            {
            if((*sonaLiigid)[i]==W_SL) // nagunii on ka S liigiline sõna leitud
				continue;
            if((*sonaLiigid)[i]==(FSxCHAR)'B' &&
                                        sl->Find((FSxCHAR)'A') >=0)
                {
                // kah õige sõnaliik,
                // tahad A-d saad B,
                // aga ütleme, et said A
                if(GeneTLDetailne(pValja, naidise_dptr, mitu_naidise_homon, gPrf, &gTyviUus, 
                    (FSxCHAR)'A', 
                    &(tmp_dptr[i]),geneVormid, pGeneKigi)==false)
                    return false; // crash
                }
            else if(sl->Find((*sonaLiigid)[i]) >= 0)
            //if((*sl)[0]==(*(mrf->sonaliik[idx]))[i])
                {
                if(GeneTLDetailne(pValja, naidise_dptr, mitu_naidise_homon, gPrf, &gTyviUus, 
                    (*sonaLiigid)[i], 
                    &(tmp_dptr[i]),geneVormid, pGeneKigi)==false)
                    return false; // crash
                }
            }
        }
    return true;
    }

//bool ETMRFAS::GeneTLDetailne( 
bool ETMRFAS::GeneTLDetailne( 
    MRFTULEMUSED  *pValja,
    const TYVE_INF *naidise_dptr,
    const int mitu_naidise_homon,
    const FSXSTRING *gPrf,       // käib tüve ette
    const FSXSTRING *gTyvi,      // algvormi tüvi morf analüüsijast (nt piksel))
    const FSxCHAR   sl,		   // sõnaliik, millesse kuuluvaid sõnu tahetakse
	TYVE_INF    *tyveinf,      // kõik gTyviga seotud info, mis sõnastikust on leitud
    const FSXSTRING *geneVormid, // genetavate vormide loend
    const FSXSTRING  *pGeneKigi)
    {
    MKT1c *rec1; // siia pannakse gTyvi (nt piksel) lgNr ja tyMuut
    MKTc  *rec;  // {lgNr, tyMuut} massiiv, mis on seotud ühe sõnaga; nt tyvedele piksel, piksli, piksle
    int muutumatu; // muutumatu tüveosa (nt piks)
    int i, j;
    FSXSTRING vormityvi;

    if((rec1=tyveMuutused.Get(tyveinf->idx.tab_idx,tyveinf->idx.blk_idx))==NULL)
        {
        return false;
        }
    // leia muutumatu tüveosa
    if((muutumatu=gTyvi->GetLength()-rec1->tyMuut.GetLength()) < 0)
        {
        return false;
        }
    if((rec=tyveMuutused[tyveinf->idx.tab_idx])==NULL)
        {
        return false;
        }
    for(i=0; i < rec->n; i++) // vt selle sõna kõiki tüvesid
        {
        FSXSTRING tyvi= gTyvi->Left(muutumatu) + rec->mkt1c[i].tyMuut;
        FSXSTRING tyvi_leksikonis=tyvi;
        int slTabIdx;
        int sliike;
        if (tyvi_leksikonis.Find(FSxSTR(" "))!=-1)
            tyvi_leksikonis.Replace(FSxSTR(" "), FSxSTR("="), 1);
	if (cXXfirst(&tyvi_leksikonis, &slTabIdx)!=ALL_RIGHT)
	    {
	    return NULL;
	    }
        sliike = sonaliik[slTabIdx]->GetLength();
        // peab tsükeldama ja sõnaliike ja tab_idx kontrollima,
        // sest sõnastik on niimoodi tehtud:
        // homonüümsed tüved (s.h. mittevajalikud) on kuidagi üheskoos...
        for (j=0; j < sliike; j++) 
            {
            int jj;
            for (jj=0; jj < mitu_naidise_homon; jj++)
                {  // kas samas paradigmas on ka näidise tüvi ?
                if (dptr[j].idx.tab_idx == naidise_dptr[jj].idx.tab_idx)
                    break;
                }
            if (mitu_naidise_homon > 0 && jj == mitu_naidise_homon)
                continue; // ei vasta nõutud paradigmale; nt. tahetakse palgi, aga see on palga
            if ((*sonaliik[slTabIdx])[j] == sl || // on sama sõnaliik ...
                ((*sonaliik[slTabIdx])[j] == (FSxCHAR)'B' && sl == (FSxCHAR)'A')) // või sobiv sõnalik
                {
                if (dptr[j].idx.tab_idx == tyveinf->idx.tab_idx) 
                    { // ... ja sama paradigma tüvi
                    LisaKdptr(dptr, &vormityvi, &tyvi, j);
                    if(GeneL(pValja, gPrf, &vormityvi, sl, dptr[j].lg_nr, geneVormid, pGeneKigi)==false)
                        {
                        return false;
                        }
                    }
                }
            }
        //-----
        }
    return true;
    }

bool ETMRFAS::GeneL(  
    MRFTULEMUSED   *pValja,
    const FSXSTRING *gPrf,       // käib tüve ette
    const FSXSTRING *gTyvi,      // tüvi morf analüüsijast
    const FSxCHAR   sl,		   // sõnaliik, millesse kuuluvaid sõnu tahetakse
	const int  lgNr,
    const FSXSTRING *geneVormid, // genetavate vormide loend
    const FSXSTRING  *pGeneKigi)
    {
    // tsükeldame üle komaga eraldet vormide
    int vasak=0, parem=0;
    FSXSTRING geneVorm1, tmp;

    for (tmp = *geneVormid; tmp.GetLength() > 0; tmp = tmp.Mid(vasak))
        {
        parem = tmp.Find((FSxCHAR)',');
        if (parem == -1)
            parem = tmp.GetLength(); // viimase lõpus polnud koma; ei saa olla
        geneVorm1=tmp.Left(parem);
        geneVorm1.Trim(); // igaks juhuks, kes kurat teab
        vasak=parem+1;
        if(GeneL1(pValja, gPrf,gTyvi,sl,lgNr,&geneVorm1, pGeneKigi)==false)
            {
            return false;
            }
        }
    return true;
    }

bool ETMRFAS::GeneL1( 
    MRFTULEMUSED   *pValja,
    const FSXSTRING *gPrf,       // käib tüve ette
    const FSXSTRING *gTyvi,      // tüvi morf analüüsijast
    const FSxCHAR   sl,		  
        const int  lgNr,
    const FSXSTRING *geneVorm, // genetav vorm
    const FSXSTRING  *pGeneKigi)
    {
    int i,j,l6ppudeAlgusNihe,l6ppudeArv,vormideAlgusNihe,ffnr;
    int l6pujrknr;
    FSxCHAR tmp[2]=FSxSTR("\0");
    FSXSTRING l6pp, tyvi, liik, kigi;
    FSxCHAR vi;
    tmp[0]=sl;
    liik=tmp;
    kigi = FSxSTR("");

    // sõnastiku kettalt sisselugemisel tuleks kohe need2 baiti
    // intiks teisenda ja seda kasutadagi lõputu bitinikerdamise asemel
    l6ppudeAlgusNihe= (((groups[lgNr].gr_algus)&0xFF)<<8)|
                                 (groups[lgNr].gr_lopp&0xFF);
    l6ppudeArv=(unsigned char)(groups[lgNr].cnt);
    vormideAlgusNihe = homo_form * l6ppudeAlgusNihe;
    ffnr = vormnr((const FSxCHAR *)*geneVorm);
    assert( l6ppudeAlgusNihe >=0 && l6ppudeArv >=0  && vormideAlgusNihe >=0 );
    
    if(ffnr <= 0)
        return false; // sellist vormi pole üldse olemaski
    for(i=0; i < l6ppudeArv; i++)
        {
        for(j=0; j < (int)homo_form; j++)
            {
            if( ffnr==(unsigned char)(fgr[vormideAlgusNihe+(i*homo_form) + j]) )
                {
                // otsitav vorm leitud
                l6pujrknr=(unsigned char)(gr[l6ppudeAlgusNihe + i]);
                l6pp=l6ppudeLoend[l6pujrknr];
                //if(adHocString.GetLength() > 0 && ffnr==vormideLoend[FSxSTR("sg n"])) //Kuidas see sai kompileeruda?!
                if(adHocString.GetLength() > 0 && ffnr==vormnr(FSxSTR("sg n")))
                    {
                    l6pp += adHocString;
                    }
                tyvi= *gPrf + *gTyvi;
                FSXSTRING geneVorm1 = *geneVorm;
                geneVorm1 += FSxSTR(", ");
 
                if (l6pp.GetLength() > 0)
                    vi = l6pp[l6pp.GetLength()-1];
                else
                    vi = tyvi[tyvi.GetLength()-1];
                if (pGeneKigi->GetLength()>0)
                    {
                    if (!TaheHulgad::OnHelitu(vi))
                        kigi = FSxSTR("gi");
                    else
                        kigi = FSxSTR("ki");
                    }
                pValja->Add(
                    (const FSxCHAR *)tyvi, 
                    (const FSxCHAR *)l6pp, 
                    (const FSxCHAR *)kigi, 
                    (const FSxCHAR *)liik, 
                    (const FSxCHAR *)geneVorm1);
                }
            }
        }
    return true;
    }

bool ETMRFAS::GeneSTV(
    MRFTULEMUSED   *pValja,
    const FSXSTRING *gPrf,        // käib tüve ette
    const FSXSTRING *gSuffiks,    // suffiks morf analüüsija väljundist
    //const FSXSTRING *gSufSl,      // suffiksi son liik morf anal väljundist
    const FSXSTRING *sl,          // sõnaliigid, millesse kuuluvaid sonu tahetakse
    const FSXSTRING *geneVormid,  // genetavate vormide loend 
    const int algv_lopp,   // 0, -ma voi -d 
    const int algv_vorm,   // sg_g[0], sg_n[0], ma voi pl_n[0] 
    const FSXSTRING *pGeneKigi)
    {
    FSUNUSED(sl);
    int sufNr;  // sufiksi nr sufiksite tabelis
    int i, j;
    FSXSTRING tmpSuf, tmpSuf1, tmpSuf2;
    FSXSTRING *sonaLiigid;
    FSxCHAR sl1;
    //FSXSTRING *sssl;
    int nSonaLiiki;
    FSXSTRING gTyviUus;
    //FSXSTRING gene_t2;
    FSXSTRING styvi;
    FSXSTRING skronksutyvi;
    int adhocnu = 0; // ad hoc nud, tud, dud jaoks

    if (gSuffiks->GetLength() >= SUFLEN)
        return true; //* ei saa olla sufiks *
    
    tmpSuf = (const FSxCHAR *)*gSuffiks;
    //* otsime välja sufiksi indeksi sufiksite tabelist *
    sufNr=suffnr((const FSxCHAR *)tmpSuf);
    if (sufNr == -1)    
        {
        //* sellist sufiksit pole olemas, *
        //* see juhtub nt siis, kui suf loendis on pikem sufiks, *
        //* aga lingv ilu pa'rast na'idat. teda lu'hemana *
        //* nt =umuslik asemel =muslik *
        //* mingi kombineerimine *
        int mitu_maha = gPrf->GetLength();

        if (mitu_maha > 3)
            mitu_maha = 3;
        tmpSuf1 = gPrf->Right(mitu_maha);
        tmpSuf1 += (const FSxCHAR *)*gSuffiks;
        for (i=0; i < mitu_maha; i++)
            {
            tmpSuf = tmpSuf1.Mid(i);
	    if ((sufNr=suffnr((const FSxCHAR *)tmpSuf)) > -1)    
                break; //* suffiks käes *
            }
        if (i == mitu_maha) // tavaliselt seda ei saa olla, et ei leia sobivat suffiksit 
            {
            if(*gSuffiks == FSxSTR("nud") || *gSuffiks == FSxSTR("tud") || *gSuffiks == FSxSTR("dud"))
                { // ... aga vahel ikka saab: leksikonis on ainult S nu, tu ja du, mitte A nud, tud ja dud... 
                tmpSuf = gSuffiks->Left(2);
                sufNr=suffnr((const FSxCHAR *)tmpSuf);
                adhocnu = 1;  // lipp püsti
                }
            else
                return true;
            }
        tmpSuf1 = tmpSuf.Mid((int)(sufix[sufNr].mitutht));
        }
    else
        tmpSuf1 = tmpSuf;

    sonaLiigid = sonaliik[(unsigned char) sufix[sufNr].ssl];
    nSonaLiiki = sonaLiigid->GetLength();

    for(i=0; i < nSonaLiiki; i++)  // vt sufiksi homonüüme (s.h. lik ja l<ik on homonüümid)
        {
        sl1 = (*sonaLiigid)[i];
        if ( sl->Find(sl1) == -1) // see sõnaliik pole siin lubatud
            if (adhocnu == 1); // ... aga teatud juhtudel ikkagi võiks
            else if (sl->Find((FSxCHAR)'A') != -1 &&      // tahetakse A, aga sufiks on leksikonis S
                    (tmpSuf1 == FSxSTR("tu") ||
                    tmpSuf1.Right(2) == FSxSTR("ke") ||
                    tmpSuf1.Right(4) == FSxSTR("kene"))); // ... aga teatud juhtudel ikkagi võiks
            else
                continue; 
        // vaja kontrollida, kas on ikka vajaliku algvormi tüvi
        gTyviUus = tmpSuf1;
        if(OtsiTyvi(&(sufix[sufNr].suftyinf[i].idx), 
                        algv_lopp, algv_vorm, &gTyviUus)==false)
            continue; //polnud sobiv tüvi
        if(gTyviUus != tmpSuf1) // pole õige algvormi tüvi
            continue;
        if(sl1==W_SL) // nagunii on ka S liigiline sõna leitud
            continue;
        if(sl1==(FSxCHAR)'B' && sl->Find((FSxCHAR)'A') >=0)
            sl1 = 'A'; // kah õige sõnaliik: tahad A-d saad B, aga ütleme, et said A

        MKT1c *rec1; // siia pannakse gTyvi (nt piksel) lgNr ja tyMuut
        MKTc  *rec;  // {lgNr, tyMuut} massiiv, mis on seotud ühe sõnaga; nt tyvedele piksel, piksli, piksle
        int muutumatu; // muutumatu tüveosa (nt piks)

        tmpSuf2 = tmpSuf1;
        if((rec1=tyveMuutused.Get(sufix[sufNr].suftyinf[i].idx.tab_idx,sufix[sufNr].suftyinf[i].idx.blk_idx))==NULL)
            { 
            return false;
            }
        // leia muutumatu tüveosa
        if((muutumatu=tmpSuf1.GetLength()-rec1->tyMuut.GetLength()) < 0)
            {
            return false;
            }
        if((rec=tyveMuutused[sufix[sufNr].suftyinf[i].idx.tab_idx])==NULL)
            {
            return false;
            }
        int tmpsufnr, jj, jjnSonaLiiki;
        FSXSTRING vormityvi;
        FSXSTRING tyvi, utyvi;
        for (j=0; j < rec->n; j++) // vt selle sufiksi paradigma kõiki "tüvesid"
            { 
            
            utyvi = gPrf->Right(sufix[sufNr].mitutht); // tavaliselt "", aga umuslik puhul u
            tyvi = tmpSuf1.Left(muutumatu) + rec->mkt1c[j].tyMuut;
            utyvi += tyvi;
            tmpsufnr=suffnr((const FSxCHAR *)utyvi);
            FSXSTRING *jjsonaLiigid = sonaliik[(unsigned char) sufix[tmpsufnr].ssl];
            jjnSonaLiiki = jjsonaLiigid->GetLength();
            for (jj=0; jj < jjnSonaLiiki; jj++) // vt "tüve" kõiki homonüüme
                {
                if ((*sonaliik[(unsigned char) sufix[tmpsufnr].ssl])[jj] != sl1) 
                     continue; // pole sama sõnaliik ...
                //if (sufix[sufNr].suftyinf[i].idx.tab_idx != sufix[tmpsufnr].suftyinf[jj].idx.tab_idx)
                    //continue; // pole sama paradigma
                // kole asi üksikute juhtumite filtreerimiseks, nt l<ik ja lik eristamiseks
                // tundl<ik+0 vs tundlik+el
                MKT1c *rec2 = tyveMuutused.Get(sufix[tmpsufnr].suftyinf[jj].idx.tab_idx,sufix[tmpsufnr].suftyinf[jj].idx.blk_idx);
                if (rec->mkt1c[j].lgNr != rec2->lgNr)
                    continue; // homonüümne tüvi (kui hääldust ei arvesta) ja samas paradigmas, aga tegelt sobimatu
                LisaKdptr(sufix[tmpsufnr].suftyinf, &vormityvi, &tyvi, jj);
                if (adhocnu == 1) // nu -> nud
                    {
                    int sgn_koht;
                    if ((sgn_koht=geneVormid->Find(FSxSTR("sg n"))) != -1)
                        {
                        FSXSTRING uustyvi = *gPrf;
                        uustyvi += tyvi;
                        uustyvi += FSxSTR("d");
                        pValja->Add(
                                (const FSxCHAR *) uustyvi, 
                                FSxSTR(""), 
                                (const FSxCHAR *)*pGeneKigi, 
                                FSxSTR("A"), 
                                FSxSTR("sg n, "));
                        FSXSTRING uusgeneVormid = geneVormid->Mid(0, sgn_koht);
                        uusgeneVormid += geneVormid->Mid(sgn_koht+5);
                        if (GeneL(pValja, gPrf, &vormityvi, (const FSxCHAR) 'A', rec->mkt1c[j].lgNr, 
                             &uusgeneVormid, pGeneKigi)==false)
                             {
                             return false;
                             }
                        }
                    else
                        {
                        if (GeneL(pValja, gPrf, &vormityvi, (const FSxCHAR) 'A', rec->mkt1c[j].lgNr, 
                             geneVormid, pGeneKigi)==false)
                             {
                             return false;
                             }
                        }
                    }
                else 
 
                    {
                     if(GeneL(pValja, gPrf, &vormityvi, (const FSxCHAR) sl1, rec->mkt1c[j].lgNr, 
                         geneVormid, pGeneKigi)==false)
                         {
                         return false;
                         }
                    }
                }
            }
        }
        return true;
    }

bool ETMRFAS::ArvaGene2(       // -1==siiber; 0==ok
    MRFTULEMUSED   *pValja,
    MRFTULEMUSED   *pMrfTul,
    const FSXSTRING  *pGeneLiik,
    const FSXSTRING  *pGeneVormid,
    const FSXSTRING  *pGeneKigi)
    {
    //char algv_lopp;
    //int algv_vorm,
    int viimne;
    
    FSXSTRING gene_liik = KOIK_LIIGID;  // igaks juhuks
    FSXSTRING genetud_tyvi, gene_t1, gene_t2, ette, kigi;
    int i, sgn=0;
    FSxCHAR vi;
 
    if (pMrfTul->Get_vormid(FSxSTR("sg n,")) != -1)
         sgn = 1; // analyyside hulgas leidub sg n 
    i = pMrfTul->Get_vormid(FSxSTR("ma,"));
    if (i != -1 && pMrfTul->Get_vormid(FSxSTR("tama,")) != i)
         sgn = 1; // analyyside hulgas leidub ma 
    if (*pGeneLiik == FSxSTR("*"))
        gene_liik = KOIK_LIIGID;
    else
        gene_liik = (const FSxCHAR*)*pGeneLiik;
    // vt kõiki algvorme
    //
    kigi = FSxSTR("");
    viimne = pValja->idxLast; 
    for (i=0; i < pMrfTul->idxLast; i++)
        {
        if ((*pMrfTul)[i]->vormid.Find(FSxSTR("?")) != -1 || (*pMrfTul)[i]->vormid.Find(FSxSTR(",")) == -1) // muutumatu s�na
            {
            if (gene_liik.Find((*pMrfTul)[i]->sl) == -1)
                continue;           // polnud sobiv sõnaliik
            if (sgn == 0 ||                         // analyyside hulgas polegi käänduvat sõna või ...
                pGeneVormid->GetLength() == 0 ||    // tahetaksegi muutumatut sõna
                pGeneVormid->Find(FSxSTR("sg n")) >=0 )  // küsitaksegi ainsuse nimetavat
                {   // et enne //_*_ // ja enne //_*_ sg n, // enne //_*_ sg g, // oleks kooskõlas
                genetud_tyvi = pMrfTul->rec[i]->tyvi;
                genetud_tyvi.Remove((FSxCHAR)'_');
                genetud_tyvi.Remove((FSxCHAR)'=');
                genetud_tyvi.Remove((FSxCHAR)'+');
                vi = genetud_tyvi[genetud_tyvi.GetLength()-1];
                if (pGeneKigi->GetLength()>0)
                    {
                    if (!TaheHulgad::OnHelitu(vi))
                        kigi = FSxSTR("gi");
                    else
                        kigi = FSxSTR("ki");
                    }
                pValja->Add(
                    (const FSxCHAR *)genetud_tyvi, 
                    FSxSTR(""),  // 0-lõpu puhul 0 ei lisa
                    (const FSxCHAR *)kigi, // 
                    (*pMrfTul)[i]->sl, 
                    (*pMrfTul)[i]->vormid);  

                continue;
                }
            }

         if ( (*pMrfTul)[i]->vormid.Find(FSxSTR("sg n,"))!= -1 )
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            //algv_lopp = null_lopp;
            //algv_vorm = sg_n;
            }
        else if ((*pMrfTul)[i]->vormid.Left(3) == FSxSTR("ma,")) 
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            //algv_lopp = lopp_ma;
            //algv_vorm = ma;
            }
        else if ( omastavanr(&((*pMrfTul)[i]->tyvi)) != -1 )
            {
            sgn=1;        //* on leitud lihtsaim algvorm *
            //algv_lopp = null_lopp;
            //algv_vorm = sg_g;
            }
        else if (!sgn && (*pMrfTul)[i]->vormid.Find(FSxSTR("pl n,"))!= -1)  //* votan d lopust maha *
            {
            if ((*pMrfTul)[i]->tyvi.Right(2) == FSxSTR("nu") ||
                (*pMrfTul)[i]->tyvi.Right(2) == FSxSTR("tu") ||
                (*pMrfTul)[i]->tyvi.Right(2) == FSxSTR("du"))
                { // nt vastsündinu+d
                (*pMrfTul)[i]->tyvi += FSxSTR("d");
                (*pMrfTul)[i]->lopp = FSxSTR("");
                (*pMrfTul)[i]->sl = LIIK_A;
                sgn=1;        // vastsündinud+0 on lihtsaim algvorm
                }
            else
                {
                //algv_lopp = lopp_d;
                //algv_vorm = pl_n;
                }
            }
        else
            {
	    continue;               // seda rohkem ei vt, sest pole algvorm
            }
        if (gene_liik.Find((*pMrfTul)[i]->sl) == -1)
            continue;           // polnud sobiv sõnaliik
        gene_t1 = (*pMrfTul)[i]->tyvi;
        // siia tuleb oletamine ise
        FSXSTRING analoogvorm, v_analoogvorm;
        FSXSTRING tyhi;
        bool rs;

        for (analoogvorm=oletajaDct.sobiv_analoog(&gene_t1, &(*pMrfTul)[i]->sl);; analoogvorm=oletajaDct.jargmine_sobiv_analoog())
            {
            int mitu;
            int a_pikkus, g_pikkus, pikkus;
            int res;
            MRFTULEMUSED tulemus, analoog_tulemus;
            int tagasi;

            a_pikkus = analoogvorm.GetLength();
            if (a_pikkus == 0) // polnud rohkem sobivaid analooge
                break;
            g_pikkus = gene_t1.GetLength();
            pikkus = a_pikkus > g_pikkus ? g_pikkus : a_pikkus;
            // leia, kui pikk jupp on sõnadel lõpus ühesugune
            for (mitu = 1; mitu <= pikkus; mitu++)
                {
                if (analoogvorm[a_pikkus-mitu] != gene_t1[g_pikkus-mitu])
                    break;
                }
            mitu--;
            if ((*pMrfTul)[i]->sl == LIIK_VERB)
                {
                v_analoogvorm = analoogvorm;
                v_analoogvorm += FSxSTR("ma");
                res = chkwrd(&tulemus, &v_analoogvorm, a_pikkus+2, 1, &tagasi, ALGV_LIIK);
                }
            else
                res = chkwrd(&tulemus, &analoogvorm, a_pikkus, 1, &tagasi, ALGV_LIIK);
                assert(res <= ALL_RIGHT);
	        if (res > ALL_RIGHT)
	            return false; // viga; ei saa olla 
            if (!tulemus.on_tulem())
                {
                assert(tulemus.on_tulem());
                }
            assert(tagasi==1);
	    if (!tulemus.on_tulem())    // polnud norm. eesti k. sõna
	        return false; // viga; ei saa olla
           
            rs = Gene2Detailne(&analoog_tulemus, &tulemus, &tyhi, pGeneLiik, pGeneVormid, pGeneKigi);
            if (rs == false)
                return false;
            analoog_tulemus.VotaTyvedeltEest(a_pikkus-mitu);
            analoog_tulemus.LisaTyvedeleEtte(gene_t1.Left(g_pikkus-mitu));
            pValja->Move2Tail(&analoog_tulemus);
            }
       }
           
    if (pValja->idxLast > viimne) // midagi leitigi 
        {
        pValja->eKustTulemused = eMRF_SO; // tulemused tulid sünteesi-oletajast
        }
    pValja->SortUniq();
    return true;
    }

// }}-PRIVATE




