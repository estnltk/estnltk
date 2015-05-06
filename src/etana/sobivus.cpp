
// 2000.07.14 TV 
// 2002.03.20 TV klass �mberv��natud

/*
 * pref, tyve, suf ja lopu omavaheliste sobivuste kontrollid
 */

/*
* kontrollib, kas lopunr & sonaliik esinevad yheaegselt mones lopugr-s
* paneb resultaadi ehk_on[]-sse
* return (sobivate lnr ja sonaliikide arv)
* POLE_TAANDLP v�i SUVA_LIIK puhul vastavalt lopunr v�i sonaliiki ei kontr.
*/

#include <string.h>

#include "mrf-mrf.h"
#include "mittesona.h"
#include "tloendid.h"

/*
* otsib l�ppu end lgr-st lgrnr
* (l�ppude jada (*gr)[(*groups)[grnr].gr] on j�rjestatud)
* return(selle l�pu koht lgr l�ppude jadas)
* return(-1), kui sellist l�ppu seal polnud
*/

int DCTRD::endingr(int grnr, char end)
	{
    int i, jrknr, int_end=(unsigned char)end;

	//jrknr = (groups[grnr].gr_algus << 8) | groups[grnr].gr_lopp; //thj 5.11.97
    jrknr=KaksYheks(groups[grnr].gr_algus, groups[grnr].gr_lopp);
	for (i=0; i < groups[grnr].cnt; i++)
		{
		/* thj 5.11.97 jrknr = ((*groups)[grnr].gr_algus << 8) | (*groups)[grnr].gr_lopp;*/
		if ( (unsigned char)(gr[jrknr + i]) == int_end )
			return i;
		if ( (unsigned char)(gr[jrknr + i])  > int_end )
			return -1;
		}
	return -1;
	}

/*
* 10.06.98 selleks, et saaks ta'psemalt algvormi tyve ka'tte
* otsin, kas mingis lopugrupis on teatud lopp ja vorm
*/
int DCTRD::LopugruppSisaldabVormi( // 0==vajalik lopp-vorm l�pugrupis olemas; -1==pole
    int lgNr,       // kas see l�pugrupp
    int lopunr,       // sisaldab sellist loppu ja
    int vorm)   //      sellist vormi?
    {
    int  k, llnr, ffnr;
    unsigned l;

	k = endingr( lgNr, lopunr );
	if (k == -1)          /* seda loppu pole selles lopugrupis */
	    return k;         /* pole enam midagi otsida */
	else       /* kontr, kas m�ni vorm v_ind-st selle l�puga sobib */
	    {
	    //llnr = (groups[lgNr].gr_algus << 8) | groups[lgNr].gr_lopp;
            llnr = KaksYheks(groups[lgNr].gr_algus, groups[lgNr].gr_lopp);
	    llnr = homo_form * (llnr + k);
	    for (l=0; l < homo_form; l++)  /*vt lopu vormihomonyyme*/
		{
                ffnr = (unsigned char)(fgr[llnr + l]);
		if (ffnr==vorm)
		     return(0);
		}
	    }
    return -1;
    }


/*
* uus variant; hjk 02.05.01
 * return mitu sobivat sõnaliiki oli, s.t. mitu 1-e on massiivis sobivad
 * nt haige puhul võib olla sl=SA, sobivad=11
 * kasutatakse m.h. selleks, et filtreerida välja liitsõna/tuletise komponendiks mittesobivaid tüvesid,
 * nt. kääri SV puhul sobivad=10 või 01, sõltuvalt muude komponentide poolt esitatavatest nõuetest
 * (kääri_terad või kääri=mine)
*/
int MORF0::ssobivus( 
    TYVE_INF *grupid,  // sisend; lõpugrupid
    const FSxCHAR *sl, // sisend; lõpugrupi sõnaliigid (stringina))
    const int sl_pik,  // sisend; massiivi sl pikkus
    const char lopunr, // sisend; lubatav lõpp (õigemini jrk nr lõppude loendis)
    const FSxCHAR *sonalk, // sisend; lubatavad sõnaliigid (stringina)) 
    const int vorminr,  // sisend; lubatav vorm (õigemini jrk nr vormide loendis)
    char *sobivad,    // väljund; 0 ja 1 joru
    const int sobivatePikkus  // sisend; massiivi 'sobivad' pikkus
    )
    {
    if(sobivatePikkus<sl_pik)
        throw VEAD(ERR_MORFI_MOOTOR,ERR_MINGIJAMA,__FILE__,__LINE__,"$Revision: 855 $");
    register int i;
    int j=0;
    int  k=0, llnr, ffnr, ok;
    unsigned l;
    FSxCHAR s;
    FSXSTRING csonalk;
    //FSXSTRING slsonalk;
    
    csonalk = sonalk;
    //slsonalk = sl;
    memset(sobivad, 0, sobivatePikkus);
    for (i=0; i < sl_pik; i++)
	    {
	    if ( csonalk != SUVA_LIIK )
	        {                               /* kontr. sonaliigi sobivust */
            s = sl[i];
            if (csonalk.Find(s)==-1)
		        continue;    // lopugrupp ei esinda sellist sonaliiki
            }
	    if ((signed char)lopunr != SUVA_LP)
	        {                               /* kontr. lopu olemasolu */
	        k = endingr( GetLgNr(grupid, i), lopunr );
	        if (k == -1)          /* seda loppu pole selles lopugrupis */
		        continue;         /* vt teisi lopugruppe */
	        }
        if (vorminr == SUVA_VRM)
            ok = 1;
        else
            {
            ok = 0;
	        if ((signed char)lopunr != SUVA_LP)
                {
                llnr = KaksYheks(groups[GetLgNr(grupid, i)].gr_algus, groups[GetLgNr(grupid, i)].gr_lopp);
	            llnr = homo_form * (llnr + k);
	            for (l=0; l < homo_form; l++)  /*vt lopu vormihomonyyme*/
		            {
                    ffnr = (unsigned char)(fgr[llnr + l]); /* vormi nr */
		            if (!ffnr)
		                break;
		            if (vorminr == ffnr)
                        {
		                ok = 1;
                        break;
                        }
		            }
                }
            }
        if (!ok)
            continue;
        // HJK 5.05.2003; HJK 02.03.2005
        if (mrfFlags.Chk(MF_EILUBATABU)) // nt soovitaja puhul tabus�nad pole lubatud
            {
            if (on_paha_sl(grupid, GetLgNr(grupid, i), sl, TABU_SL))
                continue;
            }
        /*  hjk 04.2015: las need mitmesõnaliste nimede osad olla alati lubatud
        if (!mrfFlags.Chk(MF_SPELL)) // aint spelleri puhul on m�ned s�nad lubatud, nt. Aires
            {
            if (on_paha_sl(grupid, GetLgNr(grupid, i), sl, SPELL_SL))
                 continue;
           }
        */
        if (!mrfFlags.Chk(MF_LUBATESA)) // normaalse morfi puhul tesauruse algvormide staatuses s�navormid (aukudega) pole lubatud
            {
            if (on_paha_sl(grupid, GetLgNr(grupid, i), sl, TESA_SL))
                continue;
            }
        if(i>sobivatePikkus)
            throw VEAD(ERR_MORFI_MOOTOR,ERR_MINGIJAMA,__FILE__,__LINE__,"$Revision: 855 $");
        sobivad[i] = 1;
	    j++;
	    }
    return(j);
    }

/*
 * kui s�naliik koos l�pugrupiga on sama, mis lubamatu liik oma l�pugrupiga, siis return(true); muidu return (false)
 */
bool MORF0::on_paha_sl( TYVE_INF *grupid, const int lg_nr, const FSxCHAR *sl, 
                    const FSxCHAR lubamatu_liik )
     {
     FSXSTRING slsonalk;
     int i;

     slsonalk = sl;
     for (i=0; i < slsonalk.GetLength(); i++)
         {
         if (slsonalk[i] == lubamatu_liik && lg_nr == GetLgNr(grupid, i))
             return(true);
         }
     return(false);
     }


PRSL::PRSL(void)
    {
    //usl1.Start(_usl1_, sizeof(_usl1_)/sizeof(PR_SL1),FSxPR_SL1Srt, FSxPR_SL1Bs);
    usl1.Start(8,0);
    // Kontrollib, kas prefix_tyvi_lp on norm. eestikeelne s�na
    // st s�naliik peab olema p_n_sl; lp peab sobima
    // kui p_n_sl='V' siis on asi veidi keerulisem
    usl1.AddPtr(new CPR_SL1(FSxSTR("de"), 2, FSxSTR("eeri"), 4, 'V'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("de"), 2, FSxSTR("eeru"), 4, 'V'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("ime"), 3, FSxSTR("sti"), 3, 'D'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("re"), 2, FSxSTR("eeri"), 4, 'V'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("re"), 2, FSxSTR("eeru"), 4, 'V'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("taas"), 4, FSxSTR(""), 0, 'V'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("\x00FCli"), 3, FSxSTR("sti"), 3, 'D'));
    usl1.AddPtr(new CPR_SL1(FSxSTR("\x00FCli"), 3, FSxSTR("is"), 2, 'D'));
    usl1.Sort();
    }

typedef struct              // pref, suf, lp sobivuse kontrollimiseks
    { 
    const FSxCHAR *tylp;
    const int l_pik;
    const char uus_sl;
    } PR_SL2;

static  PR_SL2 usl2[4] = 
    {
    {FSxSTR("us"), 2, 'S'},
    {FSxSTR("use"), 3, 'S'},
    {FSxSTR("ev"), 2, 'A'},
    {FSxSTR("va"), 2, 'A'}
    };

int MORF0::sobib_p_t(KOMPONENT *pref, KOMPONENT *tyvi)
    {
    int  pik2;
    FSXSTRING p_n_sl;
    CPR_SL1 *t;
    int i;

    ASSERT(tyvi->sl.GetLength()>0);
    // 07.06.2005 HJK
    if ((tyvi->liitumisinfo).Find(MITTELIITUV_SL) != -1) // HJK 26.05.2006 et igasugu liits�nad ei saaks osaleda
        return 0;
    if ((tyvi->liitumisinfo).Find(L_MITTELIITUV_SL) != -1) // HJK 6.06.2006 et igasugu l�his�nad ei saaks osaleda
        return 0;
    p_n_sl = pref->k_algus;
    p_n_sl += tyvi->k_algus;
    if (viletsls(&p_n_sl)) /* lubamatu liits�na, nt liig_uba */
        return(0);

    if (pref->k_algus == FSxSTR("pool"))
		{
        if (tyvi->sl == FSxSTR("D"))
		    {
            if (TaheHulgad::OnLopus(&(tyvi->k_algus), FSxSTR("si")) && 
                        !TaheHulgad::OnLopus(&(tyvi->k_algus), FSxSTR("kesi"))) 
				{
				if (on_liitsona(tyvi))
					return (0); // poolomaviisi
			    return (1); // poolpimesi HJK 12.11.2004
				}
			else
				return(0); // aga mitte poolneljakesi
		    }
        else if (tyvi->sl == FSxSTR("V"))
            if (tyvi->komp_jargmine) // igaks juhuks kontrollin
                if (tyvi->komp_jargmine->jrk_nr == lopp_des ||
                    tyvi->komp_jargmine->jrk_nr == lopp_tes ||
                    tyvi->komp_jargmine->jrk_nr == lopp_es )
//                { /* tegelikult, voibolla poolmagades jms on hoopis D */
//                }
                return(1);
		}
    p_n_sl = taandliik[ prfix[pref->jrk_nr].sl ];
    if (p_n_sl.Find((FSxCHAR)'V')==-1 && p_n_sl.Find(tyvi->sl)!=-1)
        {
        if (tyvi->sl == FSxSTR("A") && on_muutumatu(tyvi)
            && pref->k_algus.Right(4) != FSxSTR("pool") )
            return(0);
        return(1);
        }
    if (p_n_sl.Find((FSxCHAR)'V')!=-1 && tyvi->sl == FSxSTR("W"))
        {
        tyvi->sl = FSxSTR("S"); // sest tean, et koos W on alati ka S ??? HJK 28.05.01
        return(1);
        }
    for (i=0; i < 4; i++)
        {
        if (TaheHulgad::OnLopus(&(tyvi->k_algus), usl2[i].tylp))
            if (tyvi->sl[0] == usl2[i].uus_sl)
                return(1);
        }

    for(t=prsl.usl1.Get((FSxCHAR *)(const FSxCHAR *)(pref->k_algus)); t; t=prsl.usl1.GetNext())
        {
        pik2 = tyvi->k_pikkus - t->l_pik; /* kui pikk on tyvi enne tyvelp */
        if (pik2 > 1 &&
             tyvi->k_algus.Mid(pik2) == t->tylp )
            {
            if (tyvi->sl[0] == t->uus_sl)
                return(1);
            }
        }
    return(0);
    }

int MORF0::sobib_p_t_s(KOMPONENT *pref, KOMPONENT *tyvi, KOMPONENT *suff)
    {
    FSXSTRING p_n_sl;
    int ssl, k, j;

    ASSERT(tyvi->sl.GetLength()>0);
    if ((tyvi->liitumisinfo).Find(MITTELIITUV_SL) != -1) // HJK 26.05.2006 et igasugu liits�nad ei saaks osaleda
        return 0;
    p_n_sl = taandliik[ prfix[pref->jrk_nr].sl ];
    ssl = (unsigned char)(sufix[suff->jrk_nr].ssl);
    k = sobib_p_t(pref, tyvi);
    if (k)
        return 1;
    if (!k)
        {  // ehk p_n_sl on 'V' ? 
//      if ( strchr(p_n_sl, tyvi->sl[0]) ) // p_n_sl 'V' on erijuhtum 
        if (p_n_sl.Find(tyvi->sl)!=-1)
            return 1;
        }
    // ehk p_n_sl sobib kokku sufiksist tuleneva sonaliigiga? 
    //for (j=0;  j < sonaliik[ssl].pikkus; j++)
    for (j=0;  j < sonaliik[ssl]->GetLength(); j++)
        {
        if (p_n_sl.Find( (*sonaliik[ssl])[j])!=-1)
            return 1;
        }
    return 0;    
    }

//int MORF0::viletstyvi( FSXSTRING *ty )
 //   {
 //   return ( (dctLoend[8])[(FSxCHAR *)(const FSxCHAR *)(*ty)] ) >= 0 ? 1 : 0;
 //   }

int MORF0::viletsls( FSXSTRING *ty )
    {
    return ( (dctLoend[4])[(FSxCHAR *)(const FSxCHAR *)(*ty)] ) >= 0 ? 1 : 0;
    }
/*
* return minimaalne tyvepikkus, mida on m�tet otsida 
*/
int MORF0::minipik(FSXSTRING *ty)
    {
    FSXSTRING ttt;
    int pik=2;

    ttt = (const FSxCHAR *)(ty->Left(3));  
    if ( ttt == FSxSTR("alu") || ttt == FSxSTR("ude") || ttt == FSxSTR("pan") )
	    pik = 4;
    else
        {
        ttt = (const FSxCHAR *)(ttt.Left(2));
        if ( ( (dctLoend[9])[(FSxCHAR *)(const FSxCHAR *)ttt] ) == -1 )
	        pik = 3;
        }
    return(pik);
    }
/*
* return 1, kui ty-le vo~iks "ne" otsa kleepida, et saada omaduss. tu"ve
*/
int MORF0::sobiks_ne( FSXSTRING *ty, int pikkus )
    {
    int  j;
    int  silpe, silp;
    FSXSTRING tyvi;

    silpe = 0;
    silp = VANA_SILP;
    tyvi = (const FSxCHAR *)(ty->Left(pikkus));
    for (j=0; j < pikkus; j++)
	    {
        if (TaheHulgad::OnTaishaalik(tyvi[j]))
	        {
	        if (silp == VANA_SILP)
		        silpe++;
	        silp = UUS_SILP;
	        }
	    else
	        {
	        silp = VANA_SILP;
	        }
	    }
    if ( silpe < 2 )    /* liiga lu"hike so~na */
    	return 0;
    if ( TaheHulgad::OnLopus(&tyvi, FSxSTR("akt")) )
    	return 1;       /* na"it. "...iil" */
    if ( TaheHulgad::OnTaishaalik(tyvi[pikkus-3]) &&
	      TaheHulgad::OnTaishaalik(tyvi[pikkus-2]) &&
	       !TaheHulgad::OnTaishaalik(tyvi[pikkus-1]) )
    	return 1;       /* na"it. "...iil" */
    return 0;
    }

/*
* leiab sona, mille algvorm on ainsuse omastav, jrk nr tabelis omastavad[];
*/
int MORF0::omastavanr( FSXSTRING *mis )
    {
    return ( loend.omastavad.Get((FSxCHAR *)(const FSxCHAR *)(*mis)) ? 1 : -1 );
    }

/*
* kui tyvi on muutumatu s�na tyvi, siis return 1
*/
int MORF0::on_muutumatu(KOMPONENT *tyvi)
    {
    KOMPONENT *lopp;
    int llnr, ffnr;

    lopp = tyvi->komp_jargmine;
    if (!lopp)
        return 0;

	//llnr = (groups[lopp->lgr].gr_algus << 8) | groups[lopp->lgr].gr_lopp;
    llnr = KaksYheks(groups[lopp->lgr].gr_algus, groups[lopp->lgr].gr_lopp);
    ffnr = (unsigned char)(fgr[homo_form * llnr]);
	if (!ffnr)                
        return 1;
    return 0;
    }
