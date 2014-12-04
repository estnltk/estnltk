
#include "fsxstring.h"
#include "tloendid.h"

/// V�rdle leksikograafiliselt t�htede koode
//
/// T�hekoodile v�ib viidata NULL-viit.
/// @return
/// - Kui m�lemad (s2 ja s2) on NULL-viidad, siis loeme v�rdseteks.
/// - Kui �ks NULL viit, teine mitte, siis NULL-viidaga v�iksem
/// - Kui kumbki pole NULL-viit, siis kasutame FSStrCmp() funktsiooni.
int FSStrCmpW0(
    const FSWCHAR *s1, ///< NULL viida korral alati v�iksem
    const FSWCHAR *s2  ///< NULL viida korral alati v�iksem
    )
    {
    if(s1==NULL && s2==NULL)
        return 0;
    if(s1==NULL)
        return -1;
    if(s2==NULL)
        return  1;
    return FSStrCmp(s1, s2);
    }

/// " \t\r\n"
const FSXSTRING TaheHulgad::wWhiteSpace(FSWSTR(" \t\r\n"));

/// "?<]~_" - k�igi lisakr�nksude string
const FSXSTRING TaheHulgad::lisaKr6nksudeStr(FSxSTR("?<]~_"));

/// "_" - liits�napiirim�rk
const FSXSTRING TaheHulgad::liitSonaPiir(FSxSTR("_"));   

/// "kpt"
const FSXSTRING TaheHulgad::kpt(FSxSTR("kpt"));

/// "gbd"
const FSXSTRING TaheHulgad::gbd(FSxSTR("gbd"));

/// "kptgbdfhs"
const FSXSTRING TaheHulgad::helitu(FSxSTR("kptgbdfhs"));

/// "hs"
const FSXSTRING TaheHulgad::hs(FSxSTR("hs"));

/// "lmnr"
const FSXSTRING TaheHulgad::lmnr(FSxSTR("lmnr"));

/// "aeiu"
const FSXSTRING TaheHulgad::aeiu(FSxSTR("aeiu"));

/// "aeiul" - oletamisel verbil�ppudele eelnevad t�hed (vt t�psemat kirjeldust)
//
/// Selleks, et kontrollida, kas tyve+sufiksi liitekoht ei sisalda kaash��liku�hendit,
/// milles m�ni kaash��lik on topelt (n�it. *'l�pp+lik', aga 'vasall+lik')
const FSXSTRING TaheHulgad::aeiul(FSxSTR("aeiul"));

/// "klmnprt"
const FSXSTRING TaheHulgad::kaash1(FSxSTR("klmnprt"));

/// "rtpsdjklvnm" - us-liite ees olevad t�hed
const FSXSTRING TaheHulgad::us_ees(FSxSTR("rtpsdjklvnm"));

/// "0123456789.,:*%=+-/"
const FSXSTRING TaheHulgad::matemaatika(FSxSTR("0123456789.,:*%=+-/"));

/// "%=+-/"
const FSXSTRING TaheHulgad::matemaatika1(FSxSTR("%=+-/"));

/// "()[]<>{}0123456789.,:*%=+-/"
const FSXSTRING TaheHulgad::suludmatemaatika(FSxSTR("()[]<>{}0123456789.,:*%=+-/"));

/// "0123456789,/+-."
const FSXSTRING TaheHulgad::arv(FSxSTR("0123456789,/+-."));

/// "0123456789"
const FSXSTRING TaheHulgad::number(FSxSTR("0123456789"));

/// "03456789" - 10-nda jms
const FSXSTRING TaheHulgad::ndanumber(FSxSTR("03456789"));

/// "0123456789.,:-" - nt kellaaeg
const FSXSTRING TaheHulgad::kellanumber(FSxSTR("0123456789.,:-"));

/// "0123456789,.-%"
const FSXSTRING TaheHulgad::protsendinumber(FSxSTR("0123456789,.-%"));  

/// "bcdfghjklmnpqrstvwxyz.\\/"- l�hendite oletamiseks
const FSXSTRING TaheHulgad::lyh_kaash(FSxSTR("bcdfghjklmnpqrstvwxyz.\\/"));  

/// "\x00A7" - paragrahvi m�rk
const FSXSTRING TaheHulgad::para(FSxSTR("\x00A7"));

/// "\x00B0" - kraadi m�rk
const FSXSTRING TaheHulgad::kraad(FSxSTR("\x00B0"));
 
/// "\x00B0-" - kraad ja kaldkriips
const FSXSTRING TaheHulgad::kraadjakriips(FSxSTR("\x00B0-"));

/// "0123456789-\x00A7"
const FSXSTRING TaheHulgad::paranumber(FSxSTR("0123456789-\x00A7"));  

/// "0123456789,-+\x00B0"
const FSXSTRING TaheHulgad::kraadinumber(FSxSTR("0123456789,-+\x00B0"));  

/// "0123456789,-+FKC\x00B0"
const FSXSTRING TaheHulgad::kraadinrtht(FSxSTR("0123456789,-+FKC\x00B0"));  

/// "aeiou\x00F5\x00E4\x00F6\x00FC"
const FSXSTRING TaheHulgad::taish(FSxSTR("aeiou\x00F5\x00E4\x00F6\x00FC"));

/// "bcdfghjklmnpqrstvwxyz\x017E\x0161"
const FSXSTRING TaheHulgad::kaash(FSxSTR("bcdfghjklmnpqrstvwxyz\x017E\x0161"));

/// "abcdefghijklmnopqrstuvwxyz\x017E\x0161\x00F5\x00E4\x00F6\x00FC"
const FSXSTRING TaheHulgad::vaiketht(FSxSTR("abcdefghijklmnopqrstuvwxyz\x017E\x0161\x00F5\x00E4\x00F6\x00FC"));

/// amor-ile sobivad sisends�mbolid (vt t�psemat kirjeldust)
//
/// Suured ja v�ikesed t�hed, numbrid, sulud, kirjavahem�rgid, jutum�rgid (s.h. FS jutum�rk v�ike nurk), 
/// langjoon, apostroof, kriips, pluss %, paragrahv .
const FSXSTRING TaheHulgad::amortht(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789{}<>[]()?!:;,.\"\213/\233/\x2019-+%\x00A7\x017E\x0161\x00F5\x00E4\x00F6\x00FC\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));

/// "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\x017E\x0161\x00F5\x00E4\x00F6\x00FC\x00D5\x00C4\x00D6\x00DC\x0160\x017D"
const FSXSTRING TaheHulgad::eestitht(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz\x017E\x0161\x00F5\x00E4\x00F6\x00FC\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));

/// "\x0096\x00AD\x2013\x2014\x2015\x2044\x2215\x2032\x00B4\x0060'" - unicode-is 5 -, 2 / ja 4 apostroofi, millele vastavad m�rgid on kirjas amor_kriipsud sees 
const FSXSTRING TaheHulgad::uni_kriipsud(FSxSTR("\x0096\x00AD\x2013\x2014\x2015\x2044\x2215\x2032\x00B4\x0060'"));

/// "-----//\x2019\x2019\x2019\x2019" - 5 -, 2 / ja 4 apostroofi
const FSXSTRING TaheHulgad::amor_kriipsud(FSxSTR("-----//\x2019\x2019\x2019\x2019"));

/// "\x2019" - amoris 1 apostroof
const FSXSTRING TaheHulgad::amor_apostroof(FSxSTR("\x2019"));

/// "\x00F5\x00E4\x00F6\x00FC"
const FSXSTRING TaheHulgad::tapilised(FSxSTR("\x00F5\x00E4\x00F6\x00FC"));

/// "aeiou\x00F5\x00E4\x00F6\x00FClmnrv"
const FSXSTRING TaheHulgad::heliline(FSxSTR("aeiou\x00F5\x00E4\x00F6\x00FClmnrv"));

/// "ABCDEFGHIJKLMNOPQRSTUVWXYZ\x00D5\x00C4\x00D6\x00DC\x0160\x017D"
const FSXSTRING TaheHulgad::suurtht(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));

/// "ABCDEFGHIJKLMNOPQRSTUVWXYZ-/\x00D5\x00C4\x00D6\x00DC\x0160\x017D"
const FSXSTRING TaheHulgad::suurthtkriips(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ-/\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));

/// "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\x00D5\x00C4\x00D6\x00DC\x0160\x017D"
const FSXSTRING TaheHulgad::suurnrtht(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));

/// "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/\x00D5\x00C4\x00D6\x00DC\x0160\x017D"
const FSXSTRING TaheHulgad::suurnrthtkriips(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/\x00D5\x00C4\x00D6\x00DC\x0160\x017D"));
const FSXSTRING TaheHulgad::suurnrtht1(FSxSTR("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-/%\x00A7\x00D5\x00C4\x00D6\x00DC\x0160\x017D")); // polegi vaja?
const FSXSTRING TaheHulgad::eessodi(FSxSTR("{<[(\"\213/*\x2018\x2019\x201a\x2039\x0027\x201c\x201d\x201e\x00ab\x0022"));
const FSXSTRING TaheHulgad::tagasodi(FSxSTR("}>])\"\233/?!:;,\x203a\x0027\x201c\x201d\x00bb\x0022"));
// s_tagasodi = tagasodi ja �lakoma
const FSXSTRING TaheHulgad::s_tagasodi(FSxSTR("}>])\"\233/?!:;,\'\x2018\x2019\x203a\x0027\x201c\x201d\x00bb\x0022"));
const FSXSTRING TaheHulgad::kaldjakriips(FSxSTR("/-"));  
// punktuatsioon = eessodi + tagasodi
const FSXSTRING TaheHulgad::punktuatsioon(FSxSTR(":;,.\"\?!-([<{*}>])/\\_+=\233\213\x201a\x203a\x2039\x0027\x201c\x201d\x201e\x00ab\x00bb\x0022"));  
const FSXSTRING TaheHulgad::s_punktuatsioon(FSxSTR(":;,.\"\'?!-([<{*}>])/\\_+=\233\213\x2018\x2019\x201a\x203a\x2039\x0027\x201c\x201d\x201e\x00ab\x00bb\x0022"));  
const FSXSTRING TaheHulgad::haalitsus1(FSxSTR("aeiou\x00F5\x00E4\x00F6\x00FC-h"));
const FSXSTRING TaheHulgad::haalitsus2(FSxSTR("-hm"));
const FSXSTRING TaheHulgad::pn_eeltahed1(FSxSTR("aeiouy'\x2019\x00F5\x00E4\x00F6\x00FC"));
const FSXSTRING TaheHulgad::pn_eeltahed2(FSxSTR("aeiouys"));
const FSXSTRING TaheHulgad::pn_eeltahed3(FSxSTR("aeou"));
const FSXSTRING TaheHulgad::pn_eeltahed4(FSxSTR("aeiouy"));
const FSXSTRING TaheHulgad::pn_eeltahed5(FSxSTR("bcdfghklmnprstvx'\x2019"));
const FSXSTRING TaheHulgad::pn_eeltahed6(FSxSTR("s"));
const FSXSTRING TaheHulgad::soome_taht(FSxSTR("aehijklmnoprstuvAEHIJKLMNOPRSTUV\x00E4\x00F6\x00C4\x00D6"));
const FSXSTRING TaheHulgad::eesti_taht(FSxSTR("abdehijklmnoprstuvABDEHIJKLMNOPRSTUV\x00F5\x00E4\x00F6\x00FC\x00D5\x00C4\x00D6\x00DC"));

// t�pit�hed
//{0x00C0, "Agrave"}, {0x00C1, "Aacute"}, {0x00C2, "Acirc"}, {0x00C3, "Atilde"},  
//{0x00C5, "Aring"}, {0x00C6, "AElig"}, {0x00C7, "Ccedil"}, {0x00C8, "Egrave"}, {0x00C9, "Eacute"}, 
//{0x00CA, "Ecirc"}, {0x00CB, "Euml"}, {0x00CC, "Igrave"}, {0x00CD, "Iacute"}, {0x00CE, "Icirc"}, 
//{0x00CF, "Iuml"}, {0x00D0, "ETH"}, {0x00D1, "Ntilde"}, {0x00D2, "Ograve"}, {0x00D3, "Oacute"}, 
//{0x00D4, "Ocirc"},  {0x00D8, "Oslash"}, {0x00D9, "Ugrave"}, 
//{0x00DA, "Uacute"}, {0x00DB, "Ucirc"}, {0x00DC, "Uuml"}, {0x00DD, "Yacute"}, {0x00DE, "THORN"}, 
//{0x00DF, "szlig"}, {0x00E0, "agrave"}, {0x00E1, "aacute"}, {0x00E2, "acirc"}, {0x00E3, "atilde"}, 
//{0x00E5, "aring"}, {0x00E6, "aelig"}, {0x00E7, "ccedil"}, {0x00E8, "egrave"}, 
//{0x00E9, "eacute"}, {0x00EA, "ecirc"}, {0x00EB, "euml"}, {0x00EC, "igrave"}, {0x00ED, "iacute"}, 
//{0x00EE, "icirc"}, {0x00EF, "iuml"}, {0x00F0, "eth"}, {0x00F1, "ntilde"}, {0x00F2, "ograve"}, 
//{0x00F3, "oacute"}, {0x00F4, "ocirc"}, {0x00F8, "oslash"}, 
//{0x00F9, "ugrave"}, {0x00FA, "uacute"}, {0x00FB, "ucirc"}, {0x00FD, "yacute"}, 
//{0x00FE, "thorn"}, {0x00FF, "yuml"}, {0x0152, "OElig"}, {0x0153, "oelig"}, {0x0178, "Yuml"},  

//{0x00F5, "otilde"}, {0x00D5, "Otilde"},
//{0x00E4, "auml"}, {0x00C4, "Auml"},
//{0x00F6, "ouml"}, {0x00D6, "Ouml"},
//{0x00FC, "uuml"}, {0x00DC, "Uuml"}, 
//{0x0161, "scaron"}, {0x0160, "Scaron"}, 
//{0x017E, "zcaron"}, {0x017D, "Zcaron"}, NB! FSC-st puudu! hjk 31.07.2002

// kreeka t�hed
//{0x0391, "Alpha"}, {0x0392, "Beta"}, {0x0393, "Gamma"}, {0x0394, "Delta"}, 
//{0x0395, "Epsilon"}, {0x0396, "Zeta"}, {0x0397, "Eta"}, {0x0398, "Theta"}, {0x0399, "Iota"}, 
//{0x039A, "Kappa"}, {0x039B, "Lambda"}, {0x039C, "Mu"}, {0x039D, "Nu"}, {0x039E, "Xi"}, 
//{0x039F, "Omicron"}, {0x03A0, "Pi"}, {0x03A1, "Rho"}, {0x03A3, "Sigma"}, {0x03A4, "Tau"}, 
//{0x03A5, "Upsilon"}, {0x03A6, "Phi"}, {0x03A7, "Chi"}, {0x03A8, "Psi"}, {0x03A9, "Omega"}, 
//{0x03B1, "alpha"}, {0x03B2, "beta"}, {0x03B3, "gamma"}, {0x03B4, "delta"}, {0x03B5, "epsilon"}, 
//{0x03B6, "zeta"}, {0x03B7, "eta"}, {0x03B8, "theta"}, {0x03B9, "iota"}, {0x03BA, "kappa"}, 
//{0x03BB, "lambda"}, {0x03BC, "mu"}, {0x03BD, "nu"}, {0x03BE, "xi"}, {0x03BF, "omicron"}, 
//{0x03C0, "pi"}, {0x03C1, "rho"}, {0x03C2, "sigmaf"}, {0x03C3, "sigma"}, {0x03C4, "tau"}, 
//{0x03C5, "upsilon"}, {0x03C6, "phi"}, {0x03C7, "chi"}, {0x03C8, "psi"}, {0x03C9, "omega"}, 
//{0x03D1, "thetasym"}, {0x03D2, "upsih"}, {0x03D6, "piv"}, 

// t�hikud
//{0x00A0, "nbsp"}, {0x2002, "ensp"}, {0x2003, "emsp"}, {0x2009, "thinsp"}, 

// kriipsud
// 0x002D miinus -
//{0x00AD, "shy"}, {0x2013, "ndash"}, {0x2014, "mdash"}, 
// 0x2015 r�htkriips

// jutum�rgid
// 0x0027 ' apostroof
//{0x00AB, "laquo"} <<, {0x00BB, "raquo"} >>, {0x2018, "lsquo"} �laind 6,  {0x2019, "rsquo"} �laind 9, 
//{0x201A, "sbquo"} alaind 9,     {0x201C, "ldquo"} �laind 66, {0x201D, "rdquo"} �laind 99, 
//{0x201E, "bdquo"} alaind 99,    {0x2039, "lsaquo"} <, {0x203A, "rsaquo"} >, {0x0022, "quot"}, 
//0x201B �laind tagurpidi 9, 0x2032 prim, 0x2033 topelprim

// erim�rgid
//{0x0026, "amp"}, {0x00A7, "sect"},  {0x00B0, "deg"}, {0x00A9, "copy"}, {0x00AE, "reg"}, 

// punktuatsioon
// {0x00A1, "iexcl"}, {0x00BF, "iquest"}, {0x2026, "hellip"}, 
// 0x203c !!, 0x2044 murrujoon /, 0x2215 jagamisjoon /

// matemaatika
//{0x2030, "permil"}, {0x003C, "lt"}, {0x003E, "gt"}, {0x00D7, "times"}, {0x00F7, "divide"}, 
//{0x00B1, "plusmn"}, {0x00B9, "sup1"}, {0x00B2, "sup2"}, {0x00B3, "sup3"}, 
//{0x00BC, "frac14"}, {0x00BD, "frac12"}, {0x00BE, "frac34"}, {0x2032, "prime"}, {0x2033, "Prime"}, 
//{0x00AC, "not"},
//{0x2208, "isin"}, {0x2209, "notin"}, {0x220B, "ni"}, {0x220F, "prod"}, {0x2211, "sum"}, 
//{0x2212, "minus"}, {0x221E, "infin"},  

// rahad
//{0x00A2, "cent"}, {0x00A3, "pound"}, {0x00A5, "yen"}, {0x20AC, "euro"}, 

//t�pit�htedele lisatavad m�rgid
//{0x00B4, "acute"}, {0x00A8, "uml"}, {0x02C6, "circ"}, {0x02DC, "tilde"}, {0x00B8, "cedil"}, 

// ei tea mis
//{0x00A4, "curren"}, {0x00A6, "brvbar"},  {0x00AA, "ordf"}, {0x00AF, "macr"},  
//{0x00B5, "micro"}, {0x00B6, "para"}, {0x00B7, "middot"}, {0x00BA, "ordm"},  
//{0x0192, "fnof"}, 
//{0x200C, "zwnj"}, {0x200D, "zwj"}, {0x200E, "lrm"}, {0x200F, "rlm"}, 
//{0x2020, "dagger"}, 
//{0x2021, "Dagger"}, {0x2022, "bull"}, {0x203E, "oline"}, {0x2044, "frasl"}, {0x2111, "image"}, 
//{0x2118, "weierp"}, {0x211C, "real"}, {0x2122, "trade"}, {0x2135, "alefsym"}, 
//{0x2190, "larr"}, {0x2191, "uarr"}, {0x2192, "rarr"}, {0x2193, "darr"}, {0x2194, "harr"}, 
//{0x21B5, "crarr"}, {0x21D0, "lArr"}, {0x21D1, "uArr"}, {0x21D2, "rArr"}, {0x21D3, "dArr"}, 
//{0x21D4, "hArr"}, {0x2200, "forall"}, {0x2202, "part"}, {0x2203, "exist"}, {0x2205, "empty"}, 
//{0x2207, "nabla"}, 
//{0x2217, "lowast"}, {0x221A, "radic"}, {0x221D, "prop"}, {0x2220, "ang"}, {0x2227, "and"}, 
//{0x2228, "or"}, {0x2229, "cap"}, {0x222A, "cup"}, {0x222B, "int"}, 
//{0x2234, "there4"}, {0x223C, "sim"}, {0x2245, "cong"}, {0x2248, "asymp"}, {0x2260, "ne"}, 
//{0x2261, "equiv"}, {0x2264, "le"}, {0x2265, "ge"}, {0x2284, "nsub"}, {0x2286, "sube"}, 
//{0x2287, "supe"}, {0x2295, "oplus"}, {0x2297, "otimes"}, {0x22A5, "perp"}, {0x22C5, "sdot"}, 
//{0x2308, "lceil"}, 
//{0x2309, "rceil"}, {0x230A, "lfloor"}, {0x230B, "rfloor"}, {0x2329, "lang"}, {0x232A, "rang"}, 
//{0x25CA, "loz"}, {0x2660, "spades"}, {0x2663, "clubs"}, {0x2665, "hearts"}, {0x2666, "diams"}, 
//};

//=========================================================
// n�ide
//void TestCFSWString(void)
//    {
//    CFSWString s1(FSWSTR("(terekest!)"));
//    CFSWString s2(FSWSTR("(terekest!)"));
//    CFSWString s3(FSWSTR("(terekest!)"));
//    int n;
//    n = TaheHulgad::KustutaEesSodi(s1);
//    n = TaheHulgad::KustutaTagaSodi(s2);
//    n = TaheHulgad::KustutaSodi(s3);
//    }
//=========================================================


