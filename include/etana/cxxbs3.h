
// 2000.07.14 TV 

#if !defined( CxxBS3_H )
#define CxxBS3_H

#include <stdlib.h>

#include "tloendid.h"
#include "tmk2t.h"    
#include "result.h"
#include "ini_mrf.h"
#include "f-info.h"
#include "cxxcash.h"

#include "post-fsc.h"
#include "s6n0.h" // 2002.05.30
#include "tmk2tx.h"

// {{-bsearch.h-st
               
typedef struct  // kettal on 1bait + (1bait + 1bait)
    {
    unsigned char len;
    unsigned char s_nihe[2];
    } TABLE_DCT;
    

//typedef _int16 TYVE_NIHE;
typedef struct  // kahendtabeli element op m�lus
	{
	int len;	 // tyve pikkus baitides
	int s_nihe;  // tyve algus massivis	stm_buf
	} TABLE;

typedef struct
	{
	FSxCHAR  *v6tmed;   // Viit v�tmete puhvrile
	unsigned vbSuurus;  // V�tmete puhvri suurus baitides
	TABLE    *kTabel;   // Viit kahendtabelile
	int      ktSuurus;  // Kahendabeli pikkus
	} BTABLE;
// }}-bsearch.h-st


//*** -----------------------------------------------------------
//*** Siin tulevad p6his6nastiku kokku/lahtipakkimiseks vajalikud
//*** konstandid, andmestrukuurid, v@lismuutujad, funktsid
//***
//
// Sellisest failist on see v�rk tehtud
//
//ala#s+0-0_0 103=0,160,255,0
//alune#s+d-0_0 27=0,0,449,255,0
  

//#define DFLT_BUF_SIZE 256       // 256 S6nastikubloki suurus vaikimisi. 
#define DFLT_BUF_SIZE   512       // 512 S6nastikubloki suurus vaikimisi. 

#define NULL_LIIKI   (SONALIIKE-1) // vt kommentaari 'ini_mrf.h' failis
#if defined( FSCHAR_ASCII )
    #define EofB          '\377'    // '\xFF'
#elif defined( FSCHAR_UNICODE )     // kasutame UNICODE kooditabelit
    #define EofB          0xFFFF    // 0xFFFF
#else
    #error defineeri kas FSCHAR_ASCII v�i FSCHAR_UNICODE
#endif

#define POLNUD     -1  // genes tuleb selle asemele panna POLE_YLDSE v�i POLE_SEDA
#define POLE_YLDSE -2  // stringi x polnud ja stringi xy pole ka kindlasti
#define POLE_SEDA  -1  // stringi x polnud, aga string xy v�ib olla
#define V0RDLE      0

class PREFIKS
    {
    public:
        enum { pakitudPrefiksiSuurus=4 };

        inline int v_piir(void)      const {return prfxPiir;      };
        inline int v_samasid(void)   const {return prfxSamasid;   };
        inline int v_erinevaid(void) const {return prfxErinevaid; };
        inline int v_tabidx(void)    const {return prfxTabidx;    };

        inline void p_piir(const int _prfxPiir_) { prfxPiir=_prfxPiir_; };
        inline void p_samasid(const int _prfxSamasid_) { prfxSamasid=_prfxSamasid_; };
        inline void p_erinevaid(const int _prfxErinevaid_) { prfxErinevaid=_prfxErinevaid_; };
        inline void p_tabidx(const int _prfxTabidx_) { prfxTabidx=_prfxTabidx_; };

       void BytesToPrefiks(
            const unsigned char *ptr
            )
            {
            STRSOUP::ReadUnsignedFromString<UB1,int>(ptr  , &prfxPiir);
            STRSOUP::ReadUnsignedFromString<UB1,int>(ptr+1, &prfxSamasid);
            STRSOUP::ReadUnsignedFromString<UB1,int>(ptr+2, &prfxErinevaid);
            STRSOUP::ReadUnsignedFromString<UB2,int>(ptr+3, &prfxTabidx);
            }

        unsigned char *PrefiksToBytes(
            unsigned char *ptr,
            const int _prfxPiir_,
            const int _prfxSamasid_,
            const int _prfxErinevaid_,
            const int _prfxTabidx_,
            const int _pakitudPrefiksiSuurus_=pakitudPrefiksiSuurus
            )
            {
            if(_pakitudPrefiksiSuurus_!=pakitudPrefiksiSuurus)
                throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 1205 $");
            prfxPiir     =_prfxPiir_;
            prfxSamasid  =_prfxSamasid_;
            prfxErinevaid=_prfxErinevaid_;
            prfxTabidx   =_prfxTabidx_;
            return PrefiksToBytes(ptr);
            };

        unsigned char *PrefiksToBytes(
            unsigned char *ptr, //seal on alati konstantse pikkusega massiiv (pikkus 'pakitudPrefiksiSuurus')
            const int _pakitudPrefiksiSuurus_=pakitudPrefiksiSuurus
            ) const
            {
            if(_pakitudPrefiksiSuurus_!=pakitudPrefiksiSuurus)
                throw VEAD(ERR_MORFI_MOOTOR, ERR_MINGIJAMA, __FILE__, __LINE__,"$Revision: 1205 $");
            if(prfxPiir > 0xff)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 1205 $", "Liiga suur: prfxPiir"));
            STRSOUP::WriteUnsignedToString<UB1,int>(ptr  , prfxPiir);

            if(prfxSamasid > 0xff)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 1205 $", "Liiga suur: prfxSamasid"));
            STRSOUP::WriteUnsignedToString<UB1,int>(ptr+1, prfxSamasid);

            if(prfxErinevaid > 0xff)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 1205 $", "Liiga suur: prfxErinevaid"));
            STRSOUP::WriteUnsignedToString<UB1,int>(ptr+2, prfxErinevaid);

            if(prfxTabidx > 0xffff)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 1205 $", "Liiga suur: prfxTabidx"));
            STRSOUP::WriteUnsignedToString<UB2,int>(ptr+3, prfxTabidx);
            return ptr;
            };
    
    private:
        int prfxPiir;
        int prfxSamasid;
        int prfxErinevaid;
        int prfxTabidx;
    };
 
class LISAKR6NKSUD1 
    {
    public:
        int nKr6nksuBaiti;
        TMPLPTRARRAY<CFSbaseSTRING> liitPiirid, muudKr6nksud;
        MRF_FLAGS mrfFlags;

        bool Start(cFILEINFO *file_info);
        
        int LisaKdptr(  // 0=0k, -1 =jama --- Lisakr�nksud sisse
            const TYVE_INF *dptr,
            FSXSTRING *xstrOut,                 // v�ljundstring (sisendstring+kr�nksud)
            const FSXSTRING *xstrIn,            // sisendstring
            const int  mitmes_ptr_is);          // idx l�pugrupindusest
    };

typedef struct
    {
    PREFIKS prefiks;
    FSxCHAR LqpuTunnus;
    } ENDOFBLK;


// info, mis on vajalik suf sobivuse kontr-ks
typedef struct
	 {
	 char taandlp;  // sufiksi taandl"pp 
	 char tsl;      // s"naliik, millele suf v"ib liituda (indeks massiivis)
	 char ssl;      // sufiksi s"naliigi indeks; sõnaliikide string ise on sonaliik[sufix[i].ssl] 
	 char tylp;     // n"utav tyvel"pp (indeks massiivis) 
	 char mitutht;  // mitu ta"hte sufiksi lopust kuulub tegelikult tyvele 
    TYVE_INF suftyinf[SUF_LGCNT];  /* HJK 19.12.01 palakro'nksunduse jaoks */
    // kuna SUFINFO *sufix; siis (sonaliik[sufix[i].ssl])->GetLength() == sufix[i].suftyinf massiivi tegelik pikkus
    } SUFINFO;      
 
//**** suffiksite v�rgi l�pp 

// tyveinfo suurus m"alus 
//
#define  SizeOfLg2(nlg)   (nlg * sizeof(TYVE_INF)) 
#define  SizeOfEndOfBlk	  sizeof(ENDOFBLK) 

// tyveinfo suurus kettal (mitmesGrupis+grupiNr_lisa+Kr6nksudeGrupiNr) 
// grupiNr ja mitmesGrupis on 2 baidi peale kokku pakitud (10+6 bitti).
//
#define dSizeOfLg2(nlg,nKr6nksuBaiti)   (nlg * (sizeof(_uint8)+sizeof(_uint8)+nKr6nksuBaiti)) //suurus kettal

#define dSizeOfPrefiks    5 //kettal 5 baiti
#define dSizeOfEndOfBlk	  (dSizeOfPrefiks+dctsizeofFSxCHAR) 

#define LgCopy(kuhu, kust, mitu)    memmove(kuhu, kust, SizeOfLg2(sonaliik[mitu]->GetLength()))
#define GetLgNr(lg, indx)           ((TYVE_INF *)lg)[indx].lg_nr
#define GetKr6nksuGrupiNr(lg, indx) ((TYVE_INF *)lg)[indx].lisaKr6nksud
#define GetTabIdx(lg, indx)         ((TYVE_INF *)lg)[indx].idx.tab_idx
#define GetBlkIdx(lg, indx)         ((TYVE_INF *)lg)[indx].idx.blk_idx



class cTYVEDETABEL
    {
    protected:
        cTYVEDETABEL(void)
            {
//            DBSTDERR1("cTYVEDETABEL-0");
            tmp1=NULL;
            ps.v6tmed=NULL;
            ps.kTabel=NULL;
//            DBSTDERR1("cTYVEDETABEL-1");
            };

        ~cTYVEDETABEL(void)
            {
            if(tmp1     ) free(tmp1     );
            if(ps.v6tmed) free(ps.v6tmed);
            if(ps.kTabel) free(ps.kTabel);
            };

        bool TyvedSisse(cFILEINFO *CFileInfo);

        // lib_amor32/TarmoSource/bsearch.cpp
        bool KOtsi(
		    const BTABLE  *kt,
		    const FSxCHAR *v6ti,
		    const int      vPikkus,
		    int           *idx
		    ) const;
        
        void Stop(void);

        BTABLE   ps;          // p6hisa6nastik 
    private:
        unsigned char* tmp1;
    };

// failis S�nastik/readloe.cpp
//
class HJK_LOEND : public LOEND<FSxCHAR *,FSxCHAR *>
    {
    public:
        /// Argumentideta konstruktor
        //
        /// See konstruktor
        /// �nnestub alati.
        HJK_LOEND(void);

        /// Initsialiseerib klassi
        //
        /// Kui @a _ptr_==NULL siis 
        /// @n - massiivis @a _xstrArr_ on @a _len_/dctsizeofFSxCHAR elementi
        /// @n - iga elemendi suurus on @a dctsizeofFSxCHAR baiti
        /// @n - iga elemendi baidij�rg tuleb �igeks kohendada 
        /// ja suurus venitada sizeof(FSWCHAR) baidiseks
        /// @n - Start() funktsioon peab tagama @a free(_xstrArr_) 
        /// funktsiooni poole p��rdumise
        /// @n Kui parameeter @a _ptr_!=NULL siis
        /// @n - parameetrit @a _xstrArr_ ignoreeritakse
        /// @n - massiiv _ptr_ sisaldab @a _len_/sizeof(FSxCHAR) elementi
        /// @n - TODO::uhh mikngi kamarajura, uuri mis toimub
        /// @throw VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        void Start(
            const CMPFUNBS  _cmpbs_,
                ///< v�rdleb(v�ti,  kirje)
                ///<
            const int _len_,
                ///< Kui @a _ptr_==NULL 
                ///< @n siis on @a _xstrArr_ pikkus @n
                ///< Kui @a _ptr_!=NULL 
                ///< @n siis on @a _ptr_massiivi pikkus BAITIDES
            FSxCHAR *_xstrArr_,  
                ///< Kui @a _ptr_==NULL siis @a _xstrArr_ seal on @a _len_/dctsizeofFSxCHAR
                ///< t�hte, iga�ks dctsizeofFSxCHAR baiti pikk. Edasi reserveeritakse
                ///< @a sizeof(FSxCHAR)*_len_/dctsizeofFSxCHAR baiti m�lu, sinna teisendatakse
                ///< esialgsest puhvrist dctsizeofFSxCHAR baidised (tegelikult 2baidised) 
                ///< t�hed ja esialgne puver vabastatakse.
            FSxCHAR **_ptr_=NULL
            );
            
        ~HJK_LOEND(void);

    private:
        FSxCHAR *xstrArr;
    };

class SONALIIGID
    {
    public:
        SONALIIGID(void)
            {
            InitClassVariables();
            }

        bool Start(cFILEINFO *cfi)
            {
            assert( EmptyClassInvariant() );
            int i, len;
            long offSet=cfi->file_info.sonaliik;
            long lopp=cfi->file_info.loend[0];
            int  size=lopp - cfi->file_info.sonaliik; // sonaliikide tabeli pikkus            
            const unsigned char* tmp;
            
            bufTmp=new unsigned char[size];
            if(cfi->c_read(offSet, bufTmp, size) == false)
		        {
                Stop();
		        return false;
                }
            STRSOUP::ReadUnsignedFromString<UB4,int>(bufTmp, &sonalMassiiviPikkus);
            tmp=bufTmp+sizeof(UB4);
            try {
                sLiigid = new FSXSTRING[sonalMassiiviPikkus+1];
                for(i=0; i < sonalMassiiviPikkus; i++)
                    {
                    len=STRSOUP::FixStrByteOrder(sLiigid[i],tmp);
                    //len=STRSOUP::FixStrByteOrder(sLiigid+i,tmp);
                    tmp += len*dctsizeofFSxCHAR;
                    }
                sLiigid[sonalMassiiviPikkus] = FSxSTR("");
                }
            catch(...)
                {
                Stop();
                return false;
                }
            delete [] bufTmp;
            bufTmp=NULL;
            return true;
            }
        
        FSXSTRING *operator[] (const int idx) const
            {
            assert( ClassInvariant() );
            assert( idx==NULL_LIIKI || (idx >=0 && idx < sonalMassiiviPikkus) );

            return sLiigid+(idx==NULL_LIIKI ? sonalMassiiviPikkus : idx);
            }

        bool ClassInvariant(void) const
            {
            return sLiigid!=NULL && sonalMassiiviPikkus >0;    
            }

        bool EmptyClassInvariant(void) const
            {
            return bufTmp==NULL && sLiigid==NULL && sonalMassiiviPikkus==0;    
            }

        void Stop(void)
            {
            if(sLiigid)
                delete [] sLiigid;
            if(bufTmp)
                delete [] bufTmp;
            InitClassVariables();
            }

        ~SONALIIGID(void)
            {
            Stop();
            }

    private:
		unsigned char* bufTmp;
        FSXSTRING* sLiigid;
        int  sonalMassiiviPikkus;

        void InitClassVariables(void)
            {
            bufTmp=NULL;
            sLiigid=NULL;
            sonalMassiiviPikkus=0;
            }
    };

class FSXSTRARR
    {
    public:
        FSXSTRARR(void)
            {
            InitClassVariables();
            }

        bool Start(
            cFILEINFO *cfi,
            const long algus, 
            const int pikkus,
            const int nVeergu)
            {
            assert(EmptyClassInvariant());
            int i;
            assert( pikkus%nVeergu          == 0 );
            assert( pikkus%dctsizeofFSxCHAR == 0 );
            len=pikkus/nVeergu/dctsizeofFSxCHAR;

            try {
                tmpXptr= new unsigned char[pikkus];
	            if(cfi->c_read(algus, tmpXptr, pikkus)==false)
		            {
                    Stop();
		            return false;
		            }
                xstrArr=new FSXSTRING[len]; // stringide massiiv
                for(i=0; i < len; i++)
                    {
                    // See kirjutab stringile t�hthaaval juurde
                    // ja v�ib seega throw()'ga vea tagasi anda.
                    STRSOUP::FixStrByteOrder(xstrArr[i],tmpXptr + (i*nVeergu*dctsizeofFSxCHAR));
                    //STRSOUP::FixStrByteOrder(xstrArr+i,tmpXptr + (i*nVeergu*dctsizeofFSxCHAR));
                    assert( xstrArr[i].GetLength() < nVeergu );
                    assert( i*nVeergu*dctsizeofFSxCHAR+nVeergu*dctsizeofFSxCHAR <= pikkus );
                    }
                }
            catch(...)
                {
                Stop();
                return false;
                }
            delete [] tmpXptr;
            tmpXptr=NULL;

            assert( ClassInvariant() );
            return true;
            }

        const FSxCHAR *operator[] (const int idx) const
            {
            assert( ClassInvariant() );
            assert( idx >=0 && idx < len );

            return (const FSxCHAR *)(xstrArr[idx]);
            }

        bool ClassInvariant(void) const
            {            
            return tmpXptr==NULL // seda kasutame ainult Start() funktsiooni sees
                && xstrArr!=NULL && len>0;    
            }

        bool EmptyClassInvariant(void) const
            {            
            return tmpXptr==NULL // seda kasutame ainult Start() funktsiooni sees
                && xstrArr==NULL && len==0;    
            }

        void Stop(void)
            {
            if(tmpXptr)
                delete [] tmpXptr;
            if(xstrArr)
                delete [] xstrArr;
            InitClassVariables();            
            }

        ~FSXSTRARR(void)
            {
            Stop();
            }

    private:
        void InitClassVariables(void)
            {
            tmpXptr=NULL;
            xstrArr=NULL;
            len=0;
            }

        unsigned char *tmpXptr; ///< Ajutine puhver Start() funktsioonis kasutamiseks
        FSXSTRING *xstrArr;
        int  len;
    };


extern "C" int FSxvrdle(const void *ee1, const void *ee2 );// vajalik loenditest 2ndotsimiseks

/// S�nastikuga tegelev klass
class DCTRD:
    public cFILEINFO,
    public cTYVEDETABEL, 
    public LISAKR6NKSUD1,
    public cCACHE
    {
    public:
        DCTRD(void)
            {
//DBSTDERR1("DCTRD0");
            NulliViidad();
//DBSTDERR1("DCTRD1");
            }

        bool EmptyClassInvariant(void)
            {
            return true;
                //cFILEINFO::EmptyClassInvariant()
                //TODO:: && cTYVEDETABEL::EmptyClassInvariant()
                //TODO:: && LISAKR6NKSUD1::EmptyClassInvariant()
                //TODO:: && cCACHE::EmptyClassInvariant()
                ;
            }

        bool ClassInvariant(void)
            {
            return
                cFILEINFO::ClassInvariant()
                //TODO:: && cTYVEDETABEL::ClassInvariant()
                //TODO:: && LISAKR6NKSUD1::ClassInvariant()
                //TODO:: && cCACHE::ClassInvariant()
                ;
            }

        /// Avab p�his�nastiku ja loeb sealt loendid jms sisse
        //
        /// @throw VEAD,
        /// CFSFileException, CFSMemoryException, CFSRuntimeException
        void Open(
            const CFSFileName *pS6n);

        void Close(void);

        ~DCTRD(void)
            {
            Close();    
            };

        /// Otsi t�ve
        //
        /// @return
        /// - @a ==NULL �heski l�pugrupis polnud vajalikke vorme
        /// - @a !=NULL Leidis
        bool OtsiTyvi(
	        const AVTIDX *idx,
            const int lopp,
            const int vorm,
            FSXSTRING *tyvi
            );

        SONALIIGID sonaliik;    ///< s�naliikude massiiv
        MKTAc tyveMuutused;        
        GRUPP	*groups;        ///< l�pugrupid 
        unsigned homo_form;     ///< homon. loppude max arv 1 lgr-s        
        int vormnr( const FSxCHAR *lp ) const ;
        char *fgr;
        char *gr;               ///< l�pugruppide l�pujadad 
        HJK_LOEND l6ppudeLoend;
        HJK_LOEND vormideLoend;
        int sg_n, sg_g, pl_n, ma;   ///< gene kasutab neid 
        char lopp_ma;
        char lopp_d;
        int suffnr( const FSxCHAR *suf ) const;
        SUFINFO *sufix;         ///< suf seot. info 

    protected:

        HJK_LOEND sufiksiteLoend;
        HJK_LOEND prefiksiteLoend;

        PREFINFO *prfix;        ///< pref. seot. info 
        unsigned gr_size;       ///< l�pugruppide l�pujadade suurus
        int taandlnr;           ///< taandliikide arv 
        int tyvelpnr;           ///< t�vel�ppude arv 
        
	FSXSTRARR taandliik;
                                // sl, mida suf, pref v�iks n�uda 
                                // 'F...' - ainult 'pxris' suf sl. 
	                        // 0 - suf, pref ei n�ua mingit sl 
        FSXSTRARR tyvelp;   // milline peaks tüve tagumine ots olema 


        char lopp_a;
        char lopp_da;
        char lopp_dama;
        char lopp_dav;
        char lopp_des;
        char lopp_dud;
        char lopp_es;
        char lopp_mata;
        char lopp_nud;
        char lopp_t;
        char lopp_ta;
        char lopp_tama;
        char lopp_tav;
        char lopp_te;
        char lopp_tes;
        char lopp_tud;
        char lopp_v;
        char lopp_0;
        char suva_lp;

        int sg_p, adt, pl_g, pl_p, da, suva_vrm;
        
        HJK_LOEND dctLoend[LOENDEID];
        

        char lpnr( const FSxCHAR *lp ) const ;
        int preffnr( const FSxCHAR *pref ) const ;

        // sobivus.cpp
        int endingr(int grnr, char end);

        /// Kontrollib, kas l�pugrupp sisaldab ettenatud vormi
        //
        /// @return
        /// - @a ==0 Vajalik lopp-vorm l�pugrupis olemas
        /// - @a ==-1 Pole
        int LopugruppSisaldabVormi(
            int lgNr,       ///< kas see l�pugrupp...
            int lopunr,     ///< ...sisaldab sellist loppu ja...
            int vorm        ///< ...sellist vormi?
            );

    private:
        void readeel(void);  /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readends(void); /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readfgrs(void); /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readfms(void);  /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readgrs(void);  /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readloe(int i); /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readprf(void);  /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void readsuf(void);  /// @throw VEAD,CFSFileException,CFSMemoryException,CFSRuntimeException
        void char2sufinfo(SUF_TYVE_INF *ch, TYVE_INF *ti);
        
        /// Avab faili ja loeb midagi sisse
        //
        /// @throw VEAD,
        /// CFSFileException,CFSMemoryException,CFSRuntimeException
        void open_d1(const CFSFileName *pSon);

        /// Loeb midagi sisse
        //
        /// @throw VEAD,
        /// CFSFileException,CFSMemoryException,CFSRuntimeException
        void open_d2(void);
        void NulliViidad(void);
        void VabastaViidad(void);

        char* tmpCharPtr;   ///< ajutine puhver, mida kasutavad s�nstikku initsialiseerivad alamprogrammid

    };

//*** need funktsid on nyyd vajalikud pakitud p6his6nastiku
//*** tekitamiseks ja ei millekski muuks.

void cXXinit3(FILE_INFO &file_info);
bool cXXget2(               // ==true: j�rjekordne rida hakitud; ==false: fail otsas v�i viga
    CPFSFile &p6hisS6nTxt,  // seda cooperdame 
    CFSbaseSTRING *tyvi2,   // j�rjekorden t�vi
    int *tabidx,            // indeks
    int *hhhidx,
    TYVE_INF *lg,           // t�veinf
    int *lgcnt);            // t�idetud struktuuride arv t�veinfis
void cXXpack2(void);
void cXXtest(void);
void cXXkontr(void);
void testi_sovitajat(void);

//------------- op-m@lus ----------------

#define InitLg(lg)       // Ei tee midagi. 
#define PutTyMuutGrupisMitmes(lg,indx,n) ((TYVE_INF *)lg)[indx].idx.blk_idx=(_uint8)n
#define PutTyMuutGrupiNr(     lg,indx,n) ((TYVE_INF *)lg)[indx].idx.tab_idx=(_int16)n
#define PutKr6nksuGrupiNr(    lg,indx,n) ((TYVE_INF *)lg)[indx].lisaKr6nksud=(_int16)n
#define PutPiiriGrupiNr(      lg,indx,n) ((TYVE_INF *)lg)[indx].piiriKr6nksud=(int)n

class cTYVEINF : public DCTRD
    {
    public:
        cTYVEINF(void) 
            {
            }
        TYVE_INF dptr[SONAL_MAX_PIK];    ///< tüve kõigi homonüümide infode massiiv             

        /** Otsib sõnastikust tyvele vastavat tyveinfi
         * 
         * tulemuseks on massiiv, sest tüved võivad olla homonüümsed, 
         * nt kanna _S_ ja kanna _V_
         * @param stem - otsitav tüvi
         * @param index - *index on sõnaliikide tabeli indeks;
         * (sonaliik[*index])->GetLength() == massiivi dptr tegelik pikkus;
         * sonaliik[*index][i] == dptr[i]-le vastav sõnaliik
         * @return 
         * <ul><li> ==0 -- leidis tüve sõnastikust; tulemus dptr ja *index-is
         *      <li> ==POLE_SEDA -- seda polnud, aga pikemat võib olla, nt kan (aga kand võiks olla olemas)
         *      <li> ==POLE_YLDSE -- polnud (ja ka pikemat varianti ei saa olla)
         *      <li> >0 -- jama
         * </ul>
         */
        int cXXfirst(const FSXSTRING *stem, int *index);

        /** Otsib sõnastikust tyvele vastavat tyveinfi
         * 
         * tulemuseks on massiiv, sest tüved võivad olla homonüümsed, 
         * nt kanna _S_ ja kanna _V_
         * @param stem - otsitav tüvi
         * @param slen - tüve pikkus
         * @param index - *index on sõnaliikide tabeli indeks;
         * (sonaliik[*index])->GetLength() == massiivi dptr tegelik pikkus;
         * sonaliik[*index][i] == dptr[i]-le vastav sõnaliik
         * @return 
         * <ul><li> ==0 -- leidis tüve sõnastikust; tulemus dptr ja *index-is
         *      <li> ==POLE_SEDA -- seda polnud, aga pikemat võib olla, nt kan (aga kand võiks olla olemas)
         *      <li> ==POLE_YLDSE -- polnud (ja ka pikemat varianti ei saa olla)
         *      <li> >0 -- jama
         * </ul>
         */
        int cXXfirst(         
	        const FSxCHAR *stem,
	        const int     slen,
	        int          *index
            );

    private:
        // 2002.05.30-{{
        
        unsigned kcnt;
        unsigned char *pptr;///< jooksev PREFIKS teisendamata kujul, nagu ta on failis
        PREFIKS  pre;       ///< jooksev prefiks, �iges j�rjekorras baitidega
        unsigned stem_no;   ///< jooksva t�ve #

        /// Kui otsitav t�vi oli 2ndtabelis, loeb k�shist bloki ja veel miskit
        //
        /// @throw VEAD
        void FindBt(
	        const int tab_idx, ///< 2ndtabeli index = k�shi bloki nr 
	        int *index);

        /// Kui otsitav t�vi polnud 2ndtabelis
        //
        /// @return
        /// - @a ==POLE_YLDSE
        /// - @a ==POLE_SEDA
        /// - @a ==0
        int FindBlk(
	        const int      tab_idx,     ///< 2ndtabeli index = k�shi bloki nr
	        const FSxCHAR *stem,        ///< otsitav t�vi
	        const int      slen,        ///< t�ve pikkus
	        int           *index        ///< s�naliikide tabeli idx v�lja
            );
        
        /// Otsib blokist
        //
        /// @return
        /// - @a ==POLE_YLDSE
        /// - @a ==POLE_SEDA
        /// - @a ==s�naliikide-tabeli-idx
        int FindDb(
	        const FSxCHAR *stem,	///< otsitav tyvi
	        const int      slen	    ///< t�ve  pikkus
            );

        /// Otsib v�rdlemiseks sobivat t�ve
        //
        /// @return
        /// - @a ==POLE_YLDSE
        /// - @a ==POLE_SEDA
        /// - @a ==V0RDLE
        int  NextStem(void);
        /// J�rgmine prefiks
        void NextPre(void);
        
        // }}-2002.05.30
        /*
        int cXXfirstOld(               // otsib tyve ja tyveinfi 
	        const char   *stem,
	        const int    slen,
	        int          *index);
            */
        };


// Siia alla tuleks korraldada s�nastiku/loendite failist sisselugemise 
// ja nendest otsimisega seotud klassid
//
class MRFDCT : public cTYVEINF
    {
    public:
        MRFDCT(void) 
            {
            };
    };

#endif
