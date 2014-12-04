
/**
* kontrollib, kas S6na on '-' sisaldav OK sona;
*
* näiteks:
* metsa-, munitsipaal-, lugemis-, v�ib-olla, aero-, -
*
*/
#include "mrf-mrf.h"
//#include "valjatr.h"

int MORF0::chkhy2(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int maxtasand, int *tagasi)
    {
    int i, j;
    int res=0;
    char rezz, rezz1;
    struct lisa {
        const FSxCHAR *lubatud_lopp;
        const FSxCHAR *lubatud_sl;
        const int mitu_eemaldada;
        const FSxCHAR *otsa_panna;
        } lisakatse[3] = {
    { FSxSTR("0"), FSxSTR("A"), 2, FSxSTR("ne") },  /* +ne */
    { FSxSTR("t"), FSxSTR("AS"), 0, FSxSTR("t") },  /* is+t */
    { FSxSTR("d"), FSxSTR("AS"), 0, FSxSTR("d") } }; /* +d */
    int katsenr;
    const FSxCHAR *lubatud_liik;
    int viimane, lopus_kriips;
    int tmp;
    int mitu;
    int sobiv_an;
    CVARIANTIDE_AHEL ctoo_variandid, csobivad_variandid;
    FSXSTRING S6na = *S6nna;
    int k;
    FSXSTRING algus;
    FSXSTRING kriips;
    FSXSTRING lopp;
    FSXSTRING pisialgus;
    MRFTULEMUSED ette;
    FSXSTRING ettestr;
    k = S6na.Find((FSxCHAR)'-');
    if (k == -1)
        k = S6na.Find((FSxCHAR)'/');
    if (k == -1)
	    return ALL_RIGHT;    // ei sisalda '-' ega '/'
    algus = S6na.Left(k);
    kriips = S6na.Mid(k, 1);
    lopp = S6na.Mid(k+1);
    if (k==0 && kriips == FSxSTR("-") ) // -sona
	    {
		if (lopp.GetLength()<1)
			return ALL_RIGHT;
	    res = chkwrd(tulemus, &lopp, lopp.GetLength(), maxtasand, tagasi, KOIK_LIIGID/*MITTE_VERB*/);
	    if (res > ALL_RIGHT)
	        return res; /* viga! */
	    if (!tulemus->on_tulem())    
            {
            FSXSTRING pisilopp;
            pisilopp = lopp;
            pisilopp.MakeLower();
	        res = chkwrd(tulemus, &pisilopp, pisilopp.GetLength(), maxtasand, tagasi, KOIK_LIIGID);
	        if (res > ALL_RIGHT)
	            return res; /* viga! */
            }
        if (maxtasand < 4)  // soovitaja pärast HJK 10.06.2005
            return ALL_RIGHT;
	    if (!tulemus->on_tulem())    /* polnud -sona */
	        {
            *tagasi = 4;
		    res = chklyh4(tulemus, &lopp, lopp.GetLength()); /* nt. -E */
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            }
	    return ALL_RIGHT;
	    }

    if (maxtasand < 4)  // soovitaja p�rast HJK 10.06.2005
        return ALL_RIGHT;
 
    if (S6na.GetLength() == 2 && k == 1 && kriips == FSxSTR("-") && TaheHulgad::eestitht.Find(S6na[0])!=-1) // a-
        {
        tulemus->Add( (const FSxCHAR *)algus, FSxSTR("0"), FSxSTR(""), FSxSTR("Y"), FSxSTR("?, ")); /* parema puudusel */
        *tagasi = 4;
        return ALL_RIGHT;
        }
      /* sona-sona-sona-sona... */
    viimane = 0;
    lopus_kriips = 0;
    lopp = S6na;
    rezz = mrfFlags.Chk(MF_ALGV);  /* algvormi rezhiimi lipp */
    rezz1 = mrfFlags.Chk(MF_GENE); /* gene rezhiimi lipp */
	for (mitu=0 ;; mitu++)
	    {
        MRFTULEMUSED ajutine_tulemus;
        MRFTUL t;
        sobiv_an = -1;
        k = lopp.Find(kriips);
	    if ( k==-1 )           /* viimane sonaosa */
            {
            algus = lopp;
            lopp = FSxSTR("");
            viimane = 1;
            }
        else
            {
            algus = lopp.Left(k);
            lopp = lopp.Mid(k+1);
            if (lopp.GetLength()==0) // viimane sonaosa; sona-
                {
                viimane = 1;
                lopus_kriips = 1;
                }
            }
        if (algus.GetLength() > STEMLEN || algus.GetLength() < 1)
			{
            mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
            mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
	        return ALL_RIGHT; // tulemust pole vaja vabastada
			}
        pisialgus = algus;
        pisialgus.MakeLower();
        if (algus == FSxSTR("ist") 
            || algus == FSxSTR("lase")
            || algus == FSxSTR("lise")
            || algus == FSxSTR("na")
            || algus == FSxSTR("st")) // need ei sobi s�naks
            {
            mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
            mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
	        return ALL_RIGHT; // tulemust pole vaja vabastada
            }
        lubatud_liik = KOIK_LIIGID;
        if (viimane) 
            {
            mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
            mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
//            if ( ChIsUpper(*s) && !ChIsUpper(*(s+1))) /* viimane so'na suurta'heline */
            if (TaheHulgad::SuurAlgustaht(&algus))
                lubatud_liik = FSxSTR("SABCUNOPHGY");    /* juhuks, kui viimane algab suure ta'hega */
            if (lopus_kriips)  /* viimase lopus -, nt. nais- */
                {
                if (pisialgus == FSxSTR("kesk") || pisialgus == FSxSTR("puhke") || pisialgus == FSxSTR("inglis"))
                    {
                    ajutine_tulemus.Add((const FSxCHAR *)pisialgus, FSxSTR(""), FSxSTR(""), FSxSTR("S"), FSxSTR("?, ")); 
                    }
                lubatud_liik = FSxSTR("SABCUNOPHGDK"); 
                }
            }
        else
            { 
            mrfFlags.Off(MF_ALGV);    /* on vaja, et analu"u"siks nagu ilma algvormita */
            mrfFlags.Off(MF_GENE);    /* eemaldame GENE piirangud sonavormide valikule */
            }
        if (!ajutine_tulemus.on_tulem() 
             && nLopud.otsi_lyh_vorm((const FSxCHAR *)lopp) == NULL)
            {
            res = kchk1(&ctoo_variandid.ptr, &algus, algus.GetLength(), &csobivad_variandid.ptr, NULL,0); /* ty+lp */
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            ahelad_vabaks(&ctoo_variandid.ptr);
		    if (csobivad_variandid.ptr)
                {
                variandid_tulemuseks(&ajutine_tulemus, lubatud_liik, &csobivad_variandid.ptr);
                ahelad_vabaks(&csobivad_variandid.ptr);
                }
		    if (!ajutine_tulemus.on_tulem())
		        {
                if (TaheHulgad::AintSuured(&algus))
                    {
                    FSXSTRING suuralgus;
                    suuralgus = pisialgus;
                    TaheHulgad::AlgusSuureks(&suuralgus);
		            res = chkwrd(&ajutine_tulemus, &suuralgus, suuralgus.GetLength(), 1, tagasi, LIIK_PARISNIMI);
		            if (res > ALL_RIGHT)
		                return res; // viga! 
                    }
                }
		    if (!ajutine_tulemus.on_tulem())
		        {
		        res = chkwrd(&ajutine_tulemus, &pisialgus, pisialgus.GetLength(), 6, tagasi, lubatud_liik);
                if (res > ALL_RIGHT)
		            return res; /* viga! */
                }
            }
        if (viimane && ajutine_tulemus.on_tulem() && ette.on_tulem())
            {
            if (TaheHulgad::SuurAlgustaht(&algus))
                {
                ajutine_tulemus.TulemidNimeks(KOIK_LIIGID);
                }
            }

        if ( ( !ajutine_tulemus.on_tulem() && !viimane ) ||    /* ei saanud veel analyysitud */
              ( mitu==0 && ajutine_tulemus.Get_lopp(FSxSTR("0")) == -1 
                        && ajutine_tulemus.Get_vormid(FSxSTR("?, ")) == -1) )  /* v�i leia veel variante*/
		    {
            *tagasi = 1;
            if (pisialgus.GetLength() < PREFLEN)
                {
                i = preffnr((FSxCHAR *)(const FSxCHAR *)pisialgus);
	            if ( i != -1 )    // selline prefiks on olemas 
                    ajutine_tulemus.Add((const FSxCHAR *)pisialgus, FSxSTR(""), FSxSTR(""), FSxSTR("S"), FSxSTR("?, ")); // parema puudusel 
                }
            }
        if (ajutine_tulemus.on_tulem())
            {
            sobiv_an = ajutine_tulemus.Get_vormid(FSxSTR("sg g,")); /* eelistame sg g tyve */
            }
        if (!ajutine_tulemus.on_tulem()) /* ikka ei saanud veel analyysitud */
		    { /* kas on LYH-LYH... */
            if ( !viimane ) /*  */
                {
                mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
                mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
                FSXSTRING pisilopp;
                pisilopp = algus;
                pisilopp += kriips;
                pisilopp += lopp;
		        res = chklyh2(&ajutine_tulemus, &pisilopp); /* nt. MM-il */
		        if (res > ALL_RIGHT)
		           return res; /* viga! */
                if (!ajutine_tulemus.on_tulem()) /* ikka ei saanud veel analyysitud */
                    {
		            res = chknr2(&ajutine_tulemus, &pisilopp); /* nt. uraan-253-s */
		            if (res > ALL_RIGHT)
		               return res; /* viga! */
                    }
                if (!ajutine_tulemus.on_tulem()) /* ikka ei saanud veel analyysitud */
                    {
		            res = chklyh3(&ajutine_tulemus, &pisilopp, 1, &tmp); 
		            if (res > ALL_RIGHT)
		               return res; /* viga! */
                    }
                if (ajutine_tulemus.on_tulem())
                    viimane = 1;
                else
                mrfFlags.Off(MF_ALGV);    /* on vaja, et analu"u"siks nagu ilma algvormita */
                mrfFlags.Off(MF_GENE);    /* eemaldame GENE piirangud sonavormide valikule */
                }
            }
        if (!ajutine_tulemus.on_tulem())
            {
		    res = chklyh3(&ajutine_tulemus, &algus, 1, &tmp); /* nt. MMil */
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            }
        if (!ajutine_tulemus.on_tulem())
            {
		    res = chklyh4(&ajutine_tulemus, &algus, algus.GetLength()); /* nt. MM */
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            }
        if (!ajutine_tulemus.on_tulem() && algus.GetLength()==1)
            {
		    res = chklyh0(&ajutine_tulemus, &algus, algus.GetLength()); // nt. b; teeb valesti DV-d
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            }
        if (!ajutine_tulemus.on_tulem()) /* ikka ei saanud veel analyysitud */
            {
            if (mitu > 0) // et v�ltida juhtumeid nagu 253-uraan
		        res = chknr2(&ajutine_tulemus, &algus); /* nt. uraan-253 */
		    if (res > ALL_RIGHT)
		       return res; /* viga! */
            }
        if (ajutine_tulemus.on_tulem() && !viimane)
            {
            if (sobiv_an == -1)
                sobiv_an = 0;      /* v�tame suvaliselt esimese tyve */
// parandada
//            if ( ajutine_tulemus.Get(tul_tyvi, tul_lopp, tul_sl, tul_vorm, &sobiv_an) == NULL )
//                return ILL_LINE_LEN;   // seda ei saa olla; suvaline veateade 
            t.Start(*(ajutine_tulemus[sobiv_an]));
            }
        if (!ajutine_tulemus.on_tulem() /* ikka ei saanud veel analyysitud */
              || (TaheHulgad::OnLopus(&pisialgus, FSxSTR("is")) /*(!strcmp(s1+s1_pik-2, "is")*/ && viimane && lopus_kriips)) /* voi on see nagu kahtlane */
            {
            mrfFlags.Off(MF_ALGV);    /* on vaja, et analu"u"siks nagu ilma algvormita */
            mrfFlags.Off(MF_GENE);    /* eemaldame GENE piirangud sonavormide valikule */
            if (sobiks_ne(&pisialgus, pisialgus.GetLength()))
                katsenr = 0;
            else if (pisialgus.GetLength() > 4 && 
                (TaheHulgad::OnLopus(&pisialgus, FSxSTR("is")) || TaheHulgad::OnLopus(&pisialgus, FSxSTR("las"))))
                katsenr = 1;
            else
                katsenr = 2;
            ///////////////////////////////// pooleli 
            MRFTULEMUSED ajutine_tulemus1;
            FSXSTRING katse;
            katse = pisialgus;
            katse += lisakatse[katsenr].otsa_panna;
            res = chkwrd(&ajutine_tulemus1, &katse, katse.GetLength(), 6, tagasi, lisakatse[katsenr].lubatud_sl);
	        if (res > ALL_RIGHT)
		        return res; /* viga! */
	        if (ajutine_tulemus1.on_tulem())   /* oli sona_ne, sona_is+t v sona+d */
                {
                j = ajutine_tulemus1.Get_lopp(lisakatse[katsenr].lubatud_lopp);
                if (j != -1 ) /* analyys sobis */
                    {
                    t.Start(*(ajutine_tulemus1[j]));
                    t.tyvi = (const FSxCHAR *)(t.tyvi.Left(t.tyvi.GetLength()-lisakatse[katsenr].mitu_eemaldada));
                    t.lopp = FSxSTR("0");
                    ajutine_tulemus.Add((t.tyvi), FSxSTR(""), FSxSTR(""), (const FSxCHAR *)t.sl, FSxSTR("?, "));
                    }
                }
            }
        if (!ajutine_tulemus.on_tulem())
            {
            mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
            mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
            return ALL_RIGHT;
            }
        if (!viimane)
            {
            ette.AddClone(t);
            }
        else
            {
            tulemus->Move2Tail(&ajutine_tulemus);
            break;
            }
        }
    mrfFlags.OnOff(MF_ALGV, rezz);  /* analyys nagu korgemalt ette antud */
    mrfFlags.OnOff(MF_GENE, rezz1); /* analyys nagu korgemalt ette antud */
    if (tulemus->Get_sl( FSxSTR("H") ) != -1 
        && TaheHulgad::OnSuur(S6nna, 0)) /* vaja panna va'ljundisse suured ta'hed tagasi */
        {    
        ette.AlgusedSuureks();
        }
    if (ette.on_tulem())
        tulemus->PlakerdaKokku(&ette, (const FSxCHAR *)kriips, &mrfFlags);
    if (*tagasi < 4)
        *tagasi = 4;
    return ALL_RIGHT;
    }

