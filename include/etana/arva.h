#if !defined(ARVA_H)
#define ARVA_H
/*
* arvajaga seot v�rk:
*/

#include "fsxstring.h"
#include "mrflags.h"
#include "post-fsc.h"
#include "sloendid.h"
#include "silp.h"
#define PN_ENDLEN 5

typedef struct // kui on lihtsalt stringide ja numbrite massiiv
    {
    const FSxCHAR* tyvelp;
    int enne_silpe;
    } FSxOPAHALP;

typedef struct
    {
    int  n;                     ///< mitu t�hte algvormi t�vest eemaldada
    const FSxCHAR *u_tylp;      ///< string, mis algvormi t�vele otsa panna
    const FSxCHAR *lp;          ///< l�pp (nt de), mis t�vele otsa panna
    const FSxCHAR *vorm;        ///< mis p�hivorm siis saadakse (sg g, sg p, adt, pl g, pl p)
    const FSxCHAR *a_tylp;      ///< algvormi tyvelp
    const FSxCHAR *meta;        ///< h��likuklassid, millesse enne a_tylp olevad t�hed peavad kuuluma
    int  min_silpe;
    int  max_silpe;
    const FSxCHAR *tyypsona;
    const FSxCHAR *sonaliik;
    } FSxOTAB;

/// gene-oletajas kasutava tabeli kirje
//
/// Saadakse CFSxOTAB t��pi kirjest m�nede muutujate eemaldamisega.
/// Sellistest kirjetetest moodustame massiivi FSxGOTAB_ARRAY
class FSxGOTAB
    {
    // realisatsioon failis arva_av.cpp
    public:
        const FSxCHAR *a_tylp; ///< algvormi tyvelp
        const FSxCHAR *meta;   ///< h��likuklassid, millesse enne a_tylp olevad t�hed peavad kuuluma
        int  min_silpe;
        int  max_silpe;
        const FSxCHAR *sonaliik;
        const FSxCHAR *tyypsona;

        /// Argumentideta konstruktor
        FSxGOTAB(void)
            : a_tylp(NULL), meta(NULL), 
              min_silpe(0), max_silpe(0),
              sonaliik(NULL), tyypsona(NULL) 
              
            {            
            }

        /// Argumentideta konstruktori j�rgseks initsialiseerimiseks
        //
        /// Kopeerib argumentiks olevast kirjest 
        /// viitade v��rtused (ei reserveeri m�lu!)
        void Start(
            //const CFSxOTAB* rec
            const FSxOTAB* rec
            );

        /// Initsialiseerimata klassi invariant
        //
        /// @return
        /// - @a ==true OK
        /// - @a ==false Midagi on sassis
        bool EmptyClassInvariant(void)
            {
            return
                a_tylp==NULL && meta==NULL && sonaliik==NULL &&
                min_silpe==0 && max_silpe==0 && 
                tyypsona==NULL;
            }

        /// Initsialiseeritud klassi invariant
        //
        /// @return
        /// - @a ==true OK
        /// - @a ==false Midagi on sassis
        bool ClassInvariant(void)
            {
            return
                a_tylp!=NULL && meta!=NULL && sonaliik!=NULL && 
                min_silpe!=0 && max_silpe!=0 &&
                tyypsona!=NULL;
            }

        /// Funktsioon kirjete v�rdlemiseks
        //
        /// @return
        /// >0, <0 v�i ==0
        int Compare(
            const FSxGOTAB *rec, ///< Selle kirjega v�rdleme jooksvat
            const int sortOrder=0   ///< Seda parameetrit praegu ei kasuta
            );

        /// Funktsioon kirje v�rdlemiseks v�tmega
        //
        /// @return
        /// >0, <0 v�i ==0
        int Compare(
            const FSxCHAR *key, // seda v�rdleme a_tylp-ga
            const int sortOrder=0   ///< Seda parameetrit praegu ei kasuta
            );
    private:
        FSxGOTAB(const FSxGOTAB&) {assert(false);}
        FSxGOTAB& operator=(const FSxGOTAB&) {assert(false); return *this; } 
    };


/// gene-oletajas kasutav tabel
//
/// Koosneb FSxGOTAB t��pi kirjetest.
/// See on korduvate v�tmetega tabel.
class FSxGOTAB_ARRAY : public TMPLPTRARRAYBINDUP<FSxGOTAB,FSxCHAR>
    {
    public:
        /// Argumentideta konstruktor
        //
        /// See konstruktor
        /// �nnestub alati.
        FSxGOTAB_ARRAY(void)
            {            
            }

        /// Teeb unikaalsete kirjetega j�rjestatud massiivi.
        //
        /// Otsimisel tuleb arvestada, 
        /// et massiiv sisaldab korduvaid v�tmeid.
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        void Start(
            const FSxOTAB* array,
            const int len
            //TMPLPTRARRAYBINDUP<CFSxOTAB,  FSxCHAR>& oletajaTabel
            )
            {
            TMPLPTRARRAYBINDUP<FSxGOTAB,FSxCHAR>::Start(len, 0);
            //TMPLPTRARRAYBINDUP<FSxGOTAB,FSxCHAR>::Start(oletajaTabel.idxLast, 0);
            for(int i=0; i < idxMax; i++)
                {
                FSxGOTAB* rec=AddPlaceHolder();
                rec->Start(&(array[i]));
                //rec->Start(oletajaTabel[i]);
                }
            SortUniq();
            }

        bool ClassInvariant(void) const
            {
            return TMPLPTRARRAYBINDUP<FSxGOTAB,FSxCHAR>::ClassInvariant();
            }
    };

/// Klass tundmatute s�nade anal��si/s�nteesi oletamiseks
class OLETAJA_DCT
    {
    public:
        /// Argumenideta konstruktor
        //
        /// @throw  VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        OLETAJA_DCT(void); // falis sloendid.cpp

        CLOEND<FSxC1, FSxCHAR> harvad_lopud_1; ///< ei sobi oletamisel sageli p�risnime l�puks 
        CLOEND<FSxC1, FSxCHAR> sage_lopud_1;   ///< sobivad oletamisel h�sti p�risnime l�puks
        CLOEND<FSxC1,  FSxCHAR> pahad_sufid;    ///< ei sobi oletamisel sufiksiks
        CLOEND<FSxC1,  FSxCHAR> pahad_tyved2;   ///< ei sobi oletamisel nimis�na viimaseks komponendiks 
        CLOEND<FSxC1,  FSxCHAR> ns_tylopud;     ///< sg n mittesobivad t�vel�pud; oletamiseks 
        CLOEND<FSxC1,  FSxCHAR> sobivad_tyved2; ///< l�hikesed, aga ikkagi sobiksid oletamisel nimis�na viimaseks komponendiks
        CKLOEND<FSxC5I1, FSxCHAR> pn_lopud_jm;
        CKLOEND<FSxOC5, FSxCHAR> verbi_lopud_jm;
        CLOEND<FSxOPAHALP,  FSxCHAR> pahad_sg_n_lopud; ///< ei sobi oletamisel sg n s�na l�puks 
        CKLOEND<FSxOTAB,  FSxCHAR> oletaja_tabel;   ///< oletajas algvormide leidmiseks
        FSxGOTAB_ARRAY gene_oletaja_tabel;

        /// Klassi invariant
        //
        /// @return
        /// - @a ==true OK
        /// - @a ==false Midagi on valesti
        bool ClassInvariant(void) const
            {
            return (
                harvad_lopud_1.ClassInvariant()
                && sage_lopud_1.ClassInvariant()
                && pn_lopud_jm.ClassInvariant()
                && verbi_lopud_jm.ClassInvariant()
                && pahad_sufid.ClassInvariant()
                && pahad_tyved2.ClassInvariant()
                && ns_tylopud.ClassInvariant()
                && sobivad_tyved2.ClassInvariant()
                && pahad_sg_n_lopud.ClassInvariant()
                && oletaja_tabel.ClassInvariant()
                && gene_oletaja_tabel.ClassInvariant() //TODO: vt mis jama TV
                );
            }

        //CFSxOTAB* ot_viimane_kirje;
        FSxOTAB ot_viimane_kirje;

        FSXSTRING otsitav_tyvi;
        FSXSTRING otsitav_vorm;
        FSXSTRING a_tyvi;           ///< algvormi t�vi
        
        FSXSTRING otsitav_g_tyvi;   ///< gene oletamise v�rk
        FSXSTRING otsitav_sonaliik; ///< gene oletamise v�rk
        FSXSTRING otsitav_tylp;     ///< gene oletamise v�rk


        FSXSTRING *sobiv_algv(FSXSTRING *tyvi, FSXSTRING *lp, FSXSTRING *vorm);
        FSXSTRING *jargmine_sobiv_algv(void);
        bool pn_sobiv_kirje(void);
        void pohivorm_lp(FSXSTRING *lp1, FSXSTRING *vm1, FSXSTRING *lp2, FSXSTRING *vm2);
        bool pohivorm_lp_v(FSxCHAR eel, FSXSTRING *lp1, FSXSTRING *vm1, FSXSTRING *lp2, FSXSTRING *vm2);
        bool jargmine_pohivorm_lp_v(FSXSTRING *vm1, FSXSTRING *lp2, FSXSTRING *vm2);
        bool sobiks_nimeks(FSXSTRING *sisendsona);
        bool sobiks_sonaks(FSXSTRING *sisendsona);

        /// gene oletamise v�rk 
        const FSxCHAR *sobiv_analoog(
            FSXSTRING *tyvi, 
            FSXSTRING *sonaliik
            );

        /// gene oletamise v�rk 
        const FSxCHAR *jargmine_sobiv_analoog(void);

    private:  
        /// Illegaalne
        OLETAJA_DCT(const OLETAJA_DCT&) { assert( false ); }
  
        /// Illegaalne
        OLETAJA_DCT& operator=(const OLETAJA_DCT&) { assert(false);  return *this; }

        //FSXSTRING *konstrui_tyvi(FSXSTRING *tyvi, FSXSTRING *vorm, const CFSxOTAB *t);
        FSXSTRING *konstrui_tyvi(FSXSTRING *tyvi, FSXSTRING *vorm, const FSxOTAB *t);

        /// gene oletamise v�rk 
        const FSxCHAR *leia_analoog(FSXSTRING *tyvi, FSXSTRING *sonaliik, const FSxGOTAB *t);

    };

#endif





