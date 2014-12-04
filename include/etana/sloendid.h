
#if !defined(SLOENDID_H)
#define SLOENDID_H

// 13.05.2002

#include <stdlib.h>
//=========================================================
#include "mrflags.h"
#include "post-fsc.h"
#include "tloendid.h"

typedef struct // kui on lihtsalt stringide massiiv
    {
    const FSxCHAR* string;
    } FSxC1;

/*// Programmi sissekirjutatud loendi element.
//
/// Vaikimisi Copy-konstruktor on OK. @n
/// Vaikimisi omistamisoperaator on OK.
/// @attention Sellistest kirjetest moodustatud massiivis peavad
/// k�ik v�tmed olema unikaalsed.
class CFSxC1
    {
    public:
        const FSxCHAR* string; ///< Kirje v�ti

        /// Konstruktor
        CFSxC1(const FSxCHAR* _string_) : string(_string_)
            {
            assert(string!=0); //TODO: throw
            }

        /// V�rdleb kirjet v�tmega - kahendotsimiseks
        int Compare(const FSxCHAR* key, const int)
            {
            // Key v�ib olla NULL-viit
            return FSStrCmpW0(string, key);
            }

        /// V�rdleb kahte kirjet - j�rjestamiseks
        //
        /// @attention Sellistest kirjetest moodustatud massiivis peavad
        /// k�ik v�tmed olema unikaalsed.
        int Compare(const CFSxC1* rec, const int)
            {
            assert(rec!=0);
            int ret=FSStrCmpW0(string, rec->string);
            assert(ret!=0); // ei tohi olla korduvaid
            return ret;
            }
    };*/

/// ad hoc s�navormidele anal��side lisamiseks
typedef struct 
    {
    const FSxCHAR* sona;    ///< v�ti
    const FSxCHAR* lemma;
    const FSxCHAR* lp;
    const FSxCHAR* sl;
    const FSxCHAR* vorm;
    } FSxC5;

/*// Programmi sissekirjutatud loendi element.
//
/// Vaikimisi Copy-konstruktor on OK. @n
/// Vaikimisi omistamisoperaator on OK. @n
/// Selliste elementidega loendit kasutatakse ad hoc s�navormidele 
/// anal��side lisamiseks.
/// @attention Sellistest kirjetest moodustatud massiivis peavad
/// k�ik v�tmed olema unikaalsed.
class CFSxC5
    {
    public:
        const FSxCHAR* sona;    ///< kirje v�ti
        const FSxCHAR* lemma;
        const FSxCHAR* lp;
        const FSxCHAR* sl;
        const FSxCHAR* vorm;

        /// Konstruktor
        CFSxC5(
            const FSxCHAR* _sona_,
            const FSxCHAR* _lemma_,
            const FSxCHAR* _lp_,
            const FSxCHAR* _sl_,
            const FSxCHAR* _vorm_
            ) : sona(_sona_), lemma(_lemma_), lp(_lp_), sl(_sl_), vorm(_vorm_)
            {}

        /// V�rdleb kirjet v�tmega - kahendotsimiseks
        int Compare(const FSxCHAR* key, const int)
            {
            assert(key!=0);
            return FSxSTRCMP(sona, key);
            }
   
        /// V�rdleb kahte kirjet - j�rjestamiseks
        //
        /// @attention Sellistest kirjetest moodustatud massiivis peavad
        /// k�ik v�tmed olema unikaalsed.
        int Compare(const CFSxC5* rec, const int)
            {
            assert(rec!=0 && rec->sona!=0);
            int v = FSxSTRCMP(sona, rec->sona);
            assert(v != 0); // k�ik v�tmed peavad olema unikaalsed
            return v;
            }
    };*/

typedef struct // oletamisel noomeni l�pule eelnev t�htede hulk, l�pp ise ja talle vastav vorm 
    {
    FSXSTRING* eeltahed;
    const FSxCHAR* lopp;
    const FSxCHAR* vorm;
    // oletamise tabeli kasutamiseks vajalikud
    const FSxCHAR* tabeli_lopp; // l�pp, mille analoogia-vorm vorm on  
    const FSxCHAR* tabeli_vorm; // l�pule vastav vorm
    int      tyyp; // 0 - ainult �ldnimi; 1 �ldnimi ja p�risnimi; 3 ainult verb;
    } FSxC5I1;

/*// Programmi sissekirjutatud loendi element.
//
/// Vaikimisi Copy-konstruktor on OK. @n
/// Vaikimisi omistamisoperaator on OK. @n
/// Selliste elementidega loendit kasutatakse oletamisel. @n
/// Sellistest kirjetest tehakse korduvate v�tmetaga massiiv
class CFSxC5I1
    {
    public:
        const FSXSTRING* eeltahed;
        const FSxCHAR* lopp;        ///< kirje v�ti
        const FSxCHAR* vorm;
        // oletamise tabeli kasutamiseks vajalikud
        const FSxCHAR* tabeli_lopp; ///< l�pp, mille analoogia-vorm vorm on  
        const FSxCHAR* tabeli_vorm; ///< l�pule vastav vorm
        const int      tyyp;        ///< @a ==0 ainult �ldnimi; @a ==1 �ldnimi ja p�risnimi; @a ==3 ainult verb;

        /// Konstruktor
        CFSxC5I1(
            const FSXSTRING* _eeltahed_,
            const FSxCHAR*   _lopp_,       
            const FSxCHAR*   _vorm_,
            const FSxCHAR*   _tabeli_lopp_, ///< l�pp, mille analoogia-vorm vorm on  
            const FSxCHAR*   _tabeli_vorm_, ///< l�pule vastav vorm
            const int        _tyyp_         ///< @a ==0 ainult �ldnimi; @a ==1 �ldnimi ja p�risnimi; @a ==3 ainult verb;
            ) : eeltahed(_eeltahed_), lopp(_lopp_), vorm(_vorm_), 
                tabeli_lopp(_tabeli_lopp_), tabeli_vorm(_tabeli_vorm_), tyyp(_tyyp_)
            {         
            }

        /// V�rdleb kahte kirjet - vajalik j�rjestamiseks
        //
        /// Sellistest kirjetest koostatud massiiv 
        /// ei tohi sisaldada kahte �hesugust kirjet.
        int Compare(const CFSxC5I1* rec, const int)
            {
            int v = FSxSTRCMP(lopp, rec->lopp);
            if(v==0)
                v = FSxSTRCMP(vorm, rec->vorm);
            if(v==0)
                v = FSxSTRCMP((const FSxCHAR *)*(eeltahed), (const FSxCHAR *)*(rec->eeltahed));
            if(v==0)
                v = FSxSTRCMP(tabeli_lopp, rec->tabeli_lopp);
            if (v==0)
                v = FSxSTRCMP(tabeli_vorm, rec->tabeli_vorm);
            assert(v != 0);
            return v;            
            }

        /// V�rdleb kirjat v�tmega - vajalik kahendotsimiseks
        //
        /// Korduvad v�tmed
        /// on lubatud.
        int Compare(const FSxCHAR* key, const int)
            {
            return FSxSTRCMP(lopp, key);
            }
    };*/

typedef struct // oletamisel verbi l�pule eelnev t�htede hulk, l�pp ise ja talle vastav vorm 
    {
    FSXSTRING* eeltahed;
    const FSxCHAR* lopp;
    const FSxCHAR* vorm;
    // oletamise tabeli kasutamiseks vajalikud
    const FSxCHAR* tabeli_lopp; // l�pp, mille analoogia-vorm vorm on  
    const FSxCHAR* tabeli_vorm; // l�pule vastav vorm
    } FSxOC5;

/*// Oletajas kasutatava loendi element
class CFSxOC5
    {
    public:
        const FSXSTRING* eeltahed;
        const FSxCHAR* lopp;        ///< kirje v�ti
        const FSxCHAR* vorm;
        // oletamise tabeli kasutamiseks vajalikud
        const FSxCHAR* tabeli_lopp; ///< l�pp, mille analoogia-vorm vorm on  
        const FSxCHAR* tabeli_vorm; ///< l�pule vastav vorm

        /// Kontruktor
        CFSxOC5(
            const FSXSTRING* _eeltahed_,
            const FSxCHAR* _lopp_,
            const FSxCHAR* _vorm_,
            // oletamise tabeli kasutamiseks vajalikud
            const FSxCHAR* _tabeli_lopp_, ///< l�pp, mille analoogia-vorm vorm on  
            const FSxCHAR* _tabeli_vorm_  ///< l�pule vastav vorm
            ) : eeltahed(_eeltahed_), lopp(_lopp_), vorm(_vorm_), 
                tabeli_lopp(_tabeli_lopp_), tabeli_vorm(_tabeli_vorm_)
            {}

        /// V�rdleb kahte kirjet - kasutatakse j�rjestamisel
        int Compare(const CFSxOC5* rec, const int)
            {
            int v = FSxSTRCMP(lopp, rec->lopp);
            if (v==0)
                v = FSxSTRCMP((const FSxCHAR *)*(eeltahed), (const FSxCHAR *)*(rec->eeltahed));
            if (v==0)
                v = FSxSTRCMP(vorm, rec->vorm);
            if (v==0)
                v = FSxSTRCMP(tabeli_lopp, rec->tabeli_lopp);
            if (v==0)
                v = FSxSTRCMP(tabeli_vorm, rec->tabeli_vorm);
            assert(v != 0);
            return v;
            }

        /// V�rdleb kirje v�tit etteantud v�tmega - kasutatakse kahendotsimisel
        int Compare(const FSxCHAR* key)
            {
            return FSxSTRCMP( lopp, key);
            }
    };*/

typedef struct 
    {
    int  on_algvorm;
    int  pole_algvorm;
    const FSxCHAR* kohustuslik_tyvelp;
    const FSxCHAR* on_lopp;
    const FSxCHAR* on_sl;
    const FSxCHAR* on_vorm;
    const FSxCHAR* eelmistel_keelatud_tyvelp;
    int  lisatingimus;
    const FSxCHAR* uuele_tyvele_otsa;
    const FSxCHAR* uus_lp;
    const FSxCHAR* uus_sl;
    const FSxCHAR* uus_vorm;
    } FSxI2C5I1C4;

/*// Programmi sissekirjutatud loendi element
class CFSxI2C5I1C4
    {
    public:
        const int  on_algvorm;
        const int  pole_algvorm;
        const FSxCHAR* kohustuslik_tyvelp;
        const FSxCHAR* on_lopp;
        const FSxCHAR* on_sl;
        const FSxCHAR* on_vorm;             ///< kirje v�ti
        const FSxCHAR* eelmistel_keelatud_tyvelp;
        const int  lisatingimus;
        const FSxCHAR* uuele_tyvele_otsa;
        const FSxCHAR* uus_lp;
        const FSxCHAR* uus_sl;
        const FSxCHAR* uus_vorm;

        /// Konstruktor
        CFSxI2C5I1C4(
            const int  _on_algvorm_,
            const int  _pole_algvorm_,
            const FSxCHAR* _kohustuslik_tyvelp_,
            const FSxCHAR* _on_lopp_,
            const FSxCHAR* _on_sl_,
            const FSxCHAR* _on_vorm_,
            const FSxCHAR* _eelmistel_keelatud_tyvelp_,
            const int  _lisatingimus_,
            const FSxCHAR* _uuele_tyvele_otsa_,
            const FSxCHAR* _uus_lp_,
            const FSxCHAR* _uus_sl_,
            const FSxCHAR* _uus_vorm_
            ) : on_algvorm(_on_algvorm_), pole_algvorm(_pole_algvorm_), kohustuslik_tyvelp(_kohustuslik_tyvelp_), 
                on_lopp(_on_lopp_), on_sl(_on_sl_), on_vorm(_on_vorm_), 
                eelmistel_keelatud_tyvelp(_eelmistel_keelatud_tyvelp_), lisatingimus(_lisatingimus_),
                uuele_tyvele_otsa(_uuele_tyvele_otsa_), 
                uus_lp(_uus_lp_), uus_sl(_uus_sl_), uus_vorm(_uus_vorm_)
            {}

        /// V�rdleb kahte kirjet - vajalik j�rjestamiseks
        int Compare(const CFSxI2C5I1C4* rec, const int)
            {
            int v = FSxSTRCMP(on_vorm, rec->on_vorm);
            if (v==0)
                v = FSxSTRCMP(on_sl, rec->on_sl);
            if (v==0)
                v = FSxSTRCMP(on_lopp, rec->on_lopp);
            if (v==0)
                v = FSxSTRCMP(kohustuslik_tyvelp, rec->kohustuslik_tyvelp);
            if (v==0)
                v = FSxSTRCMP(eelmistel_keelatud_tyvelp, rec->eelmistel_keelatud_tyvelp);
            if (v==0)
                v = FSxSTRCMP(uuele_tyvele_otsa, rec->uuele_tyvele_otsa);
            if (v==0)
                v = FSxSTRCMP(uus_lp, rec->uus_lp);
            if (v==0)
                v = FSxSTRCMP(uus_sl, rec->uus_sl);
            if (v==0)
                v = FSxSTRCMP(uus_vorm, rec->uus_vorm);
            assert(v!= 0);
            return v;         
            }

        /// V�rdleb kirje v�tit etteantud v�tmega - vajalik kahendotsimiseks
        int Compare(const FSxCHAR* key, const int)
            {
            return FSxSTRCMP(on_vorm, key);        
            }
    };*/

/// Sorditava ja kahendotsitava d�nbaamilise massiivi modifikatsioon
//
/// Lisab sinna ainult �he 
/// spetsiifilise kahendotsimisefunktsiooni juurde
template <class REC, class KEY>
class TMPLPTRARRAYBIN3 : public TMPLPTRARRAYBIN<REC, KEY>
    {
    public:
        /// Kahendotsimine: leiab kirje viida ettentud pikkusega v�tme j�rgi
        //
        /// @return
        /// - @a !=NULL Leidis
        /// - @a ==NULL Ei leidnud, v�ti oli NULL-viit v�i 
        /// v�tme pikkus oli null.
        REC* Get(
	        const FSxCHAR* key, ///< V�tme viit (v�ib olla NULL-viit)
	        const int keyLen    ///< V�tme pikkus (v�ib olla null)
	        )
            {
            assert( keyLen >= 0);
            if (key == NULL || keyLen == 0)
                return NULL;
            FSXSTRING tmpString = key;
            tmpString[keyLen] = 0;
            return TMPLPTRARRAYBIN<REC, KEY>::Get((FSxCHAR *)((const FSxCHAR *)tmpString));
            }
    };

/// Ports programmi sissekirjutatud loendeid.
class MUUD_LOENDID
    {
    public:
        MUUD_LOENDID(void);
        
        //LOEND<FSxC1, FSxCHAR *> nr_lyh;
        //LOEND<FSxC1, FSxCHAR *> omastavad;     
        //LOEND<FSxC1, FSxCHAR *> pahad_hyyd;
        //LOEND<FSxC1, FSxCHAR *> head_om;
        //LOEND<FSxC1, FSxCHAR *> head_gene_lopud;

        CLOEND<FSxC1, FSxCHAR> nr_lyh;           ///< numbrile k�lge sobivad l�hendid
        CLOEND<FSxC1, FSxCHAR> omastavad;        ///< omastav ongi algvorm
        CLOEND<FSxC1, FSxCHAR> pahad_hyyd;       ///< ei sobi liits�nadesse
        CLOEND<FSxC1, FSxCHAR> head_om;          ///< sobivad liits�nade 2. komponendiks 
        CLOEND<FSxC1, FSxCHAR> head_gene_lopud;  ///< sobivad gene algvormi l�puks

    };


#endif




