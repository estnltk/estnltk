
#include "mrf-mrf.h"

// arvamise va'rk

int MORF0::arvax(MRFTULEMUSED *tulemus, FSXSTRING *S6nna)
    {
    int res, tmp;
    FSXSTRING S6na1;
    int S6naPikkus;
    int S6naPikkus1;

    S6naPikkus = S6nna->GetLength();
    if ( S6naPikkus <= 0 )  // voimatu seis 
	    return ALL_RIGHT;

    // kontr, kas sõna on mingi 'mittesõna' (nt. (!))  

    res = arvamitte( tulemus, S6nna);
    if (res > ALL_RIGHT)
	    return res; 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     

    S6na1 = *S6nna;
    S6na1.TrimLeft(TaheHulgad::s_punktuatsioon);
    S6na1.TrimRight(TaheHulgad::punktuatsioon);
    S6naPikkus1 = S6na1.GetLength();

    if ( S6naPikkus1 == 0 )
	    {   // kui pärast sulgude jms eemaldamist ei jäägi midagi alles 
	    return ALL_RIGHT;
	    }
    if (S6na1 != *S6nna) /* oli sodine sona */
        {
	    mrfFlags.On(MF_LYHREZH); // ei oleta suurtähelisi lyhendeid 
	    res = chkx( tulemus, &S6na1, S6naPikkus1, 100, &tmp );
	    if (res != ALL_RIGHT)
	        return res;
        if (tulemus->on_tulem())
            return res;
        }
    // äkki on nt 'segamisest' (esimene ' on juba eemaldatud)
    if (S6na1[S6naPikkus1-1] == APOSTROOF)
        {
        FSXSTRING S6na2;

        S6na2 = S6na1.Left(S6naPikkus1-1);
        if (TaheHulgad::PoleMuudKui(&S6na2, &(TaheHulgad::vaiketht)))
            {
	        res = chkx( tulemus, &S6na2, S6na2.GetLength(), 100, &tmp );
	        if (res != ALL_RIGHT)
	            return res;
            if (tulemus->on_tulem())
                return res;
            if(Barvaww( tulemus, &S6na2, S6na2.GetLength(), KOIK_LIIGID )==false) 
	            return CRASH; // viga!
            if (tulemus->on_tulem())
	            return ALL_RIGHT;     // oli korrektne s“na 
            }
        }
	mrfFlags.Off(MF_LYHREZH); // oleta ka suurtähelisi lyhendeid 

    // proovime, kas on va'iketa'heline lyhend 

    res = arvalyh1( tulemus, &S6na1);
    if (res > ALL_RIGHT)
	    return res; 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s“na */

    // proovime, kas sh asendamine teeb sona arusaadavaks
    res = arvash1( tulemus, &S6na1);
    if (res > ALL_RIGHT)
	    return res; 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne sõna 

    // kontr, kas sõna on suurtäheline lyh käändelõpuga 

    res = chklyh3( tulemus, &S6na1, 1, &tmp );
    if (res > ALL_RIGHT)
	    return res; 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne sõna 

    // kontr, kas sõna on SonaSona v sooona

    res = arvavi1( tulemus, &S6na1, S6naPikkus1 );
    if (res > ALL_RIGHT)
	    return res; // viga! 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne s“na 

    // kontr, kas s“na on ha'a'litsus 

    res = arvai( tulemus, &S6na1, S6naPikkus1 );  
    if (res > ALL_RIGHT)
	    return res; // viga!
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne s“na 

    // kontr, kas s“na on '-' sisaldav säna, nt. bla-bla-sona

    res = arvahy1( tulemus, &S6na1, S6naPikkus1 );  
    if (res > ALL_RIGHT)
	    return res; // viga!
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne s“na 
    
    // proovime, kas on suurta'heline lyhend 

    res = arvalyh2( tulemus, &S6na1);
    if (res > ALL_RIGHT)
	    return res; 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     /* oli korrektne s“na */
    // kontr, kas sõna on mingi produktiivsesse muuttüüpi kuuluv sõna

    if(Barvaww( tulemus, &S6na1, S6naPikkus1, KOIK_LIIGID )==false)
	    return CRASH; // viga!
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne s“na 

    // kontr, kas s“na on suurt„heline lyh ilma k„„ndeläputa 

    res = chklyh4( tulemus, &S6na1, S6naPikkus1 );   // vt punktita säna 
    if (res > ALL_RIGHT)
	    return res; // viga! 
    if (tulemus->on_tulem())
	    return ALL_RIGHT;     // oli korrektne s“na 

    // lihtsalt oletame et on lyhend
    tulemus->Add((const FSxCHAR *)S6na1, FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); 

    return ALL_RIGHT;
    }

bool MORF0::Barvaww(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus1, const FSxCHAR *lubatavad_sl)
    {
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    int res;
    FSXSTRING S6na1;

    // kontr, kas s“na on tundmatu pa'risnimi, milles lopp '-ga 

    S6na1 = *S6na;
    if (oletajaDct.sobiks_sonaks(&S6na1))
        {
        if (TaheHulgad::AintSuured(&S6na1))
            {
            S6na1.MakeLower();
            TaheHulgad::AlgusSuureks(&S6na1);
            }
        }
    res = arvapn2( tulemus, &S6na1, S6naPikkus1 );  
    if (res > ALL_RIGHT)
	    return false; // viga! 
    if (tulemus->on_tulem())
	    return true;     // oli korrektne s“na 

    // kontr, kas s“na on analyysitav suf ja lopu kaudu
    // leitakse sona vo'imalikud lopud 
    res = arvasuf1(&ctoo_variandid.ptr, &S6na1, S6naPikkus1, &csobivad_variandid.ptr);  
    if (res > ALL_RIGHT)
	    return false; // viga! 
    if (csobivad_variandid.ptr)
        {
        variandid_tulemuseks(tulemus, lubatavad_sl, &csobivad_variandid.ptr);
        //ahelad_vabaks(&ctoo_variandid.ptr);       //destruktoris
        //ahelad_vabaks(&csobivad_variandid.ptr);   //destruktoris
        if (tulemus->on_tulem() && TaheHulgad::SuurAlgustaht(&S6na1))
            {
            tulemus->TulemidNimeks(LIIK_YLDNIMI);
            }
	    return true;     // oli korrektne s“na 
        }
 
    // kontr, kas s“na on tundmatu nimiso'na, mis analüüsitav tagumise otsa kaudu 
    //if (!S6na1.OnSuur(0)) // pärisnimede analüüs läheks enamasti nihu vist
        {
        res = arvans1( tulemus, &S6na1, S6naPikkus1, &ctoo_variandid.ptr);  
        if (res > ALL_RIGHT)
	        return false; // viga! 
        if (tulemus->on_tulem())
            {
            //ahelad_vabaks(&ctoo_variandid.ptr);   //destruktoris
	        return true;     // oli korrektne s“na 
            }
        }
    if (ctoo_variandid.ptr == 0) // sõna ei saa üldse analüüsida kui mingit sõna
		return true;

    // kontr, kas s“na on tundmatu pärisnimi, nimiso'na v verb 

    res = arvans2( tulemus, &S6na1, S6naPikkus1, &ctoo_variandid.ptr, lubatavad_sl );  
    if (res > ALL_RIGHT)
	    return false; // viga! 
    //ahelad_vabaks(&ctoo_variandid.ptr);   //destruktoris
    if (tulemus->on_tulem())
        {
        tulemus->SortUniq();  // sest tabelist tuleb samu algvorme mitmest kirjest...
	    return true;     // oli korrektne s“na 
        }
    return true;
    }
