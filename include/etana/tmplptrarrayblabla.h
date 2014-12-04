#if !defined( CLOEND_H )
#define CLOEND_H


#include "post-fsc.h"

extern "C" {
    typedef int (*CMPFUNSRT)(const void* e1, const void* e2 );
    typedef int (*CMPFUNBS )(const void* e1, const void* e2 );
    }

/// Klass massiivist sorditud koopia tegemiseks ja sellest 2ndotsimiseks
template <class REC, class KEY> // <kirje-t��p, v�tme-t��p *>
class CLOEND
    {
    public:
        /// Argumentideta konstruktor
        //
        /// Argumentideta konstruktor
        /// �nnestub alati.
        CLOEND(void) throw()
            { 
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        /// Argumentidega konstruktor
        //
        /// Kui kirjete v�rdlusfunktsiooni pole antud, ei j�rjsesta
        /// ja eeldame, et kirjed on juba j�rjsestatud. 
        /// @throw VEAD
        CLOEND(
            REC* _ptr_,                 ///< massiivi viit
            const int _len_,            ///< massiivi pikkus
            const CMPFUNSRT _cmpsrt_,   ///< v�rdleb(kirje, kirje)
            const CMPFUNBS  _cmpbs_     ///< v�rdleb(v�ti,  kirje)
            )
        try
            {
            InitClassVariables();
            Start(_ptr_, _len_,  _cmpsrt_, _cmpbs_);
            assert( ClassInvariant() );
            }
        catch(...)
            {
            Stop();
            throw;
            }

        /// Klassi initsailiseerimiseks peale argumentideta konstruktorit
        //
        /// Kui kirjete v�rdlusfunktsiooni pole antud, ei j�rjsesta
        /// ja eeldame, et kirjed on juba j�rjsestatud. 
        /// @throw VEAD
        void Start(
            REC* _ptr_,                 ///< massiivi viit
            const int _len_,            ///< massiivi pikkus
            const CMPFUNSRT _cmpsrt_,   ///< v�rdleb(kirje, kirje)
            const CMPFUNBS  _cmpbs_     ///< v�rdleb(v�ti,  kirje)
            )
            {
            if(_ptr_==NULL || _len_<0)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 961 $"));
            Stop();
            if((ptr=(REC**)calloc(_len_, sizeof(REC*)))==NULL) // see malloc() on OK
                throw(VEAD(ERR_X_TYKK,ERR_NOMEM,__FILE__,__LINE__,"$Revision: 961 $"));
            len=(_len_);
            cmpsrt=(_cmpsrt_);
            cmpbs=(_cmpbs_);
            for(int i=0; i<len; i++)
                ptr[i]=_ptr_+i;
            if(_cmpsrt_!=NULL)
                sort();
            assert(ClassInvariant());
            }

        /// M�lu vabaks ja  pood kinni
        //
        /// @attention Vabastab ainult viitade massiivi,
        /// Viidatavade kirjeta vabastamisega ei tegele!
        void Stop(
            bool initClassVariables=true
            ) throw()
            {
            if(ptr==NULL)
                {
                assert(EmptyClassInvariant());
                return;
                }
            assert(ClassInvariant());
            free(ptr);
            if(initClassVariables)
                {
                InitClassVariables();
                assert(EmptyClassInvariant());
                }
            }

        ~CLOEND(void) 
            {
            Stop(false);
            }

        /// Kahendotsimine: v�ti (t�hejada+pikkus) -> kirje viidaks
        //
        /// @throw VEAD,
        /// CFSFileException,CFSMemoryException,CFSRuntimeException
        /// @return
        /// - @a !=NULL Leidis
        /// - @a ==NULL Ei leidnud
        const REC* Get(
	        const FSWCHAR* key, ///< V�tme viit
	        const int keyLen    ///< V�tme pikkus
	        ) const
            {
            assert( keyLen >= 0);
            assert( ClassInvariant() );

            if (key == NULL || keyLen <= 0)
                return NULL;
            CFSWString tmpString = key;
            assert(tmpString.GetLength()>=keyLen);
            tmpString[keyLen] = 0;
            return Get((const FSxCHAR *)tmpString);
            }

        /// Kahendotsimine: v�ti -> kirje viidaks
        //
        /// @return
        /// - @a !=NULL Leidis
        /// - @a ==NULL Ei leidnud
        const REC* Get(
	        const KEY* key ///< V�tme viit (KEY peab olema viitmuutuja t��p)
	        ) const
            {
            assert( ClassInvariant() );
            if (key==NULL)
                return NULL;
            const REC** rec=(const REC**)bsearch(key, ptr, len, sizeof(REC**), cmpbs);
            return rec==NULL ? NULL : *rec;
            }

        /// Kahendotsimine: v�ti -> indeksiks
        //
        /// @return
        /// - @a >=0 Leitud indeks
        /// - @a ==-1 Polnud
        int Find(
            const KEY* key
            ) const
            {
            assert( ClassInvariant() );
            if (key == NULL)
                return -1;
            REC** t=(REC**)bsearch(key, ptr, len, sizeof(REC**), cmpbs);
            return (t==NULL) ? -1 : t-ptr;
            }

        /// Lineaarne otsimine: v�ti -> kirje viidaks (ja indeksiks)
        //
        /// @return
        /// - @a !=NULL Leidis
        /// - @a ==NULL Ei leidnud
        const REC* LGetRec( 
            const KEY* key, ///< V�tme viit
            int* idx=NULL   ///< @a ==-1 polnud; @a >=0 leitud kirje indeks
            ) const
            {
            assert( ClassInvariant() );
            if (key == NULL)
                return NULL;
            for(int i=0; i < len; i++)
                {
                if(cmpbs(key, ptr+i)==0)
                    {
                    if(idx)
                        *idx = i;
                    return ptr[i];
                    }
                }
            if(idx)
                *idx = -1;
            return NULL; // ei leidnud
            }

        /// Lineaarne otsimine: v�ti -> indeksiks (ja kirje viidaks)
        //
        /// @return
        /// - @a >=0 Leitud kirje indeks
        /// - @a ==-1 Polnud
        int LGetIdx(
            const KEY* key,  ///< v�tme viit
            const REC** rec=NULL  ///< @a ==NULL polnud; @a !=NULL leitud kirje viit
            ) const
            {
            int idx;
            const REC* r=LGetRec(key, &idx);
            if(rec!=NULL)
                *rec=r;
            return idx;
            }

        /// Indeks kirje viidaks
        //
        /// @attention Ei kontrolli, et indeks
        /// j��b lubatud piiridesse.
        REC operator[] (
            const int idx ///< indeks
            ) const
            {
            assert( ClassInvariant() );
            if(idx<0 || idx>=len)
                throw(VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"$Revision: 961 $"));
            return ptr[idx];
            }
                  
        /// Kahendotsimine: v�ti -> kirje indeksiks
        //
        /// @return
        /// - @a >= 0 Kirje indeks
        /// - @a ==-1 Polnud
        int operator[] (
            const KEY key ///< V�tme viit
            ) const
            {
            return Find(key);
            }
 
        bool EmptyClassInvariant(void) const throw()
            {
            return len==0 && cmpsrt==NULL && cmpbs==NULL && ptr==NULL;
            };

        bool ClassInvariant(void) const throw()
            {
            // Kui kirjete v�rdlusfunktsiooni pole antud, ei j�rjsesta.
            // Eeldame, et on juba j�rjsestatud 
            return len > 0 && ptr!=NULL && cmpbs!=NULL;
            }

        CMPFUNSRT cmpsrt;   ///< Viit funktsioonile (v�rdleb kirjeid)
        CMPFUNBS  cmpbs;    ///< Viit funktsioonile (v�rdleb v�tit kirje v�tmega)
        REC **ptr;          ///< Viitade massiiv (j�rjestatud)
        int len;            ///< Viitade massiivi pikkus
        //CFSWString tmpString;///< Abistring

        /// Funktsioon kirjete j�rjestamiseks
        inline
        void sort(void)
            {
            assert( ClassInvariant() );

            qsort(ptr, len, sizeof(REC**), cmpsrt);
            };

        /// Argumentideta konstruktoris klassi muutujate esialgseks initsaliseerimiseks
        void InitClassVariables(void)
            {
            len=0;
            cmpsrt=NULL;
            cmpbs=NULL;
            ptr=NULL;
            };
    };

/// Korduvate v�tmetega loend
template<class REC, class KEY>
class CKLOEND : public CLOEND<REC, KEY>
    {
    public:
        /// Argumentideta konstruktor
        //
        /// See argumentideta konstruktor
        /// �nnestub alati.
        CKLOEND(void) {}

        /// Argumentidega konstruktor
        //
        /// @attention See konstruktor v�ib vaba m�lu
        /// puudusel eba�nnestuda. 
        /// @throw VEAD,
        /// CFSMemoryException, CFSRuntimeException
        CKLOEND(
            REC* _ptr_,                 ///< massiivi viit
            const int _len_,            ///< massiivi pikkus
            const CMPFUNSRT _cmpsrt_,   ///< v�rdleb(kirje, kirje)
            const CMPFUNBS  _cmpbs_):   ///< v�rdleb(v�ti,  kirje)
            CLOEND<REC, KEY>(_ptr_, _len_,  _cmpsrt_, _cmpbs_)
            {
            }

        /// Kahendotsimine: Leiab viida esimesele v�tmele vastavale kirjele
        //
        /// @return
        /// - @a !=NULL Viit kirjele
        /// - @a ==NULL Ponud
        const REC* Get(
            const FSWCHAR* key,  ///< v�ti 
            const int keyLen     ///< V�tme pikkus
            ) 
            {
            CLOEND<REC, KEY>::tmpString = key;
            CLOEND<REC, KEY>::tmpString[keyLen] = 0;            
            //TODO::ma arvan siin peaks ka olema lastKey=&tmpString;
            return Get((const FSxCHAR *)(CLOEND<REC,KEY>::tmpString));
            
            //LOEND<REC, KEY>::tmpString = key;
            //LOEND<REC, KEY>::tmpString[keyLen] = 0;            
            //return Get((FSxCHAR *)((const FSxCHAR *)LOEND<REC, KEY>::tmpString));
            }

        /// Kahendotsimine: Leiab viida esimesele v�tmele vastavale kirjele
        //
        /// @return
        /// - @a !=NULL Viit kirjele
        /// - @a ==NULL Ponud
        const REC* Get(
            const KEY* key ///< Viit v�tmele
            )   // v�tme viit --> kirje viidaks
            {
            int idx = CLOEND<REC,KEY>::Find(key);
            if(idx < 0)
                return NULL;
            while(idx>0 && 
                CLOEND<REC,KEY>::cmpbs(key, CLOEND<REC,KEY>::ptr+idx-1)==0)
                --idx;
            lastIdx=idx;
            lastKey=key;
            //return &(CLOEND<REC,KEY>::ptr[idx]);
            return CLOEND<REC,KEY>::ptr[idx];
            }

        /// Kahendotsimine: Leiab j�rgmise v�tmle vastava kirje
        const REC* GetNext(void)
            {
            if(++lastIdx < CLOEND<REC,KEY>::len && 
	           CLOEND<REC,KEY>::cmpbs(lastKey, CLOEND<REC,KEY>::ptr+lastIdx)==0)
                {
                //return &(LOEND<REC, KEY>::ptr[lastIdx]);
                return CLOEND<REC, KEY>::ptr[lastIdx];
                }
            return NULL;
            }

        int lastIdx;
        const KEY* lastKey;
    };

#endif


