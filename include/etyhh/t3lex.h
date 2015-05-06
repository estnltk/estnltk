#if !defined( T3LEX_H )
#define T3LEX_H

#include "fsxstring.h"
#include "tmplarray.h"
#include "loefailist.h"
#include "tmplptrsrtfnd.h"
#include "etmrf.h"

#include "t3common.h"

//=========================================================

typedef FSXSTRING MARGEND;

/** ühistamismärgendite loendi lugememine/kirjutamine ("taglist.txt") */
class T3TAGSPRE
    {
    public:
        /** ühestamismärgendite massiiv */
        TMPLPTRARRAYBIN2<FSXSTRING,CFSWString> margendid; 

        /// Konstruktor
        T3TAGSPRE(void)
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        /** "cooked"-korpusefaili põhjal ühestaminismärgendite massiivi tegemine */
        void TagsFromCooked(
            const CFSFileName& fileName,
            const PFSCODEPAGE codePage
            );

        /** ühestamismärgendite massiiv tekstifailist "taglist.txt" */
        //void TagsFromFile(void);

        /** ühestamismärgendite massiiv tekstifaili "taglist.txt" */
        void TagsToFile(void);

        /** Argumentideta konstruktori järgne invariant */
        bool EmptyClassInvariant(void) const
            {
            return margendid.idxMax >0;
            }

        /** Initsialiseeritud klassi invariant */
        bool ClassInvariant(void) const
            {
            return margendid.idxMax > 0;
            }

    private:

        /** Klassi esialgne initsialiseerimine konstruktoris */
        void InitClassVariables(void)
            {
            margendid.Start(130,50);
            }

        /** copy-konstruktor on illegaalne */
        T3TAGSPRE(T3TAGSPRE&) { assert(false); }

        /** omistamisoperaator on illegaalne */
        T3TAGSPRE& operator=(T3TAGSPRE&) { assert(false);  return *this; }
   };
   
//-----------------------------------------------------------

/** treeningkorpuse sõnavormiga seotud märgendi-info massiivi element */
class T3DCTRECINF
    {
    public:
        /** ühestamismärgendi indeks (võti) */
        char    margIdx;
        
        /** loendur */
        int     margCnt;
        
        /** tõenäosus */
        UKAPROB margProb;

        T3DCTRECINF(void) 
            {
            InitClassVariables();
            }

        /** võtmege võrdlemine (ühestamismärgendite indeksid) kahendotsimiseks */
        int Compare(const char *key, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            if(margIdx > *key)
                return  1;
            if(margIdx < *key)
                return -1;
            return 0;
            }

        /** kirjete võrdlemine järjestamiseks*/
        int Compare(const T3DCTRECINF *rec, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            assert(rec->ClassInvariant());
            return Compare(&(rec->margIdx));
            }

        void Start(const T3DCTRECINF& dctRecInf)
            {
            assert(dctRecInf.ClassInvariant());
            margIdx = dctRecInf.margIdx;
            margCnt = dctRecInf.margCnt;
            assert(ClassInvariant());
            }

        bool EmptyClassInvariant(void) const
            {
            return 
                margProb == 0.0 &&
                margIdx == 0 && margCnt == 0;
            }
        bool ClassInvariant(void) const
            {
            return margIdx >= 0 && margCnt >= 0;
            }
    private:
        T3DCTRECINF(T3DCTRECINF&) { assert(false); }
        T3DCTRECINF& operator=(T3DCTRECINF&) { assert(false);  return *this; }
        bool InitClassVariables(void)
            {
            margIdx = margCnt = 0;
            margProb = 0.0;
            return true;
            }
    };

/** Leksikoni kirje -- treeiningkorpuse sõnavormiga seotud märgendi-info massiiv */
typedef TMPLPTRARRAYSRT<T3DCTRECINF> T3DCTRECINFARR;

class T3DCTREC
    {
    public:
        /** sõnavorm treeningkorpusest, võti kahendotsimisel */
        CFSWString sona;
        
        /** selle sõnavormi esinemiste arv treeningkorpuses */
        int sonaCnt;
        
        /** treeningkorpuse sõnavormiga seotud märgendi-info massiiv */
        T3DCTRECINFARR dctRecInf;

        T3DCTREC(void)
            {
            InitClassVariables();
            }
        
        /** võtmega võrdlemine kahendotsimiseks */
        int Compare(const CFSWString* key, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            return sona.Compare((const FSWCHAR*)*key);
            }
        
        /** kirjega võrdlemine järjestamiseks */
        int Compare(const T3DCTREC* rec, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            assert(rec->ClassInvariant());
            return sona.Compare(rec->sona);
            }
        
        bool EmptyClassInvariant(void) const
            {
            return sonaCnt==0 && dctRecInf.idxLast>0;
            }
        
        bool ClassInvariant(void) const
            {
            return sonaCnt>=0 && dctRecInf.idxLast>0;
            }
    private:
        T3DCTREC(T3DCTREC&) { assert(false); }       
        T3DCTREC& operator=(T3DCTREC&) { assert(false);  return *this; }
        void InitClassVariables(void)
            {
            sonaCnt=0;
            dctRecInf.Start(5, 5);
            }
    };

/** Leksikon -- masssiiv treeningkorpuse sõnavormidest ja nondega seotud infost */    
class T3DCTRECPRE : public T3DCTREC
    {
    public:
        /** Leksikon */
        TMPLPTRARRAYBIN<T3DCTREC, CFSWString> dct; ///< Leksikon

        T3DCTRECPRE(void) : T3DCTREC() {};

        /** Leksikon "cooked"-korpusefailist
         * 
         * @param fileName -- treeningkorpuse failinimi
         * @param codePage -- treeningkorpuse kooditabel
         * @param margendid -- ühestamismärgendite massiiv 
         * @param gramm1
         */
        void LexFromCooked(
            const CFSFileName& fileName,
            const PFSCODEPAGE codePage,
            const TMPLPTRARRAYBIN2<FSXSTRING,CFSWString> &margendid,
            /*const bool lisaLexiMorfistMargendeid,*/
            SA1<int> &gramm1 /*, ETMRFA *mrf*/
            );

        /*
        void LexFromLex(
            const CFSFileName &fileName,
            const PFSCODEPAGE codePage,
            const TMPLPTRARRAYBIN2<PCFSWString,CFSWString> &margendid,
            const SA1<int> &gramm1
            );

        void LexToLex(
            const CFSFileName& fileName,
            const PFSCODEPAGE codePage,
            const TMPLPTRARRAYBIN2<PCFSWString,CFSWString>& margendid
            );
        */

        /** Leksikon tekstifaili "lex.txt"
         * 
         * @param margendid
         */
        void LexToFile(const TMPLPTRARRAYBIN2<FSXSTRING,CFSWString> &margendid);

        /** Leksikon tekstifailist lex.txt */
        void LexFromFile(void);  
        
        bool EmptyClassInvariant(void) const
            {
            return dct.idxLast>=0;
            }

        bool ClassInvariant(void) const
            {
            return dct.idxLast>=0;
            }
    private:
        /// copy-konstruktor on illegaalne
        T3DCTRECPRE(T3DCTRECPRE&) { assert(false); }

        /// omistammisoperaator on illegaalne
        T3DCTRECPRE& operator=(T3DCTRECPRE&) { assert(false);  return *this; }
;

    };
//-----------------------------------------------------------

/** Lemmast sõltumatute mitmesusklasside massiivi element */
class T3MITMESUSKLASS
    {
    public:
        T3DCTRECINFARR mitmesus;

        T3MITMESUSKLASS(void)
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        T3MITMESUSKLASS(T3DCTREC &dctRec)
            {
            InitClassVariables();
            mitmesus.Start(dctRec.dctRecInf.idxLast,0);
            int i;
            for(i=0; i<mitmesus.idxMax; i++)
                {
                mitmesus.AddClone(*(dctRec.dctRecInf[i]));
                }
            mitmesus.Sort();
            assert(ClassInvariant());
            }

        bool GetIdxid(
            TMPLPTRARRAYSRTINT &idxid) const
            {
            int i;
            idxid.Start(mitmesus.idxLast, 0);
            if(idxid.ClassInvariant()==false)
                return false;
            for(i=0; i<idxid.idxMax; i++)
                {
                INTCMP *p=idxid.AddPlaceHolder();
                if(p==NULL)
                    return false;
                p->obj=(int)(mitmesus[i]->margIdx);
                }
            return true;
            }

        void Start(const T3MITMESUSKLASS &rec)
            {
            int i;
            for(i=0; i<rec.mitmesus.idxLast; i++)
                {
                mitmesus.AddClone(*(rec.mitmesus[i]));
                }
            }

        void AddFrom(const T3MITMESUSKLASS &rec)
            {
            int i;
            for(i=0; i<mitmesus.idxLast; i++)
                {
                assert(mitmesus[i]->margIdx==rec.mitmesus[i]->margIdx);
                mitmesus[i]->margCnt+=rec.mitmesus[i]->margCnt;
                }
            }

        /** võtmega võrdlemine kahendotsimiseks */
        int Compare(const TMPLPTRARRAYSRTINT *key, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            int i, cmp=mitmesus.idxLast-key->idxLast;
            if(cmp) //erinev arv m�rgendeid, tuleb sellest
                return cmp;
            for(i=0; i<mitmesus.idxLast; i++)
                {
                char tmpKey=(char)((*key)[i]->obj);
                if((cmp=mitmesus[i]->Compare(&tmpKey))!=0)
                    return cmp;
                }
            return 0;
            }

        /** kirjega võrdlemine järjestamiseks */
        int Compare(const T3MITMESUSKLASS *rec, const int sortOrder=0) const
            {
            assert(ClassInvariant());
            assert(rec->ClassInvariant());
            int i, cmp=mitmesus.idxLast-rec->mitmesus.idxLast;
            if(cmp)
                return cmp;
            for(i=0; i<mitmesus.idxLast; i++)
                {
                if((cmp=mitmesus[i]->Compare(rec->mitmesus[i]))!=0)
                    return cmp;
                }
            return 0;
            }

        bool EmptyClassInvariant(void) const
            {
            return mitmesus.idxMax > 0;
            }

        bool ClassInvariant(void) const
            {
            return mitmesus.idxMax > 0;
            }
    private:
        void InitClassVariables(void)
            {
            mitmesus.Start(3,3);
            }

        /** copy-konstruktor on illegaalne */
        T3MITMESUSKLASS(T3MITMESUSKLASS&) { assert(false); }
        
        /** omistamisoperator on illegaalne */
        T3MITMESUSKLASS& operator=(T3MITMESUSKLASS&) { assert(false);  return *this; }
    };

/** Lemmast sõltumatute mitmesusklasside massiiv */
class T3MITMESUSKLASSIDPRE
    {
    public:
        /** lemmast sõltumatu mitmesusklasside massiiv */
        TMPLPTRARRAYBIN<T3MITMESUSKLASS, TMPLPTRARRAYSRTINT> mitmesusKlass;

        /**
         * 
         * @param lex
         * @param gramm1
         * @param mitmesusKlassidesIgnoreeeri
         * @param kasutaMitmesusKlasseJaotus
         */
        void MitmesusKlassidFromLex(
            const TMPLPTRARRAYBIN<T3DCTREC, CFSWString> &lex,
            const SA1<int> &gramm1,
            const int mitmesusKlassidesIgnoreeeri,
            const bool kasutaMitmesusKlasseJaotus
            );

        /**
         * 
         * @param margendid
         * @param gramm1
         */
        void MKlassidToFile(
            const TMPLPTRARRAYBIN2<FSXSTRING,CFSWString> &margendid,
            const SA1<int> &gramm1
            );

        /*
        bool MitmesusKlassidToFile(
            const CFSFileName& fileName,
            const PFSCODEPAGE codePage,
            const SA1<int> &gramm1,
            const TMPLPTRARRAYBIN2<PCFSWString,CFSWString>& margendid);
            */

        T3MITMESUSKLASSIDPRE(void)
            {
            InitClassVariables();
            }

        bool EmptyClassInvariant(void) const
            {
            return mitmesusKlass.idxMax > 0;
            }

        bool ClassInvariant(void) const
            {
            return mitmesusKlass.idxMax > 0;
            }
    private:
        void InitClassVariables(void)
            {
            mitmesusKlass.Start(30,30);
            }

        T3MITMESUSKLASSIDPRE(T3MITMESUSKLASSIDPRE&) { assert(false); }
        T3MITMESUSKLASSIDPRE& operator=(T3MITMESUSKLASSIDPRE&) { assert(false);  return *this; }

    };
//-----------------------------------------------------------

    class KOLMGRAMMIDEFAILIST : public CPFSFile
    {
    public:
        CFSWString margend;
        int loendur;

        KOLMGRAMMIDEFAILIST(void):CPFSFile() {};
        int Read(
            const PFSCODEPAGE codePage,
            const bool ainultMargendid=false)
            {
            int ret, pos, n;

            CFSAString rida, num;
            if(ReadLine(&rida)!=true)
                return -1; // fail otsas
            ret = (int)(rida.TrimLeft(" \t"));
            assert( ret >= 0 && ret < 3 );
            if(ainultMargendid && ret > 0)
                return ret;
            pos = (int)(rida.FindOneOf(" \t"));
            assert( pos > 0 );
            margend = FSStrAtoW(rida.Left(pos),codePage);
            if(ainultMargendid)
                return ret;
            num=rida.Mid(pos);
            num.Trim();
            n = STRSOUP::UnsignedStr2Num<int,char>(&loendur,(const char*)num);
            assert( n > 0 );            
            return ret;
            }
    private:
        KOLMGRAMMIDEFAILIST(KOLMGRAMMIDEFAILIST&) { assert(false); }       
        KOLMGRAMMIDEFAILIST& operator=(KOLMGRAMMIDEFAILIST&) { assert(false);  return *this; }
    };

class T3NGRAM
    {
    public:
        /** Trigrammide massiiv  */
        SA3<UKAPROB> tabel;


        T3NGRAM(void)
            {
            InitEmptyClassVariables();
            }

        /** Arvuta n-grammid "cooked"-korpusefailist
         * 
         * @param fileName -- sisend "cooked"-korpusefailist
         * @param codePage -- sisendi kooditabel
         * @param margendid -- ühestamismärgendite massiiv
         */
        void NGramsFromCooked(const CFSFileName& fileName,
            const PFSCODEPAGE codePage, const TMPLPTRARRAYBIN2<FSXSTRING,
                                                    CFSWString>& margendid);

        /*
        void NGramsFromNGrams(
            const CFSFileName& fileName,
            const PFSCODEPAGE codePage,
            const TMPLPTRARRAYBIN2<PCFSWString,CFSWString>& margendid
            );
        */

        void ArvutaTshikiPriki(const int margendid_idxLast);

        void ArvutaLambdad(const int margendid_idxLast);

        void ArvutaTabel(const int margendid_idxLast);

        SA1<int> gramm1; // NB! sõnastiku tegemine kasutab seda
                         //     mitmesusklasside tegemine kasutab seda

        // n-grammid tekstifailist "3grammid.txt"
        //void NGramsFromFile(
        //    const TMPLPTRARRAYBIN2<PCFSWString,CFSWString> &margendid
        //    );
        //void NGramsFromNGrams(
        //    const CFSFileName& fileName,
        //    const PFSCODEPAGE codePage,
        //    const TMPLPTRARRAYBIN2<PCFSWString,CFSWString>& margendid
        //    );

        /** n-grammid tekstifaili "3grammid.txt"
         * 
         * @param margendid
         */
        void NGramsToFile(const TMPLPTRARRAYBIN2<FSXSTRING,CFSWString> &margendid);

        /** Argumentideta kontruktori järgne invariant */ 
        bool EmptyClassInvariant(void) const
            {
            return true;
            }

        /** Initsialiseeritud klassi invariant */
        bool ClassInvariant(void) const
            {
            return tabel.ClassInvariant() &&
                  gramm1.ClassInvariant() &&
                  gramm2.ClassInvariant() &&
                  gramm3.ClassInvariant() ;
            }
    private:

        /** Muutujate esialgseks initsialiseerimiseks konstruktorites */
        void InitEmptyClassVariables(void)
            {
            nGrammeErinevaid[0]=nGrammeErinevaid[1]=nGrammeErinevaid[2]=0;
            nGrammeKokku[0]=nGrammeKokku[1]=nGrammeKokku[2]=0;                       
            }

        double lambda[3];
        SA2<int> gramm2;
        SA3<int> gramm3;
        int nGrammeErinevaid[3];
        int nGrammeKokku[3];
        T3NGRAM(T3NGRAM&) { assert(false); }       
        T3NGRAM& operator=(T3NGRAM&) { assert(false); return *this; }
    };

//-----------------------------------------

/**
 * 
 * @param flags -- morfi lipud
 * @param inCodePage -- treeningkorpuse kooditabel
 * @param inCooked -- treeningkorpus
 * @param mitmesusKlassidesIgnoreeeri
 */
void T3mestaTxtTab(
    const MRF_FLAGS *flags,
    const PFSCODEPAGE inCodePage,
    const FSTCHAR *inCooked,
    const int  mitmesusKlassidesIgnoreeeri
    );




#endif




