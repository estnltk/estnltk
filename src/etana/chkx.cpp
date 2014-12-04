
#include <string.h>

#include "mrf-mrf.h"
//#include "valjatr.h"

// kontrollin, kas on nt tema(kese)le

int MORF0::chksuluga(MRFTULEMUSED *tul, FSXSTRING *S6nna, int maxtasand)
    {
    int res, s1, s2;
    FSXSTRING sona;

    sona = *S6nna;
    for (;;)
        {
        s1 = sona.Find(FSxSTR("("));
        s2 = sona.ReverseFind(FSxSTR(")"));
        if (s1 == -1 || s1 > s2)       // polegi sulge kujul ()
            return ALL_RIGHT;
        if (s1 == 0 && s2 == sona.GetLength()-1) // (sona)
            sona = sona.Mid(1, sona.GetLength()-2);
        else
            break;
        }

    if (TaheHulgad::PoleMuudKui( &sona, &(TaheHulgad::suludmatemaatika))==true)
        return ALL_RIGHT;

    FSXSTRING son1, son2;
    MRFTULEMUSED tul1, tul2;
    
    son1 = sona.Mid(0,s1);
    son1 += sona.Mid(s1+1, s2-s1-1);
    son1 += sona.Mid(s2+1);
    son2 = sona.Mid(0,s1);
    son2 += sona.Mid(s2+1);
    if (son1.GetLength() < 1)
        return ALL_RIGHT;
    TaheHulgad::Puhasta(&son1);
    if (son1.GetLength() < 1)
        return ALL_RIGHT;
    if (son2.GetLength() < 1)
        return ALL_RIGHT;
    TaheHulgad::Puhasta(&son2);
    if (son2.GetLength() < 1)
        return ALL_RIGHT;
	res = chkx( &tul1, &son1, son1.GetLength(), maxtasand, &(tul1.tagasiTasand) );
	if (res == ALL_RIGHT && tul1.on_tulem())
	    res = chkx( &tul2, &son2, son2.GetLength(), maxtasand, &(tul2.tagasiTasand) );
	if (res != ALL_RIGHT)
	    return res;
    if (tul2.on_tulem())
        {
        tul->Move2Tail(&tul1);
        tul->Move2Tail(&tul2);
        }
    return ALL_RIGHT;
    }

// kontrollib, kas S6nna on eesti k. s�na
//
//	res !=  ALL_RIGHT -- viga
//	res ==  ALL_RIGHT
//        resultaat pannakse ahelasse TUL **tulemus (vt valjatr.cpp)


int MORF0::chkx(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi)
    {
    int res;
    FSXSTRING S6na1, S6na2, S6na3;
    int tagasi1;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;

    //int i = mrfFlags.Chk(MF_ARAROOMA);

    if ( S6naPikkus <= 0 )
	    {   /* kui p�rast sulgude jms eemaldamist ei j��gi midagi alles */
	    return ALL_RIGHT;
	    }

    *tagasi = 1; /* mittesonade analyysi jaoks vaikimisi va'a'rtus */

    /* kontr, kas s�na on mingi 'mittes�na' (nt. % & -)  */

    res = chkmitte( tulemus, S6nna, S6naPikkus );
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    /* kontr, kas s�na on 1-suurt�hel. lyh */

    res = chklyh0( tulemus, S6nna, S6naPikkus );
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    /* kontr, kas s�na on nr sisald. sona (1. korda) */

    res = chknr2( tulemus, S6nna);
    if (res > ALL_RIGHT)
    	return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    S6na1 = *S6nna;
    if (TaheHulgad::OnLopus(&(S6na1), FSxSTR(".")))
        {
		if (S6na1.GetLength()==1)
	        return ALL_RIGHT;     /* ongi ainult . */
        S6na1 = (const FSxCHAR *)(S6na1.Mid(0, S6na1.GetLength()-1)); // l�pust punkt maha
        res = chknr2( tulemus, &S6na1); // 2. korda; et poleks vahet kas 2-aastane v 2-aastane.
        if (res > ALL_RIGHT)
    	    return res; /* viga! */
        if (tulemus->on_tulem())
	        return ALL_RIGHT;     /* oli korrektne s�na */
        }

    /* kontr, kas s�na on muutumatu lyh */

    res = chklyh1( tulemus, &S6na1);
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    /* kontr, kas s�na on k��ndel�puga lyh */

    res = chklyh2( tulemus, &S6na1);
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    /* kontr, kas s�na on suurt�heline lyh k��ndel�puga */

    res = chklyh3( tulemus, &S6na1, maxtasand, tagasi );
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    *tagasi = 1; /* mittesonade analyysi jaoks vaikimisi va'a'rtus */
    /* kontr, kas s�na on nr sisaldav va"rk */
    S6na3 = S6na1;
    S6na3.MakeLower();

    if (S6na3 != S6na1)
        {
        res = kchk1(&ctoo_variandid.ptr, &S6na1, S6na1.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
        if (res > ALL_RIGHT)
	        return res; /* viga! */
        if (csobivad_variandid.ptr)
            {
            variandid_tulemuseks(tulemus, KOIK_LIIGID, &csobivad_variandid.ptr);
            }
        ahelad_vabaks(&ctoo_variandid.ptr);
        ahelad_vabaks(&csobivad_variandid.ptr);
        if (!tulemus->on_tulem())
            {
            if (TaheHulgad::AintSuured(&S6na1)) /* AAFRIKA */
                { /* kontr, kas s�na on geograafiline nimi + lp */
                S6na2 = S6na3;
                //S6na2[0] = S6na1[0];
                S6na2.SetAt(0, S6na1[0]);
                res = kchk1(&ctoo_variandid.ptr, &S6na2, S6na2.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
                if (res > ALL_RIGHT)
	                return res; /* viga! */
                if (csobivad_variandid.ptr)
                    {
                    variandid_tulemuseks(tulemus, LIIK_PARISNIMI, &csobivad_variandid.ptr);
                    }
                ahelad_vabaks(&ctoo_variandid.ptr);
                ahelad_vabaks(&csobivad_variandid.ptr);
                }
            }
        if (tulemus->on_tulem())
            {  
            if ( !mrfFlags.Chk(MF_SPELL) )
                { /* ehk on ka mitte-pa'risnimi? */
                ahelad_vabaks(&ctoo_variandid.ptr);
                ahelad_vabaks(&csobivad_variandid.ptr);
                res = kchk1(&ctoo_variandid.ptr, &S6na3, S6na3.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
                if (res > ALL_RIGHT)
	                return res; /* viga! */
                if (csobivad_variandid.ptr)
                    {
                    variandid_tulemuseks(tulemus, KOIK_LIIGID, &csobivad_variandid.ptr);
                    }
                }
            //ahelad_vabaks(&ctoo_variandid.ptr);       //destruktoris
            //ahelad_vabaks(&csobivad_variandid.ptr);   //destruktoris
        	return ALL_RIGHT;     /* oli korrektne s�na */
            }
        }

    /* kontr, kas s�na on tavaline eesti k. s�na */
    if (TaheHulgad::PoleSuuri(&S6na1)
        || TaheHulgad::SuurAlgustaht(&S6na1)
        || TaheHulgad::AintSuuredjaKriipsud(&S6na1))
	    {
        res = chkwrd(tulemus, &S6na3, S6na3.GetLength(), maxtasand, tagasi, KOIK_LIIGID);
	    if (res > ALL_RIGHT)
	        return res; /* viga! */
	    if (tulemus->on_tulem())    /* oli norm. eesti k. s�na */
            {
            if( !mrfFlags.Chk(MF_SPELL) )
                { /* kontr, kas s�na voiks olla ka s�na+GI */
                MRFTULEMUSED ajutine_tulemus;
                FSXSTRING lubatud_ki_liigid = KI_LIIGID;
                if (tulemus->Get_sl(FSxSTR("P")) != -1)
                    lubatud_ki_liigid.Remove((FSxCHAR)'P');
                if (tulemus->Get_sl(FSxSTR("D")) != -1)
                    lubatud_ki_liigid.Remove((FSxCHAR)'D');
                if ((dctLoend[0])[(FSxCHAR *)(const FSxCHAR *)S6na3] == -1) // pole selline sona, millel peabki ki otsas olema 
                    res = chkgi( &ajutine_tulemus, &S6na3, S6na3.GetLength(), *tagasi - 1, &tagasi1, (FSxCHAR *)(const FSxCHAR *)lubatud_ki_liigid );
                if (res > ALL_RIGHT)
	                return res; /* viga! */
                tulemus->Move2Tail(&ajutine_tulemus);
                }
	        return ALL_RIGHT;
            }
        else
            {  /* kontr, kas s�na on s�na+GI */
            res = chkgi( tulemus, &S6na1, S6na1.GetLength(), maxtasand, tagasi, KI_LIIGID );   /* vt sona, millel 1. t voib olla suur, teised v */
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            if (tulemus->on_tulem())
	            return ALL_RIGHT;     /* oli korrektne s�na */
            }
	    }

    /* kontr, kas s�na on suurt�hega algav '-' sisaldav s�na*/

    *tagasi = 1; /* mittesonade analyysi jaoks vaikimisi va'a'rtus */

    res = chkhy1( tulemus, &S6na1); /* vt punktita s�na */
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */
    
    /* kontr, kas s�na on nt Ladina-Ameerika */

    res = chkhy2( tulemus, &S6na1, maxtasand, tagasi ); /* vt punktita s�na */
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    if (maxtasand < 4) 
        return ALL_RIGHT;
    /* kontr, kas s�na on suurt�heline lyh ilma k��ndel�puta */

    *tagasi = 4;
    res = chklyh4( tulemus, &S6na1, S6na1.GetLength() );   /* vt punktita s�na */
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s�na */

    return ALL_RIGHT;
    }

/*
 * kontrollib, kas S6na on eesti k. s�na

	chkwrd !=  ALL_RIGHT -- viga
	chkwrd ==  ALL_RIGHT
    tulemus on muutujas tul
 */


int MORF0::chkwrd(MRFTULEMUSED *tul, FSXSTRING *S6nna, int S6naPikkus, 
                        int maxtasand, int *tagasi, const FSxCHAR *lubatavad_sl)
    {
    int res;
    CVARIANTIDE_AHEL csobivad_variandid;

    res = chkww(S6nna, S6naPikkus, maxtasand, tagasi, &csobivad_variandid.ptr);
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (csobivad_variandid.ptr)
        {
        variandid_tulemuseks(tul, lubatavad_sl, &csobivad_variandid.ptr);
        //ahelad_vabaks(&sobivad_variandid);    //destruktoris
        }
	return ALL_RIGHT;     /* oli korrektne s�na */
    }

/*
* nn suur lyliti:
* kontrollib, alates lihtsamatest struktuuridest, kas S6na on eesti k. s�na
*/

int MORF0::chkww(FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi, VARIANTIDE_AHEL **sobivad_variandid)
    {
    int res;
    CVARIANTIDE_AHEL ctoo_variandid;
	*tagasi=1;
    //TV char *paha_koht=NULL;
    /* kontr, kas s�na on tyvi+lp */
    //TV paha_koht = init_hjk_cxx(S6naPikkus, paha_koht);
    //if (!paha_koht)
    //    return CRASH;
    char paha_koht[(STEMLEN+1)*(STEMLEN+1)];
    init_hjk_cxx(S6naPikkus, paha_koht, sizeof(paha_koht));

    res = kchk1(&ctoo_variandid.ptr, S6nna, S6naPikkus, sobivad_variandid, paha_koht,sizeof(paha_koht)); /* ty+lp */
    if (res > ALL_RIGHT)
	    return res; /* viga! */
    if (!ctoo_variandid.ptr)  /* ei saa kuidagi olla eesti k sona */
        {
        //close_hjk_cxx(paha_koht);
	    return ALL_RIGHT;
        }
    if (!*sobivad_variandid)
        {
        if (mrfFlags.Chk(MF_EILUBATABU)) // nt soovitaja puhul tabus�nad pole lubatud
        // et ei juhtuks nii, et kuigi s�nastikus olev liits�na on tabu, aga kuna osas�nad on OK, 
        // siis edaspidi saab ikka OK anal��si
        // selleks vt veelkord s�nastikku, kusjuures luban tabus�nu
            {
            int re;
            CVARIANTIDE_AHEL cto_variandi, csobiva_variandi;
            mrfFlags.Off(MF_EILUBATABU);
            
            //char *pah_koh=NULL;
            //pah_koh = init_hjk_cxx(S6naPikkus, pah_koh);
            //if (!pah_koh)
            //    return CRASH;
            char pah_koh[(STEMLEN+1)*(STEMLEN+1)];
            init_hjk_cxx(S6naPikkus, pah_koh, sizeof(pah_koh));
            re = kchk1(&cto_variandi.ptr, S6nna, S6naPikkus, &csobiva_variandi.ptr, pah_koh,sizeof(pah_koh)); /* ty+lp */
            if (re > ALL_RIGHT)
                return re; /* viga! */
            mrfFlags.On(MF_EILUBATABU);
            //ahelad_vabaks(&to_variandi); //destruktoris
            if (csobiva_variandi.ptr)  // ahhaa, tabu liits�na s�nastikus!
                {
                //close_hjk_cxx(pah_koh);
                //ahelad_vabaks(&sobiva_variandi); //destruktoris
                return ALL_RIGHT;
                }
           //close_hjk_cxx(pah_koh);
           //ahelad_vabaks(&sobiva_variandi); //destruktoris
           }
        if (maxtasand >= 2) 
            {
             /* kontr, kas s�na on tyvi+suf+lp */
	        *tagasi=2;
            res = kchk2(&ctoo_variandid.ptr, sobivad_variandid, paha_koht,sizeof(paha_koht)); /* ty+suf */
            if (res > ALL_RIGHT)
    	        return res; /* viga! */
            }
        }
    if (!*sobivad_variandid)
        {
        if (maxtasand >= 3) 
            {
            /* kontr, kas s�na on pref+tyvi+lp */
	        *tagasi=3;
            res = kchk30(&ctoo_variandid.ptr, S6nna, S6naPikkus, sobivad_variandid, paha_koht,sizeof(paha_koht));  /* pref+ty */
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        }
    if (!*sobivad_variandid)
        {
        if (maxtasand >= 4) 
            {
            /* kontr, kas s�na on tyvi1+tyvi2+lp; tyvi1+tyvi2+suf+lp */
	        *tagasi=4;
            res = kchk4(&ctoo_variandid.ptr, S6nna, S6naPikkus, sobivad_variandid, 
                paha_koht, sizeof(paha_koht));
//{
//printf("DB:%s:%d\n", __FILE__,__LINE__);
//MRFTULEMUSED dbTul;
//variandid_tulemuseks(&dbTul, KOIK_LIIGID, sobivad_variandid);
//}
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        }
    if (!*sobivad_variandid)
        {
        if (maxtasand >= 5) 
            {
            /* kontr, kas s�na on pref+tyvi+suf+lp */
	        *tagasi=5;
            res = kchk33(&ctoo_variandid.ptr, sobivad_variandid, paha_koht,sizeof(paha_koht)); /* pref+ty+suf */
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        }
    if (!*sobivad_variandid)
        {
        if (maxtasand >= 5) 
            {
            /* kontr, kas s�na on tyvi1+vsuf+tyvi2+[?suf+?]lp  */
	        *tagasi=5;
            res = kchk5(&ctoo_variandid.ptr, S6nna, S6naPikkus, sobivad_variandid, paha_koht,sizeof(paha_koht)); 
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        }
    if (!*sobivad_variandid)
        {
        if (maxtasand >= 6) 
            {
            /* kontr, kas s�na on tyvi1+tyvi2+tyvi3+[?suf+?]lp  */
	        *tagasi=6;
            res = kchk6(&ctoo_variandid.ptr, S6nna, S6naPikkus, sobivad_variandid, 
                paha_koht, sizeof(paha_koht)); 
            if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        }

    /* kontr, kas s�na on pref+j�r.k+lp */

    if (maxtasand < 7)    /*  rohkem ei vt */
        {
        //close_hjk_cxx(paha_koht);
        //ahelad_vabaks(&too_variandid); //destruktoris
	    return ALL_RIGHT;
        }

    /* kontr, kas s�na on pref|tyvi1 + liits�na */

    //close_hjk_cxx(paha_koht);
    //ahelad_vabaks(&too_variandid); //destruktoris
	return ALL_RIGHT;
    }

/* 
* kontr, kas s�na on s�na+GI 
*/

int MORF0::chkgi(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi, const FSxCHAR *lubatavad_sl)
    {
    int res;
    FSXSTRING S6na3, ki;
    FSxCHAR enne_ki;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;

    if (S6naPikkus < 4)       /* pole norm. eesti k. s�na + GI */
	    return ALL_RIGHT;

    S6na3 = *S6nna;
    S6na3.MakeLower();
    ki = (const FSxCHAR *)(S6na3.Right(2));
    enne_ki = S6na3[S6na3.GetLength()-3];
    if ( !(     // pole nii, et...
        (ki == FSxSTR("ki") && TaheHulgad::OnHelitu(enne_ki))  ||    // enne 'ki' helitu h��lik
        (ki == FSxSTR("gi") && !TaheHulgad::OnHelitu(enne_ki)) ||    // enne 'gi' heliline h��lik
        ((ki == FSxSTR("ki") || ki == FSxSTR("gi")) && (enne_ki == V_SH || enne_ki == V_ZH)) // s'ja z' puhul on lubatud nii gi kui ki
        ) )
        return ALL_RIGHT;

    S6na3 = (const FSxCHAR *)(S6na3.Mid(0, S6na3.GetLength()-2));
	if ( (dctLoend[0])[(FSxCHAR *)(const FSxCHAR *)S6na3] != -1 )
		{
		return ALL_RIGHT; /*sonale ei tohi [gk]i otsa panna */
		}
    if (TaheHulgad::SuurAlgustaht(S6nna) || TaheHulgad::AintSuured(S6nna))
		{
        FSXSTRING S6na1;
        S6na1 = S6na3;
        S6na1[0] = *S6nna[0];
        res = kchk1(&ctoo_variandid.ptr, &S6na1, S6na1.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
		if (res > ALL_RIGHT)
		    return res; // viga! 
        ahelad_vabaks(&ctoo_variandid.ptr);
		}
    if(!mrfFlags.Chk(MF_SPELL) || !csobivad_variandid.ptr)
        res = chkww(&S6na3, S6na3.GetLength(), maxtasand, tagasi, &csobivad_variandid.ptr);
    if (csobivad_variandid.ptr)
        {
        variandid_tulemuseks(tulemus, lubatavad_sl, &csobivad_variandid.ptr);
	    if (tulemus->on_tulem())
            tulemus->LisaLoppudeleTaha((const FSxCHAR *)ki);
        //ahelad_vabaks(&too_variandid);        //destruktoris
        //ahelad_vabaks(&sobivad_variandid);    //destruktoris
	    return ALL_RIGHT;     /* oli korrektne s�na */
        }
    //ahelad_vabaks(&too_variandid);  //destruktoris
    return ALL_RIGHT;
    }
