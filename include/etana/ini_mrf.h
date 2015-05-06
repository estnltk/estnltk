
// 2000.07.14 TV 

#ifndef INI_MRF_H
#define INI_MRF_H
#include "mrflags.h"
#include "post-fsc.h" 
/*
  * eesti k sõnade morf. analüüsiga seot värk:
  * prefiksite, sufiksite, vormide ja lõppudega seot. konstandid ja struktuurid
  * ühine nii vanamorf\mrf kui vanamrorf\init -ile
  */

#define LOENDEID 11		// NB1 See number peab olema >= tegelik_loendite_arv+1.
						// NB2 Kui seda muuta, tuleb FILEINFO 
						// lugemine/salvestamine ymberkirjutada (rfi.cpp/wfi.cpp)!!!!
#define ENDLEN 8       
#define FORMLEN 10
#define STEMLEN 40         /* peab olema == tmk2tx.h/TYVE_MAX_PIKKUS */
#define SUFLEN 15          /* sufiksi max pikkus + 1 (-jaskondlikkuse) */
#define PREFLEN 9          /* prefiksi max pikkus + 1; */
#define MAX_ENDNR 170      /* erin. lõppude max arv (teg. 163 erinevat)    */
#define MAX_FORMNR 110     /* erin. vormide max arv (teg. 102 erinevat)    */
#define MAX_SUFNR 920      /* erin. suf max arv (teg. 794 erinevat) 10.11.95 */
#define MAX_PREFNR 500     /* erin. pref max arv (teg. 431 erinevat)11.06.01*/
#define TAANDLIIKE  30     /* suf, pref poolt 'nõutavate' sõnaliikide arv */
#define TAANDL_MAX_PIK 8   /* taandliigi stringi max pikkus */
#define TYVELOPPE   40     /* suf, vahesuf poolt nõut. tyvelõppude arv */
#define TYVELP_MAX_PIK 6   /* tyvelõpu stringi max pikkus */
#define SUF_LGCNT 4        /* sufiksi max lopugruppide arv */
// TV-2000.07.14-{{
//#define SONALIIKE   180  // max lubatud sõnaliigi jõrjendite arv
                           // Seisuga 2000.07.14 oligi neid 179 tükki.
                           // Sõnaliikide tabeli indeksi jaoks ruumi 8bitt, vt cxxbs3.h
#define SONALIIKE   300    // Peab olema teglik_sõnaliigijõrjendite_arv+1
                           // NULL_LIIKI - selle paneb 'readeel()' sõnaliikide 
                           // tabelisse juurde, nii on vaja
                           // SONALIIKE-1 == NULL_LIIKI
                           // NULL_LIIKI > max (sõnaliikide_tabeli_idx)
// }}-TV-2000.07.14

#define SONAL_MAX_PIK 14   /* sonaliikide stringi max pikkus; enne 19.10.98 oli 6 */
#define POLE_TAANDLP -2    /* vajalik tegel. init.c-s */

 typedef struct
	 {
     // 2 baidine täisarv on lõõdud 2ks baidiks, et asi ei sõltuks
     // protsessori baidijärjest
	 unsigned char  gr_algus; /* 'viit' lgr lõppude jadale gr[]-s; suurem bait */
	 unsigned char  gr_lopp; /* 'viit' lgr lõppude jadale gr[]-s; vaiksem bait */
	 char cnt;      /* selle jada pikkus */
	 } GRUPP;      /* 1 lõpugrupp */



typedef struct 
    {
    char piiriKr6nksud0; 
    char piiriKr6nksud1; 
    char lisaKr6nksud0;
    char lisaKr6nksud1;
    char tab_idx0;
    char tab_idx1;
    char blk_idx;
    } SUF_TYVE_INF; /* TYVE_INF imiteerimine HJK 04.01.2002 */

typedef struct
    {
    char taandlp;  // sufiksi taandl"pp 
    char tsl;      // s"naliik, millele suf v"ib liituda (indeks massiivis)
    char ssl0;      // sufiksi s"naliigi indeks 
    char ssl1;      // sufiksi s"naliigi indeks 
    char tylp;     // n"utav tyvel"pp (indeks massiivis) 
    char mitutht;  // mitu ta"hte sufiksi lopust kuulub tegelikult tyvele 
    SUF_TYVE_INF suftyinf[SUF_LGCNT];  /* HJK 19.12.01 palakro'nksunduse jaoks */
    } KETTA_SUFINFO;     // info, mis on vajalik suf sobivuse kontr-ks 

typedef struct
	{
	char sl;        /* sõnaliik, millele pref võib liituda (indeks mass-s) */
	char piiriKr6nksud0; 
	char piiriKr6nksud1; 
        char lisaKr6nksud0;
        char lisaKr6nksud1;
	} KETTA_PREFINFO;     /* info, mis on vajalik pref sobivuse kontr-ks (kettal)*/

typedef struct
	{
	char sl;        /* sõnaliik, millele pref võib liituda (indeks mass-s) */
	int  piiriKr6nksud; 
    int  lisaKr6nksud;
	} PREFINFO;     /* info, mis on vajalik pref sobivuse kontr-ks (mälus) */

#endif
