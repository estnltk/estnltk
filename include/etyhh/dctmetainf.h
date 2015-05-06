#if !defined DCTMETAINF_H
#define DCTMETAINF_H

#include <time.h>

/** Sõnastik võib sisaldada seda tüüpi FILEINFOsid */
enum DCTELEMID
    {
    /** Väärtustamata muutuja tähistamiseks */
    DCTELEMID_NOTHING,
    /** Ühestamismärgendite loend */
    DCTELEMID_T3TAGS,
    /** Trigrammide maatriks */
    DCTELEMID_T3GRAMS,
    /** Leksikon: massiiv (mrf-infi-alguspos+sõnavorm) */
    DCTELEMID_T3LEX_WLST,
    /** Mitmesusklassid */
    DCTELEMID_T3M_KLASSID,
    /** Mis iganes */
    DCTELEMID_T3LEXCOOP
    };

/** Klass sõnastikulementide massiivi elemendi esitamiseks */
class DCTMETASTRCTELEM
    {
    public:        
        /** Annab selle sõnastikuelemendiga seotud info alguspositsiooni failis */
        long algusPos;
        
        /** Sõnastikuelemendi tüüp/ID */
        DCTELEMID dctElemId; 

        DCTMETASTRCTELEM(void) 
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        /** Võrdleb kirje võtit etteantud võtmega, vaja kahendotsimiseks */
        int Compare(const DCTELEMID* key, const int sortOrder)
            {
            assert(ClassInvariant());
            if(key==NULL)
                throw VEAD(ERR_X_TYKK,ERR_NULLPTR,__FILE__,__LINE__);
            int ret=(int)dctElemId - (int)*key;
            return ret;
            }

        /** Võrdleb kirjet etteantud kirjega, vaja järjestamiseks */
        int Compare(const DCTMETASTRCTELEM* rec, const int sortOrder )
            {
            assert(ClassInvariant());
            if(rec==NULL)
                throw VEAD(ERR_X_TYKK,ERR_NULLPTR,__FILE__,__LINE__);
            return Compare(&(rec->dctElemId), sortOrder);
            }

        /** Tekitame etteantud tüüpi tühja FILEINFO 
         * 
         * @param id -- seda tüüpi tühi sõnastikuelement
         * @param pos -- algab sõnastikus sellest positsioonist
         */
        void Start(const DCTELEMID id, const long pos)
            {
            dctElemId=id;
            algusPos=pos;
            }

        bool ClassInvariant(void)
            {
            return algusPos!= -1L;
            }

        bool EmptyClassInvariant(void)
            {
            return algusPos== -1L;            
            }
   private:
        void InitClassVariables(void)
            {
            algusPos= -1L;
            }

        /** Copy-konstruktor on illegaalne */
        DCTMETASTRCTELEM(const DCTMETASTRCTELEM&) { assert(false); }

        /** Omistamisoperaator on illegaalne */
        DCTMETASTRCTELEM& operator=(const DCTMETASTRCTELEM&) { assert(false); return *this;}
    };
    
/** Klass sõnastikuelementide massiivi esitamiseks
 * 
 * Sisaldab sõnastiku tegemise aega ja sõnastikuelementide loetelu
 * (DCTMETASTRCTELEM tüüpi kirjete massiivi mis on otsitav DCTELEMID järgi).
 * 
 * Klassimalli parameetrid:
 * <ul><li> DCTMETASTRCTELEM --
 *     <li> DCTELEMID --
 * </ul>
 */
class DCTMETASTRCT : 
    public TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>,
    public CPFSFile
    {
    public:
        enum {              //  012345678901234567 8
            timeStampLen=18 // \nAA.KK.PP TT:MM:SS\0
            };              // Pikkus ilma EOS-ita

        DCTMETASTRCT(void)
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        /**
         * 
         * @param dctFileName -- sõnastikufaili nimi
         */
        DCTMETASTRCT(const CFSFileName& dctFileName)
        try {
            InitClassVariables();
            Start(dctFileName);
            assert(ClassInvariant());
            }
        catch(...)
            {
            Stop();
            throw;
            }

        /**
         * 
         * @param dctFileName -- sõnastikufaili nimi
         */
        void Start(const CFSFileName& dctFileName)
            {
            char timeStampString[timeStampLen+1]; // +1 et EOS ära mahuks
            TMPLPTRARRAY<DCTMETASTRCTELEM>::Start(1,1);
            if(Open(dctFileName, FSTSTR("rb"))==false)
                { 
                throw VEAD(ERR_X_TYKK,ERR_OPN,__FILE__,__LINE__," ",
                        "Ei suutnud faili avada lugemiseks", (const FSTCHAR*)dctFileName); 
                }
            if(CPFSFile::Seek(-(timeStampLen), SEEK_END)==false || 
                                ReadBuffer(timeStampString,timeStampLen)==false)
                {
                throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__," ",
                        "Andmefail riknenud", (const FSTCHAR*)dctFileName); 
                }
            timeStampString[timeStampLen]='\0';
            timeStamp=timeStampString;
            if(timeStamp[ 0]!='\n'||timeStamp[ 3]!='.'||timeStamp[ 6]!='.'||
               timeStamp[ 9]!=' ' ||timeStamp[12]!=':'||timeStamp[15]!=':'||
               timeStamp[18]!='\0')
                {
                throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__," ",
                        "Andmefail riknenud", (const FSTCHAR*)dctFileName); 
                }
            if(CPFSFile::Seek(-(timeStampLen+1), SEEK_END)==false)
                {
                throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__," ",
                        "Andmefail riknenud", (const FSTCHAR*)dctFileName); 
                }
            int n;
            ReadUnsigned<UB1,int>(&n);
            if(CPFSFile::Seek(-(timeStampLen+1+n*5), SEEK_END)==false)
                {
                throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__," ",
                        "Andmefail riknenud", (const FSTCHAR*)dctFileName); 
                }
            DCTMETASTRCTELEM* ptr;
            for(int i=0; i<n; i++)
                {
                ptr=TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::AddPlaceHolder();
                int tmpInt;
                ReadUnsigned<UB1,int>(&tmpInt);
                ptr->dctElemId=(DCTELEMID)tmpInt;
                ReadUnsigned<UB4,long>(&(ptr->algusPos));
                }
            }

        /** Tekitame koha ettantud tüüpi sõnastikuelemendile
         * 
         * @param id -- seda tüüpi FILEINFOLE tekitame koha
         * @param pos
         * @return Viit loodud sünastikuelemendile
         */
        DCTMETASTRCTELEM* Add(const DCTELEMID id, const long pos)
            {
            DCTMETASTRCTELEM* ptr=TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::AddPlaceHolder();
            ptr->Start(id, pos);
            return ptr;
            }

        /** Tekitame uue sõnastikufaili ja initsialiseerime klassi
         * 
         * @param dctFileName -- sõnastikufaili nimi
         */
        void Creat(const CFSFileName& dctFileName)
            {
            if(Open(dctFileName, FSTSTR("wb+"))==false) 
                {
                throw VEAD(ERR_X_TYKK,ERR_OPN,__FILE__,__LINE__," ",
                        "Ei suuda tekitada andmefaili", (const FSTCHAR*)dctFileName); 
                }
            TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::Start(1,1);
            }

        /** Leiab sõnastikuelmendi alguspositsiooni sõnastikufailis
         * 
         * @param id -- sõnastikuelemendi tüüp
         * @return Vastava sõnastikuelemendi alguspositsioon sõnastikufailis
         * Erind, kui sellist tüüpi sõnastikuelementi polnud
         */
        long Find(const DCTELEMID id)
            {
            DCTMETASTRCTELEM* ptr=Get(&id);
            if(ptr==NULL)
                throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__);
            return ptr->algusPos;
            }

        /** Lugemisjärg sõnastikufailis etteantud kirjetüübi kohale */
        void Seek(const DCTELEMID id)
            {
            Seek2Pos(Find(id));
            }

        /** Lugemisjärg sõnastikufailis parameetdiga etteantud kohale*/
        void Seek2Pos(const long pos)
            {
            if(CPFSFile::Seek(pos)==false)
                 throw VEAD( ERR_X_TYKK, ERR_ROTTEN, __FILE__, __LINE__);
            }
        
        /** METAINFO sõnastikufailile sappa 
         * 
         * Sõnastikule sappa (uuesti) kirjutame ainult METAINFO, FILEINFOd 
         * jäävad endistele kohtadele failis.
         * Metainfo sõnastikufaili sabas on kujul:
         * <ul><li> 1bait  (1) FILEINFO tüüp, ehk siis DCTELEMID
         *     <li> 4baiti (1) FILEINFO alguspositsioon failis
         *     <li> 1bait  n ehk eelneva massiivi pikkus
         *     <li> 1bait  reavahetuse kood '\\012' 
         *     <li> 17baiti AA.KK.KP TT:MM:SS ehk aasta.kuu.päev tunnid.minutid,
         * sõnastiku kettale kirjutamise aeg
         */
        void Write(void)
            {
            Sort();
            for(int i=0; i<idxLast; i++)
                {
                // 1bait - sõnastikuosise liik
                WriteUnsigned<UB1, int>((int)(operator[](i)->dctElemId));
                // 4baiti - sõnastikuosise alguspositsioon
                WriteUnsigned<UB4, long>(operator[](i)->algusPos);
                }
            time_t t=time(NULL);
#if defined( __GNUC__ )
            tm* now=localtime(&t);
#else
            struct tm localnow, *now=&localnow;
            if(localtime_s(now, &t))
                now=NULL; //mingi jama aja k�ttesaamisega
#endif
            if(now==NULL)
                throw VEAD(ERR_X_TYKK,ERR_MINGIJAMA,__FILE__,__LINE__);

#if defined( KUNI_080814 )
            // 1bait - sõnastikuosiste arv
            // sõnastiku kokkukirjutamise aeg
                     //                     1 11 1 11 1 11
                     //          0 1 23 4 56 7 89 0 12 3 45 6 78
            sprintf(timeStamp, "%c\n%02d.%02d.%02d %02d:%02d:%02d",
                (char)idxLast,
                now->tm_year+1900-2000,
                now->tm_mon+1,
                now->tm_mday,
                now->tm_hour,
                now->tm_min,
                now->tm_sec);
            assert(strlen(timeStamp)+1==timeStampLen);
#endif
            WriteUnsigned<UB1, int>(idxLast);
            int nr;
            timeStamp.Empty();
            timeStamp += "\n";                      //[0] reavahetus
            if((nr=now->tm_year+1900-2000)<10)      //[1-2]aasta
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==3);
            
            timeStamp += '.';                       //[3]punkt
            if((nr=now->tm_mon+1)<10)               //[4-5]kuu
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==6);

            timeStamp += '.';                       //[6]punkt
            if((nr=now->tm_mday)<10)                //[7-8]kuupäev
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==9);

            timeStamp += ' ';                       //[9]tühik
            if((nr=now->tm_hour)<10)                //[10-11]tunnid
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==12);

            timeStamp += ':';                       //[12]koolon
            if((nr=now->tm_min)<10)                 //[13-14]minutid
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==15);

            timeStamp += ':';                       //[15]koolon
            if((nr=now->tm_sec)<10)                 //[16-17]sekundid
                timeStamp+='0';
            STRSOUP::UnsignedNum2Str<int, CFSAString, char, 10>(nr, timeStamp);
            assert(timeStamp.GetLength()==18);
                                                    //[18]stringilõputunnus
            
//timeStamp = "\n14.11.27 16:18:12"; //DB

            assert(timeStamp.GetLength()==18 && 18==timeStampLen);
            WriteBuffer(timeStamp,timeStampLen); //kirjutame ilma lõpetava 0-baidita
            }

        /** Taastame argimentideta kontrukturi järgse seisu */
        void Stop(void)
            {
            CPFSFile::Close();
            TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::Stop();
            InitClassVariables();
            }

        /** Argumentidega konstruktori järgne klassi invaraint */
        bool ClassInvariant(void)
            {
            if( timeStamp[ 0]!='\n'||timeStamp[ 3]!='.'||timeStamp[ 6]!='.'||
                timeStamp[ 9]!=' ' ||timeStamp[12]!=':'||timeStamp[15]!=':'||
                timeStamp[18]!='\0'||18!=timeStampLen)
                return false;
            return 
                TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::ClassInvariant();
            }

        /** Argumentideta konstruktori järgne klassi invariant */
        bool EmptyClassInvariant(void)
            {
            return timeStamp[0]=='\0' &&
                TMPLPTRARRAYBIN<DCTMETASTRCTELEM, DCTELEMID>::EmptyClassInvariant();
            }
        
        /** Sõnastiku tegemise aeg */
        CFSAString timeStamp;

    private:
        /** Muutujate algväärtustamiseks argumentideta konstruktoris */
        void InitClassVariables(void)
            {
            timeStamp.Empty();
            }

        /** Copy-konstruktor on illegaalne */
        DCTMETASTRCT(const DCTMETASTRCT&) { assert(false); }

        /** Omistamisoperaator on illegaalne */
        DCTMETASTRCT& operator=(const DCTMETASTRCT&) { assert(false); return *this;}    
    };

/** Klass 8bitiste cooperdatud stringide loendiga seatud info paiknemise esitamiseks
 * 
 * Kahendtabeli ja Cooperi meetodil pakkimise
 * kombinatsioon
 */
class DCTCOOPACKFILEINF
    {
    public:
        //enum
        //    {
        //    suurusKettal = 4+4+2 ///< Andmestruktuuri suurus failis
        //    };
        
        /** Sellest positsioonist algab kahendtabel */
        long posKahendTabeliAlgus;
        
        /** Sellest posotsioonist algavad kokkucooperdatud blokid */
        long posCooperdatudBlokkideAlgus;
        
        /** Coooperdatud bloki suurus */
        int  cooperdatudBlokiSuurus;
        
        /** Kahendtabelis olev sõna jrk nr kettal niimitme baidine */
        int  nBaidineIdx;

        /** Kirjete arv kahendtabelis==cooperdatud blokkide arv */
        int  kahendTabeliPikkus;

        DCTCOOPACKFILEINF(void)
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        /** Argumentidega konstruktor - Sõnastikfailist alguspsitsioonide lugemiseks */
        DCTCOOPACKFILEINF(
            DCTMETASTRCT& dct,
            const DCTELEMID dctElemId
            )
            {
            InitClassVariables();
            Read(dct, dctElemId);
            assert(ClassInvariant());
            }

        /** Sõnastikfailist FILEINFO lugemiseks */
        void Read(
            DCTMETASTRCT& dct,
            const DCTELEMID dctElemId
            )
            {
            if(dctElemId!=DCTELEMID_T3LEXCOOP)
                {
                throw VEAD(ERR_X_TYKK,ERR_ARGVAL,__FILE__,__LINE__,"Vigane sõnastikufail"); 
                }
            dct.Seek(dctElemId);
            if(dct.ReadUnsigned<UB4, long>(&posKahendTabeliAlgus       )==true &&
               dct.ReadUnsigned<UB4, long>(&posCooperdatudBlokkideAlgus)==true &&
               dct.ReadUnsigned<UB2, int >(&cooperdatudBlokiSuurus     )==true &&
               dct.ReadUnsigned<UB2, int >(&nBaidineIdx                )==true &&
               dct.ReadUnsigned<UB2, int >(&kahendTabeliPikkus         )==true )
                {
                return; //ok
                }
            throw VEAD(ERR_X_TYKK,ERR_ROTTEN,__FILE__,__LINE__,"Vigane sõnastikufail"); 
            }

        /** Sõnastikufaili FILEINFO kirjutamiseks
         * 
         * FILEINFO kirjutatakse faili alates jooksvast positsioonist
         * @param dct -- pakitud sõnastikufail
         * @return FILEINFO algusnihe sõnastikufailis
         */
        long Write(CPFSFile& dct)
            {
            long pos=dct.Tell();
            if(     dct.WriteUnsigned<UB4, long>(posKahendTabeliAlgus)==true &&
                    dct.WriteUnsigned<UB4, long>(posCooperdatudBlokkideAlgus)==true &&
                    dct.WriteUnsigned<UB2, int >(cooperdatudBlokiSuurus)==true &&
                    dct.WriteUnsigned<UB2, int >(nBaidineIdx)==true &&
                    dct.WriteUnsigned<UB2, int >(kahendTabeliPikkus)==true)
                {
#if !defined(NDEBUG)
                long endPos=dct.Tell();
                assert(endPos-pos==14);
#endif
                return pos;
                }
            throw VEAD(ERR_X_TYKK,ERR_WRITE,__FILE__,__LINE__,"$Revision: 1134 $"); 
            }

        /** "Starditud" klassi invaraint */
        bool ClassInvariant(void)
            {
            return 
                posKahendTabeliAlgus!= -1L && 
                posCooperdatudBlokkideAlgus!= -1L &&
                cooperdatudBlokiSuurus!= -1 &&
                nBaidineIdx!= -1 &&
                kahendTabeliPikkus!= -1;
            }

        /** Argumentideta konstruktori järgne klassi invariant */
        bool EmptyClassInvariant(void)
            {
            return 
                posKahendTabeliAlgus== -1L && 
                posCooperdatudBlokkideAlgus== -1L &&
                cooperdatudBlokiSuurus== -1 &&
                nBaidineIdx== -1 &&
                kahendTabeliPikkus== -1;
            }

    private:
        /** Muutujate algväärtustamiseks argumentideta konstruktoris */
        void InitClassVariables(void)
            {
            posKahendTabeliAlgus= -1L;
            posCooperdatudBlokkideAlgus= -1L;
            cooperdatudBlokiSuurus= -1;
            nBaidineIdx= -1;
            kahendTabeliPikkus= -1;
            }

    };

#endif // defined DCTMETAINF_H
