
#if !defined(MRF_MRF_H)
#define MRF_MRF_H

#include "ahel2.h"
#include "cxxbs3.h"
#include "sonatk.h"
#include "mittesona.h"
#include "sloendid.h"
#include "ctulem.h"
#include "adhoc.h"
#include "fsxstring.h"
#include "arva.h"
#include "mrf2yh2mrf.h"

/**
 * liitsõnade komponentide sobivuse kontrolliks
 */
class TY1TYYP  // esimese komponendi tüübi jaoks
    {
    public:
        const FSxCHAR sl;        // sõnaliik
        const char *sobiks_lp;   // char on tegelt lopu jrk nr loppude massiivis
        const int  *vorm;   // kääne vms
        const FSxCHAR *tyvelp; // tüve lõpp, nt mis, sus
        const int  lisakontroll; // mida peab alamprogramm kontrollima
        const int  tyyp;     // komponendile omistatud tüüp
        
        bool ClassInvariant(void) const
            {
            return sobiks_lp!=NULL && vorm!=NULL && tyvelp!=NULL;
            }

        TY1TYYP(
            const FSxCHAR _sl_,
            const char *_sobiks_lp_,   // char on tegelt lopu jrk nr loppude massiivis
            const int  *_vorm_,
            const FSxCHAR *_tyvelp_,
            const int  _lisakontroll_,
            const int  _tyyp_
            ) : sl(_sl_), sobiks_lp(_sobiks_lp_), vorm(_vorm_), tyvelp(_tyvelp_), 
                lisakontroll(_lisakontroll_),  tyyp(_tyyp_)
            {
            assert(ClassInvariant());
            }
        
        // kirjete võrdleminie, et saaks vajadusel kirjeid sortida
        int Compare(const TY1TYYP* rec, const int sortOrder=0) const
            {
			FSUNUSED(sortOrder);
            return TaheHulgad::FSxCHCMP(sl, rec->sl);
            };

        // võtmete võrdlemine, et saaks 2ndotsida
        int Compare(const FSxCHAR* key, const int sortOrder=0) const
            {
			FSUNUSED(sortOrder);
            return TaheHulgad::FSxCHCMP(sl, *key);
            };
    };

/// Programmi kirjutatud loendi element - kasutatakse liitsõnanduses tyvi2 + lp juhuks
//
/// @attention Neist moodustatud massiivi ei järjesta,
/// peab olema juba kirjutatud õiges järjekorras!
class CTY2TYYP   // teise komponendi tüübi jaoks
    { 
    public:
        const FSxCHAR  sl; // sõnaliik
        const FSxCHAR* tyvelp; // tüve lõpp, nt mis
        const int      lisakontroll; // mida peab alamprogramm kontrollima 
        const int      tyyp; // omistatud tüüp

        /// Konstruktor
        CTY2TYYP(
            const FSxCHAR  _sl_,  ///< Kirje v�ti
            const FSxCHAR* _tyvelp_,
            const int      _lisakontroll_,
            const int      _tyyp_
            ) : sl(_sl_), tyvelp(_tyvelp_), lisakontroll(_lisakontroll_), tyyp(_tyyp_)
            {
            }

        /// Kirje võtme võrdlemiseks etteantud võtmega - vajalik kahendotsimiseks
        int Compare(const FSxCHAR* key, const int) const
            {
            return TaheHulgad::FSxCHCMP(sl, *key);            
            }
    };

/// Programmi kirjutatud loendi element - kasutatakse liitsõnanduses tyvi2 + suf juhuks
//
/// @attention Neist moodustatud massiivi ei j�rjesta,
/// peab olema juba kirjutatud �iges j�rjekorras!
class CTY2SUFTYYP  // liitsõnanduse tarvis järelliite/järelkomponendi liigitamise jaoks 
    { 
    public:
        const FSxCHAR  sl;   // tüve sõnaliik
        const FSxCHAR* tyvelp;      // järelkomponendi algus
        const FSxCHAR  sufsl;   // järelliite/järelkomponendi sõnaliik
        const FSxCHAR* suf;               // sufiksi algus 
        const int      tyyp;   // omistatud tüüp

        /// Konstruktor
        CTY2SUFTYYP(
            const FSxCHAR  _sl_,        ///< kirje võti
            const FSxCHAR* _tyvelp_,
            const FSxCHAR  _sufsl_,
            const FSxCHAR* _suf_,             // sufiksi algus 
            const int      _tyyp_
            ) : sl(_sl_), tyvelp(_tyvelp_), 
                sufsl(_sufsl_), suf(_suf_), tyyp(_tyyp_)
            {
            }

        /// Kirje võtme võrdlemiseks etteantud võtmega - vajalik kahendotsimiseks
        int Compare(const FSxCHAR* key, const int=0) const
            {
            return TaheHulgad::FSxCHCMP(sl, *key);
            }
    };

/// Programmi kirjutatud loendi element - pref, suf, lp sobivuse kontrollimiseks
//
/// Kontrollib, kas prefix_tyvi_lp on norm. eestikeelne sõna
/// st sõnaliik peab olema p_n_sl; lp peab sobima
/// kui p_n_sl='V' siis on asi veidi keerulisem
class CPR_SL1                
    {
    public:
        const FSxCHAR* pref;  ///< kirje võti; eesliide ise
        const int p_pik;      // eesliite pikkus
        const FSxCHAR* tylp;  // tüve lõpp, nt eeri
        const int l_pik;      // tüvelõpu pikkus 
        const char uus_sl;    // liite abil saadud sõna liik

        /// Konstruktor
        CPR_SL1(
            const FSxCHAR* _pref_,
            const int _p_pik_,
            const FSxCHAR* _tylp_, 
            const int _l_pik_,
            const char _uus_sl_
            ) : pref(_pref_), p_pik(_p_pik_), tylp(_tylp_), l_pik(_l_pik_), uus_sl(_uus_sl_)
            {
            }

        int Compare(const CPR_SL1* rec, const int)
            {
            return FSStrCmpW0(pref, rec->pref);
            }

        int Compare(const FSxCHAR* key, const int)
            {
            return FSStrCmpW0(pref, key);            
            }
    };


class TY2
    {
    public:
        TY2(void);

        //KLOEND<TY2TYYP, FSxCHAR *> tyyp;
        //KLOEND<TY2SUFTYYP, FSxCHAR *> suftyyp;
        TMPLPTRARRAYBINDUP<CTY2TYYP,    FSxCHAR> tyyp;
        TMPLPTRARRAYBINDUP<CTY2SUFTYYP, FSxCHAR> suftyyp;
    
    };

class PRSL // ei tea miks see k�ll eraldi klassiks on tehtud? TV
    {
    public:
        PRSL(void);
        
        //KLOEND<PR_SL1, FSxCHAR *> usl1;
        TMPLPTRARRAYBINDUP<CPR_SL1, FSxCHAR> usl1;
    };

/// Morf analüüsiga seotud klasside tuumik (chkmin()-i tase)
//
/// Ebaõnnestumist kontrolli ErrNo() funktsiooni
/// kaudu.
class MORF0 
    : public MRFDCT
    {
    public:
        /// Argumentideta konstruktor
        //
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        MORF0(void) 
            {
            konveier=NULL;
            }

        /// Initsialiseerib (s�nastiku, loendid jms)
        //
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        void Start(const CFSFileName* pohiSonastik, AHEL2* a2)
            {
            MRFDCT::Open(pohiSonastik);
            BStart(a2);
            }

        /// Sulgeb (s�nastik kinni, loendite alt m�lu vabaks jms)
        void Stop(void)
            {
            MRFDCT::Close();
            }

        /** Morf analüüsib tundmatuid sõnu
         *
         * @throw  VEAD, CFSFileException, CFSMemoryException, CFSRuntimeException
         * @param[in] const FSXSTRING* @sisse
         * sisendsõna (esialgsel kujul)
         * @param[in] const FSXSTRING* @sissePuhastatud
         * sisendsõna (vajadusel olemitest ja märgenditest puhastatud)
         * @param[out] MRFTULEMUSED* @tulemus
         * analüüsi tulemus
         * @param[in] const int @maxtasand
         * kui keerulist sõnamoodustus-struktuuri maksab katsetada
         */
        void chkmin(  //-->Source Files/chkmin.cpp
            const FSXSTRING* sisse,
            const FSXSTRING* sissePuhastatud,
            MRFTULEMUSED* tulemus,
            const int maxtasand
            );

        /// Morf analüüsib tundmatuid s�nu (oletades)
        //
        /// @return
        /// - @a ==true Ok
        /// - @a ==false Mootor jooksis kokku. T�psem inf baasklassiist VEAD                                       
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        void arvamin(   // lib_amor32/Oletaja -- c2\morf\lib_amor32\chkoleta.cpp
            const FSXSTRING *sisse, ///< sisends6na
            MRFTULEMUSED *tulemus);  ///< tulemus
            

        // oletaja tykid - kutsutakse chkoleta()'st
        // lib_amor32/Oletaja -- c2\morf\lib_amor32               
        // arvax.cpp

        /// Kasutatakse oletamisel
        //
        /// õnnetul kombel kasutatakse klassis MORF_VMT,
        /// seep�rast peab olema @a public.
        /// @return
        /// - @a ==true OK
        /// - @a ==false Jama
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        bool Barvaww(
            MRFTULEMUSED* tulemus, 
            FSXSTRING* S6na, 
            int S6naPikkus, 
            const FSxCHAR* lubatavad_sl
            );

        bool EmptyClassInvariant(void)
            {
            return 
                MRFDCT::EmptyClassInvariant()
                && konveier==NULL
                //&& nLopud.EmptyClassInvariant()
                //&& ad_hoc.EmptyClassInvariant()
                //&& loend.EmptyClassInvariant()
                //&& ty2.EmptyClassInvariant()
                //&& ty1_tyyp.EmptyClassInvariant()
                //&& prsl.EmptyClassInvariant()
                ;
            }

        bool ClassInvariant(void)
            {
            return MRFDCT::EmptyClassInvariant()
                && konveier!=NULL
                //&& nLopud.ClassInvariant()
                //&& ad_hoc.ClassInvariant()
                //&& loend.ClassInvariant()
                //&& ty2.ClassInvariant()
                //&& ty1_tyyp.ClassInvariant()
                //&& prsl.ClassInvariant()
                ;
            }

    protected:
        int omastavanr( FSXSTRING* mis );

        AHEL2 *konveier; // viit, et ühilduks vana koodiga
        NLOPUD nLopud;
        AD_HOC ad_hoc;
        MUUD_LOENDID loend;
        TY2 ty2;
        //TY1TYYP_ARR ty1_tyyp;
        TMPLPTRARRAYBINDUP<TY1TYYP, FSxCHAR> ty1_tyyp;
        PRSL prsl;

        // MadalTase ======================================
        // hjk_cxx.cpp ------------------------------------
        /** otsib sõnasisest juppi sõnastikust  
         * 
         * peaaegu nagu cXXfirst, aga kasutatakse liitsõna analüüsil: 
         * et vältida asjatut
         * juppide taasotsimist sõnastikust, märgitakse massiivis paha_koht
         * ära kohad algsõnas, kus asuvaid juppe pole uuesti mõtet otsida
         * @param S6na_algus - algne sõna
         * @param nihe       - jupi kaugus sõna algusest
         * @param JupiPikkus - jupi pikkus 
         * @param cnt        - cXXfirst-i tagastatav indeks
         * @param paha_koht  - siin on info sellest, milliseid juppe pole mõtet otsida
         * @param paha_koha_suurus - massiivi paha_koht suurus
         * @return  -  samad asjad, mis cXXfirst
         */
        int hjk_cXXfirst(
            FSXSTRING *S6na_algus, 
            int nihe, 
            int JupiPikkus, 
            int *cnt, 
            char *paha_koht,
            const int paha_koha_suurus);
        
        /** loob massiivi paha_koht hjk_cXXfirst-i jaoks
         * 
         * @param S6naPikkus
         * @param paha_koht
         * @param paha_koha_pikkus - massiivi paha_koht suurus
         */
        void init_hjk_cxx(
            int S6naPikkus, 
            char *paha_koht,       
            const int paha_koha_pikkus 
            );
        
        /** teeb uue massiivi paha_koht ja kopeerib osa eelmise infost sinna
         * 
         * kasutatakse juhul, kui liitsõna analüüsi üheks etapiks on 
         * alamsõna käsitlemine omaette analüüsi vajava liitsõnana
         * @param v_pikkus
         * @param v_paha
         * @param u_pikkus
         * @param u_paha
         * @param u_paha_pikkus
         */
        void uus_paha(
            int v_pikkus, 
            const char *v_paha, 
            int u_pikkus, 
            char *u_paha,
            const int u_paha_pikkus);

        // kjuhtum.cpp ------------------------------------
        /** kontrollib, kas liitsõna eesmine komponent vastab teatud tingimustele
         * 
         * @param tyvi
         * @param lgrd
         * @param sl_ind
         * @param sobivad_variandid
         * @return 
         * <ul><li> @a 1 - vastab
         *      <li> @a 0 - ei vasta
         *  </ul>
         */
        int juht1(
              KOMPONENT *tyvi, 
              TYVE_INF *lgrd, 
              int sl_ind, 
              VARIANTIDE_AHEL **sobivad_variandid);
        
        /** kontrollib, kas liitsõna tagumine komponent (või järelliide) vastab teatud tingimustele
         * 
         * @param tyvi - komponent ise
         * @return 
         * <ul><li> @a 1 - vastab
         *      <li> @a 0 - ei vasta
         *  </ul>
        */
        int juht2(KOMPONENT *tyvi);
        
        /** liitsõna eesmise ja tagumise komponendi sobivus
         * 
         * (neid iseloomustavate tüüpide põhjal)
         * @param ty1tyyp
         * @param ty2tyyp
         * @return 
         * <ul><li> @a  > 0 -- sobib (mida suurem nr, seda paremini)
         *      <li> @a == 0 -- ei sobi
         *  </ul>
         */
        int ty1ty2(int ty1tyyp, int ty2tyyp);
        
        /** tyvi1 + lõpp + tyvi2 sobivus
         * 
         * (neid iseloomustavate tüüpide põhjal)
         * @param ty1tyyp
         * @param ty2tyyp
         * @return 
         * <ul><li> @a  > 0 -- sobib (mida suurem nr, seda paremini)
         *      <li> @a == 0 -- ei sobi
         *  </ul>
         */
        int ty1_l_ty2(int ty1tyyp, int ty2tyyp);
        
        /** kui kaks liitsõna komponenti sobivad kokku, siis paneb nad kokku ühte variantide ahelasse
         * 
         * @param ty1_variandid - esimese komponendi variandid
         * @param ty2_variandid - teise komponendi variandid
         * @param sobivad_variandid - tulemus
         * @return   sobivuse kindlust iseloomustav positiivne arv
         */
        int tyvi1tyvi2(VARIANTIDE_AHEL **ty1_variandid, VARIANTIDE_AHEL **ty2_variandid, VARIANTIDE_AHEL **sobivad_variandid);
        
        /** kas sõna keskel algab tyvi2, mis sobib siia sõnasse?
         * 
         * @param ty1_ahelad -- varem leitud info ty1 kohta
         * @param ty2        -- varem leitud info ty2 kohta
         * @param S6na       -- algne sõna
         * @param eel_pik    -- mitu tähte enne ty2 alguse kohta
         * @param sobivad_variandid -- siia pannakse tulemus, kui analüüs õnnestus
         * @param paha_koht   -- massiiv sõnastikust otsimise kiirendamiseks
         * @param paha_koha_suurus -- selle massiivi suurus
         * @return 
         * <ul><li> @a mitte ALL_RIGHT -- viga
         *      <li> @a ALL_RIGHT -- õnnestus või ei õnnestunud
         *  </ul>
         */
        int liitsona(VARIANTIDE_AHEL **ty1_ahelad, KOMPONENT *ty2, FSXSTRING *S6na, int eel_pik, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht, const int paha_koha_suurus);
        
        /** teisendab ty1 tüübi selliseks, et teda saab kasutada ty1 + liitsõna sobivuse kontrollil
         * 
         * (sest piirangud sellele, milline ty1 sobib liitsõnaga ja 
         * milline peab seejuures olema liitsõna esimene komponent, on rangemad,
         * kui juhtumil paljalt ty1 + ty2 )
         * @param ty1tyyp -- sobivuse tüüp;
         * @return  sobivuse tüüpi iseloomustav positiivne arv
         */
        int ty11tyyp(int ty1tyyp);
        
        /** ty1 + liitsõna sobivuse kontroll
         * 
         * @param ty1tyyp - ty1 tüüp
         * @param ty2tyyp - liitsõna 1. komponendi tüüp
         * @return   sobivuse kindlust iseloomustav positiivne arv
         */
        int ty11ty11(int ty1tyyp, int ty2tyyp);

        // komp.cpp ---------------------------------------
        class CVARIANTIDE_AHEL
            {
            public:
                VARIANTIDE_AHEL* ptr;
                CVARIANTIDE_AHEL(void)
                    {
                    ptr=NULL;
                    }
                ~CVARIANTIDE_AHEL(void)
                    {
                    if(ptr!=NULL)
                        {
                        ahelad_vabaks(&ptr);
                        }
                    assert(ptr==NULL);
                    }
            };

        /*void ahelad_vabaks(VARIANTIDE_AHEL **ahel);
        void eemalda_1ahel(VARIANTIDE_AHEL **ahel);
        void komp_vabaks(KOMPONENT **komp);*/

        KOMPONENT *lisa_esimene(VARIANTIDE_AHEL *kuhu);
        KOMPONENT *esimene_komp(VARIANTIDE_AHEL *ahel);
        KOMPONENT *kop_kompid(KOMPONENT **kuhu, KOMPONENT *kust);
        KOMPONENT *lisa_1komp(KOMPONENT **komp);
        void nulli_1komp(KOMPONENT *komp);
        void kopeeri_komp(KOMPONENT *kuhu, KOMPONENT *kust);
        VARIANTIDE_AHEL *lisa_1ahel(VARIANTIDE_AHEL **ahel);
        void nulli_1variant(VARIANTIDE_AHEL **ahel);
        VARIANTIDE_AHEL *kopeeri_ahel(VARIANTIDE_AHEL *kuhu, VARIANTIDE_AHEL *kust);
        VARIANTIDE_AHEL *lisa_ahel(VARIANTIDE_AHEL **mille_taha, VARIANTIDE_AHEL *kust);
        VARIANTIDE_AHEL *viimane_variant(VARIANTIDE_AHEL *ahel);
        VARIANTIDE_AHEL *viimane_prefita_variant(VARIANTIDE_AHEL *ahel);
        void lisa_min_info(KOMPONENT *komp, FSXSTRING *algsona, int nihe, int k_pikkus);
        void lisa_psl_info(KOMPONENT *komp, int tyyp, int jrk_nr);
        void lisa_ty_info(KOMPONENT *kuhu, TYVE_INF *grupid, int sl_ind, int mitmes );
        void lisa_lp_info(KOMPONENT *kuhu, TYVE_INF *grupid, int mitmes, char lopunr );
        void lisa_ty_ja_lp_info(VARIANTIDE_AHEL *ahel, TYVE_INF *grupid, int sl_ind, int mitmes, char lopunr);
        void lisa_suf_ja_lp_info(KOMPONENT *kuhu, TYVE_INF *grupid, int sl_ind, int mitmes, char lopunr);
        int on_liitsona(KOMPONENT *komp);
        int on_tylopuga(VARIANTIDE_AHEL *variandid, KOMPONENT *ty, KOMPONENT *lopp);
        void asenda_tyves(VARIANTIDE_AHEL **variandid, const FSxCHAR *mis, const FSxCHAR *millega);
        int leia_algvorm(KOMPONENT *komp);

        // sobivus.cpp ------------------------------------
        int ssobivus( TYVE_INF *grupid, const FSxCHAR *sl, 
            const int sl_pik, const char lopunr, const FSxCHAR *sonalk, 
            const int vorminr, char *sobivad, const int sobivatePikkus);
        bool on_paha_sl( TYVE_INF *grupid, const int lg_nr, const FSxCHAR *sl, 
                     const FSxCHAR lubamatu_liik );
        int sobib_p_t(KOMPONENT *pref, KOMPONENT *tyvi);
        int sobib_p_t_s(KOMPONENT *pref, KOMPONENT *tyvi, KOMPONENT *suff);
        //int viletstyvi( FSXSTRING *ty );
        int viletsls( FSXSTRING *ty );
        int minipik(FSXSTRING *ty);
        int sobiks_ne( FSXSTRING *ty, int pikkus );
        int on_muutumatu(KOMPONENT *tyvi);

        // ty_lp.cpp --------------------------------------
        int ty_lp(KOMPONENT *lopp, int nihe, int typikkus, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);
        int ty_suf(KOMPONENT *suff, int nihe, int typikkus, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);
        int ty2jne(KOMPONENT *tyvi, VARIANTIDE_AHEL **varasemad_variandid, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);

        // S�nad ==========================================
        // kchk1.cpp --------------------------------------
        int kchk1(VARIANTIDE_AHEL **variandid, FSXSTRING *word, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid, 
                                                    char *paha_koht, const int paha_koha_suurus);

        // kchk2.cpp --------------------------------------
        int kchk2(VARIANTIDE_AHEL **variandid, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);
        int liide_ok( FSXSTRING *ty, int typik, FSXSTRING *suf, const FSxCHAR *suf_sl);

        // kchk30.cpp -------------------------------------
        int kchk30(VARIANTIDE_AHEL **variandid, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid, 
            char *paha_koht, const int paha_koha_suurus);

        // kchk33.cpp -------------------------------------
        int kchk33(VARIANTIDE_AHEL **variandid, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);

        // kchk4.cpp --------------------------------------
        int kchk4(VARIANTIDE_AHEL **variandid, FSXSTRING *S6na, int S6naPikkus, 
            VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht,const int paha_koha_suurus);

        // kchk5.cpp --------------------------------------
        int lp_variant(KOMPONENT *tyvi1, KOMPONENT *tyvi, FSXSTRING *S6na, int pik, VARIANTIDE_AHEL **vahe_variant);
        int edasiseks(VARIANTIDE_AHEL *variant, VARIANTIDE_AHEL **mille_taha, VARIANTIDE_AHEL **vahe_variant, VARIANTIDE_AHEL **uus_variant);
        int kchk5(VARIANTIDE_AHEL **variandid, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid, char *paha_koht, const int paha_koha_suurus);

        // kchk6.cpp --------------------------------------
        int kchk6(VARIANTIDE_AHEL **variandid, FSXSTRING *S6na, int S6naPikkus,
            VARIANTIDE_AHEL **sobivad_variandid, 
            char *paha_koht, const int paha_koha_pikkus);

        // Mittes�nad =====================================
        // chkgeon.cpp ------------------------------------
        
        /** @brief Kontrollib, kas on tegemist mitmesõnalise geonimega
         * 
         * @param[out] MRFTULEMUSED* @tul
         * Kui tul->on_tulem()==true, siis oli mitmesõnaline geonimi. muidu mitte.
         * @param[in]  FSXSTRING* @sona
         * Sisendsõna (vajadusel olemitest ja märgenditest puhastatud)
         * @param[out] int* @mitu
         * Mitmest sõnast koosnes (2 või 3)
         * @return @a !=ALL_RIGHT kui mingi jama
         * 
         */
        int chkgeon(MRFTULEMUSED* tul, FSXSTRING* sona, int* mitu);

        int chkvaljend(MRFTULEMUSED *tul, FSXSTRING *S6na);

        // chkhy1.cpp -------------------------------------
        int chkhy1(MRFTULEMUSED *tulemus, FSXSTRING *S6na);

        // chkhy2.cpp -------------------------------------
        int chkhy2(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int maxtasand, int *tagasi );

        // chklyh0.cpp ------------------------------------
        int chklyh0(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);

        // chklyh1.cpp ------------------------------------
        int chklyh1(MRFTULEMUSED *tulemus, FSXSTRING *S6na);
        bool sobiks_emailiks(FSXSTRING *sisendsona);
        bool sobiks_veebiaadressiks(FSXSTRING *sisendsona);

        // chklyh2.cpp ------------------------------------
        int chklyh2(MRFTULEMUSED *tulemus, FSXSTRING *S6na);

        // chklyh3.cpp ------------------------------------
        int chklyh3(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int sygavus, int *tagasitasand);
        
        // chklyh4.cpp ------------------------------------
        int chklyh4(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);

        // chkmitte.cpp -----------------------------------
        int chkmitte(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);

        // chknr1.cpp -------------------------------------

        // chknr2.cpp -------------------------------------
        int chknr2(MRFTULEMUSED *tulemus, FSXSTRING *S6na);

        // AdHoc ==========================================
        // valjatr.cpp ------------------------------------
        FSXSTRING *OigeTyveInf(
            const TYVE_INF *tyveInf, // sisend; selle tüve lõpugrupp jms
        	int *mitmesTyveInf, // nii sisend kui väljund; siia paneb mitmes dpr-ist
            // const int mituTyveInfi, // sisend; alati =1
            // const AVTIDX *idx,
            const FSxCHAR *snaliik, // sisend; lubatavad sõnaliigid (stringina))
            const int lopp, // sisend; lubatav lõpp (õigemini jrk nr lõppude loendis)
            const int vorm, // sisend; lubatav vorm (õigemini jrk nr vormide loendis)
	        FSXSTRING *tyvi);

        // PeaTs�kkel =====================================
        // chkx.cpp ---------------------------------------
        int chksuluga(MRFTULEMUSED *tul, FSXSTRING *S6nna, int maxtasand);
        int chkx(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi);
        int chkwrd(MRFTULEMUSED *tul, FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi, const FSxCHAR *lubatavad_sl);
        int chkww(FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi, VARIANTIDE_AHEL **sobivad_variandid);
        int chkgi(MRFTULEMUSED *tulemus, FSXSTRING *S6nna, int S6naPikkus, int maxtasand, int *tagasi, const FSxCHAR *lubatavad_sl);

        // adhoc.cpp
        void lisa_ad_hoc_gi(MRFTULEMUSED *tul, FSXSTRING *s6na);
        void lisa_ad_hoc(MRFTULEMUSED *tul, MRFTUL *t, int lgr, TYVE_INF *tyveinf, const FSXSTRING *lubatavad_sl);

        // valjatr.cpp
        void variandid_tulemuseks(MRFTULEMUSED *tul, const FSxCHAR *lubatavad_sonaliigid, VARIANTIDE_AHEL **ahel);

        OLETAJA_DCT oletajaDct;

        // oletaja tykid - kutsutakse chkoleta()'st
        // lib_amor32/Oletaja -- c2\morf\lib_amor32               
        // arvax.cpp
        int arvax(MRFTULEMUSED *tulemus, FSXSTRING *S6nna);

        // arvamitte.cpp
        int arvamitte(MRFTULEMUSED *tulemus, FSXSTRING *S6na);
        // arvalyh1.cpp
        int arvalyh1(MRFTULEMUSED *tulemus, FSXSTRING *S6na);
        bool sobiks_lyhendiks(FSXSTRING *S6na);
        // arvash1.cpp
        int arvash1(MRFTULEMUSED *tulemus, FSXSTRING *S6na);
        // arvavi1.cpp
        int arvavi1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);
        // arvahy1.cpp
        int arvahy1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);
        // arvai.cpp
        int arvai(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);
        // arvapn2.cpp
        int arvapn2(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus);
        // arvasuf1.cpp
        int arvasuf1(VARIANTIDE_AHEL **too_variandid, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid);
        // arvapn1.cpp
        int arvapn1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **too_variandid);
        bool algv_lyhem( FSXSTRING *tyvi, int tyvepik, FSXSTRING *lp, int silpe );
        bool soome_pn_se( FSXSTRING *tyvi, int tyvepikkus, SILP *s );
        bool eesti_pn_s( FSXSTRING *tyvi, int tyvepikkus );
        bool eesti_pn_se( FSXSTRING *tyvi, int tyvepikkus, SILP *s );
        bool soome_pn_s( FSXSTRING *tyvi, int tyvepikkus );
        bool sobiks_sg_n( FSXSTRING *sona, int sonapikkus, SILP *s);
        bool ent_tyvi(FSXSTRING *tyvi, int tyvepik, int silpe);
        // arvans1.cpp
        int arvans1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **variandid);
        // arvans2.cpp
        int arvans2(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid, const FSxCHAR *lubatavad_sl);
        bool sobiks_sg_n_ns( FSXSTRING *sona, int sonapikkus);
        // arvav1.cpp
        //int arvav1(MRFTULEMUSED *tulemus, FSXSTRING *S6na, int S6naPikkus, VARIANTIDE_AHEL **sobivad_variandid);
        // arvalyh2.cpp
        int arvalyh2(MRFTULEMUSED *tulemus, FSXSTRING *S6na);
        bool sobiks_akronyymiks(FSXSTRING *sisendsona);

    private:
        void BStart(AHEL2 *a2);// -->MadalTase/kjuhtum.cpp

    };


#endif





