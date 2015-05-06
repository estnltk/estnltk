
#if !defined( SONATK_H )
#define SONATK_H

/// @file sonatk.h
/// @brief eesti k s�nade morf. anal��siga seot v�rk: prefiksite, sufiksite, vormide ja l�ppudega seot. konstandid ja struktuurid

#include "ini_mrf.h"
#include "tmk2t.h"
#include "mrflags.h"
#include "post-fsc.h"
#include "fsxstring.h"

#define KOIK_LIIGID FSxSTR("ABCDFGHIJKNOPSUVWXYZ")     ///< v�imalikud s�naliigid

#define MITTE_VERB  FSxSTR("ABCDFGHIJKNOPSUWXYZ")      ///< v�imalikud s�naliigid, v.a. tegusona

#define KI_LIIGID   FSxSTR("kABCDFGHIJKNOPSUVWXYZ")    ///< == KOIK_LIIGID + k ki-liite ad hoc variantide piiramiseks

#define LIIK_VERB  FSxSTR("V")                          ///< s�naliik tegusona

#define LIIK_PARISNIMI  FSxSTR("H")                     ///< s�naliik p�risnimi

#define LIIK_YLDNIMI    FSxSTR("S")                     ///< s�naliik �ldnimi

#define LIIK_SACU  FSxSTR("SACU")                       ///< s�naliigid SACU

#define LIIK_A  FSxSTR("A")                             ///< s�naliik omaduss�na; ainult A

#define LIIK_KAANDSONA  FSxSTR("ABCGHNOPSU")            ///< ainult k��ndsonad

#define LIIK_KAAND1     FSxSTR("ABCDGHJKNOPSUXY")      ///< LIIK_KAANDSONA + muutumatud, v.a. h��ds�nad I

#define TYLP_LIIK1  FSxSTR("ABCDGHIJKNOPSUWXYZ")        ///< gene jaoks - noomen, mis v�ib olla sg n

#define TYLP_LIIK2  FSxSTR("ADGIJKPXYZ")                ///< gene jaoks - muutumatu s�na


#define ALGV_LIIK   FSxSTR("ABCHNOPSUV")                ///< algvormide leidmiseks - ainult neil on m�tet otsida algvormi 

#define SUFFE  6                                        ///< max arv �ksteise sisse sobivaid suf; oletus

#define PREFFE  6                                       ///< max arv �ksteise sisse sobivaid pref; oletus

#define SUVA_LP      -2                                 ///< == POLE_TAANDLP

#define SUVA_LIIK    FSxSTR("z")

#define SUVA_SL      (FSxCHAR)'z'

#define TABU_SL      (FSxCHAR)'t'                       ///< tabus�na (perse) tunnus

#define SPELL_SL     (FSxCHAR)'s'                       ///< mitmesõnalise nime viimase osa (Aires) tunnus (varem aint spelleris lubatud, 2015 alati lubatud) 

#define TESA_SL      (FSxCHAR)'e'                       ///< aint tesauruses lubatava s�na (aukudega) tunnus 

#define MITTELIITUV_SL  (FSxCHAR)'m'                    ///< liits�na koosseisu mittesobiva s�na (viie_aastane) tunnus 

#define L_MITTELIITUV_SL  (FSxCHAR)'n'                    ///< liits�na l�ppu mittesobiva s�na (abt, bai, utt jms) tunnus 

#define W_SL  (FSxCHAR)'W'                             ///< s�naliik deverbaal; ainult koos noomeniga (n�itab, et on tuletatud verbist, nt. jooks)

#define SUVA_VRM     -2

#define null_lopp     0                                 ///< lpnr("")

#define TAISH         1

#define KAASH         2

#define UUS_SILP      1

#define VANA_SILP     2

#define LOEND_EL     500                                ///< max elementide arv 1 loendis

#define V_STR_LEN    1024                               ///< v�ljundstingi max pikkus

#define MAG_SIZE     3                                  ///< sisend-magasini suurus

#define MITU_OMASTAVAT  8                               ///< massiivi omastavad[][] m��tmed

#define OMASTAVA_MAX_PIK 11

#define K_PREF        1

#define K_TYVI        2

#define K_SUFF        3

#define K_LOPP        4

#define L_TYVE_TYYP  40

/** Sõnastruktuuri 1 komponent (pref, tyvi, suf v lopp)
 * 
 * üks lüli ühe sõna võimalike komponentide ahelas;
 * vajalik just liitsõnade analüüsiks, kuna pole ette teada, millistest
 * komponentidet (tüvedest, liidetest) sõna kokku on pandud ja kuidagi tuleb 
 * säilitada info juba leitud võimalike komponentide kohta
 * 
 * sellega on seotud palju infot:
 * millist tähejada esindab; mis info on tema kohta sõnastikus;
 * kus asub komponentide ahelas;
 */
class KOMPONENT   
    {
    public:
        KOMPONENT(void)
            {
            InitClassVariables();
            }

        KOMPONENT *komp_jargmine;
        KOMPONENT *komp_eelmine;
        FSXSTRING algsona;          ///< anal-tav s�na
        int nihe;                   ///< komponendi algus s�nas
        FSXSTRING k_algus;          ///< komponendi algus
        int k_pikkus;               ///< komponendi pikkus
        int k_tyyp;                 ///< PREFIKS, TYVI, SUFIKS v LOPP

        // tuleneb sonastikust
        int jrk_nr;                 ///< indeks vastavalt k_tyyp-ile kas
                                    ///< prefinfo, sufinfo v loppude tabelisse;
                                    ///< tuleneb sonastikust
        int liitumistyyp;           ///< komponendi liitumis-liik; vajalik liits�nanduses;
                                    ///< tuleneb sonastikust

        // tuleneb komponentide sobivusn�uetest
        FSXSTRING sl;               ///< komponendi sonaliik;
                                    ///< tuleneb komponentide sobivusn�uetest
        TYVE_INF tylgr;             ///< 1 element ty_lgrd[]-st;
                                    ///< tuleneb komponentide sobivusn�uetest
        
        // ainult kui k_tyyp==LOPP
        int lgr;                    ///< lopugrupp; ainult kui k_tyyp==LOPP
        int lpnr;                   ///< lopu nr lopugrupis; ainult kui k_tyyp==LOPP

        // abi-info
        FSXSTRING liitumisinfo;     ///< abi-info
        FSXSTRING algvorm;          ///< abi-info
		
	int sonastikust;            ///< leitud s�nastikust v�i oletatud; 
                                    ///< vaja lisakr�nksude ja algvormi leidmise jaoks

    private:
        void InitClassVariables(void)
            {
            komp_jargmine=komp_eelmine=NULL;    
            }

        /// Copy-konstruktor pole lubatud
        KOMPONENT(const KOMPONENT&) { assert(false); }

        /// Omistamisoperaator pole lubatud
        KOMPONENT& operator==(const KOMPONENT&) { assert(false);  return *this; }
    }; 

/** ahel ühe sõna komponentideks tükeldamise eri versioonide hoidmiseks
 * (pole teada, kui palju võimalikke tükeldamise variante, s.h. pooleliolevaid, 
 * tuleks alles hoida, seetõttu kasutame ahelat, mitte massiivi) 
 */
struct VARIANTIDE_AHEL   
    {
    /** ahela sisu: võimalikud komponendid */
    KOMPONENT *variant;                           
    struct VARIANTIDE_AHEL *eelmine_variant;    ///< eelmine ahel
    struct VARIANTIDE_AHEL *jargmine_variant;   ///< j�rgmine ahel
    };

void ahelad_vabaks(VARIANTIDE_AHEL **ahel);
void eemalda_1ahel(VARIANTIDE_AHEL **ahel);
void komp_vabaks(KOMPONENT **komp);

#endif



