
// 1995 
//
// 2002.03.14 klassiks �mberv��natud
// 2002.09.11 CPFSCFile peale �mbermuditud

#if !defined( F_INFO_H )
#define F_INFO_H

#include "post-fsc.h"
#include "suurused.h"
#include "ini_mrf.h" // sealt tuleb LOENDEID konstant
#include "viga.h"
#include "tmplptrsrtfnd.h"

class THFILEINFO;

class XFILEINFO
    {
    public:
        XFI_TYPE xfiType;
        long xfiOffSet;

        XFILEINFO(void) {};

        XFILEINFO(
            const XFI_TYPE _xfiType_, 
            const long _xfiOffSet_)
            {
            Start(_xfiType_,_xfiOffSet_);
            assert( ClassInvariant() );
            };

        void Start(
            const XFI_TYPE _xfiType_, 
            const long _xfiOffSet_) 
            {
            xfiType=_xfiType_;
            xfiOffSet=_xfiOffSet_;

            assert( ClassInvariant() );
            };

        int Compare(const XFI_TYPE *pXFIType, const int sortOrder=0) const
            {
			FSUNUSED(sortOrder);
            assert( ClassInvariant() );

            if(xfiType < *pXFIType)
                return -1;
            if(xfiType > *pXFIType)
                return  1;
            return 0;
            };

        bool ClassInvariant(void) const
            {
            return xfiType >=0 && xfiOffSet > 0L;
            };
    };

class METAFILEINFO : public TMPLPTRARRAYLIN<XFILEINFO, XFI_TYPE> 
    {
    public:
        CPFSFile dctFile;

        METAFILEINFO(void) /*: xfiOffSet(-1L)*/ {};
        
        // xfiOffSet == metainfi alguspos v�i failil�pupos (kui metainfi pole)
        //
        bool ReadMeta(
            const CFSFileName *pDctName, 
            const FSTCHAR *opnMode=FSTSTR("rb"))
            {
            if(dctFile.Open(*pDctName, opnMode)==false)
                return false;
            if(dctFile.Seek(0L, SEEK_END)==false)
                return false;
            long dctFileLen=dctFile.Tell();
            if(dctFile.Seek(dctFileLen-2)==false)
                return false;
            char filosoft[2];
            if(dctFile.ReadChar(filosoft)==false || dctFile.ReadChar(filosoft+1)==false)
                return false;
            if(strncmp(filosoft, "FS", 2)!=0)
                {
                Start(1,1);
                }
            else
                {
                if(dctFile.Seek(dctFileLen-3)==false)
                    return false;
                int idxMax;
                if(dctFile.ReadUnsigned<UB1,int>(&idxMax)==false)
                    return false;
                Start(idxMax, 1);
                 if(dctFile.Seek(dctFileLen-3-idxMax*5)==false)
                    return false;
                for(int i=0; i<idxMax;i++)
                    {
                    XFILEINFO *pxfInfo=AddPlaceHolder();
                    assert( pxfInfo!=NULL );
                    int int_xfi_type;
                    if(dctFile.ReadUnsigned<UB1,int>(&int_xfi_type)==false)
                        return false;
                    pxfInfo->xfiType=(XFI_TYPE)int_xfi_type;
                    if(dctFile.ReadUnsigned<UB4,long>(&(pxfInfo->xfiOffSet))==false)
                        return false;
                    }
                }
            return true;
            };

        bool Seek2(const XFI_TYPE x)
            {
            XFILEINFO *pxfi=Get(&x);
            if(pxfi)
                {
                return dctFile.Seek(pxfi->xfiOffSet);
                }
            return false;
            };

       bool WriteMeta(void)
            {
            if(dctFile.Seek(0L, SEEK_END)==false)
                return false;
            for(int i=0; i < idxLast; i++)
                {
                if(dctFile.WriteUnsigned<UB1,XFI_TYPE>(rec[i]->xfiType)==false)
                    return false;
                if(dctFile.WriteUnsigned<UB4,long>(rec[i]->xfiOffSet)==false)
                    return false;
                }
            if(dctFile.WriteUnsigned<UB1,int>(idxLast)==false)
                return false;
            if(dctFile.WriteString("FS", 2)==false)
                return false;
            return true;
            };

   };

typedef struct
    {
    //--- algused ---

    long    bt_offset;       // 32 kahendtabeli    algus       
    long    sa_offset;       // 31 t6vede massiivi algus       
    long    tyveL6ppudeAlgus;// 30 t�vel�ppude 2ndtabel        
    long    piiriKr6nksud;   // 29 
    //----------------------------NB! See tykk peab j"a"ama kokku
    //                            ja faili l~opust sama kaugele!
    int	   VersionMS;	    // 28     siia tuli nyyd  versiooni'info juurde 
    int	   VersionLS;	    // 27     vt init1.c                            
    int    buf_size;        //        s6nastiku bloki suurus      
    //----------------------------NB! Peale buf_size-i peab tulema 26*4 baiti!!! 
    
    long    tyveKr6nksud;    // 26 

    long    ends;	        // 25 l6ppude massiivi algus      
    long    groups;	        // 24 l-gruppide mass. algus      
    long    gr;				// 23 l-gruppide l6pujadade algus 
    long    forms;           // 22 vormide massiivi algus      
    long    fgr;             // 21 v_gruppide jadade algus     

    long    suf;             // 20 sufiksite massiivi algus    
    long    sufix;           // 19 suf. seot. info algus       
    long    vaba1;           // 18 vaba
    long    vaba2;           // 17 vaba   

    long    pref;            // 16 prefiksite massiivi algus   
    long    prfix;           // 15 pref. seot. info algus      
    long    taandsl;         // 14 taands6naliigid             
    long    tyvelp;          // 13 tyvel6pud  
    long    sonaliik;        // 12 s6naliigid                  

    long    loend[LOENDEID]; // 11 loendid (vt. ini_mrf.h)                   
    } FILE_INFO;

#define FILE_INFO_SIZE (32*sizeof(UB4) + sizeof(SB2))

/// S�nastiku struktuuri kohta k�iva infi lugemiseks/salvestamiseks
//
/// @throw VEAD,
/// CFSFileException,CFSMemoryException,CFSRuntimeException
class cFILEINFO : public METAFILEINFO
    {
    public:
        FILE_INFO file_info;
        cFILEINFO(void)
            {
            InitClassVariables();
            assert(EmptyClassInvariant());
            }

        bool EmptyClassInvariant(void) const
            {
            if( file_info.bt_offset!= 0L||
                file_info.sa_offset!= 0L||
                file_info.tyveL6ppudeAlgus!= 0L||
                file_info.piiriKr6nksud!= 0L||
                //
                file_info.VersionMS!= 0||
                file_info.VersionLS!= 0||
                file_info.buf_size!= 0||
                //
                file_info.tyveKr6nksud!= 0L||
                file_info.ends!= 0L||
                file_info.groups!= 0L||
                file_info.gr!= 0L||
                file_info.forms!= 0L||
                file_info.fgr!= 0L||
                file_info.suf!= 0L||
                file_info.sufix!= 0L||
                file_info.vaba1!= 0L||
                file_info.vaba2!= 0L||
                file_info.pref!= 0L||
                file_info.prfix!= 0L||
                file_info.taandsl!= 0L||
                file_info.tyvelp!= 0L||
                file_info.sonaliik!= 0L)
                return false;
            for(int i=0; i<LOENDEID; i++)
                {
                if(file_info.loend[i]!= 0L)
                    return false;
                }
            return true;
            };

        bool ClassInvariant(void) const
            {
            if( file_info.bt_offset <= 0L ||
                file_info.sa_offset <= 0L ||
                file_info.tyveL6ppudeAlgus <= 0L ||
                file_info.piiriKr6nksud <= 0L ||
                
                //file_info.VersionMS<==0 ||
                //file_info.VersionLS<==0 ||

                file_info.buf_size <= 0 ||

                file_info.tyveKr6nksud <= 0L ||
                file_info.ends <= 0L ||
                file_info.groups <= 0L ||
                file_info.gr <= 0L ||
                file_info.forms <= 0L ||
                file_info.fgr <= 0L ||
                file_info.suf <= 0L ||
                file_info.sufix <= 0L ||
                file_info.vaba1 != 0L ||
                file_info.vaba2 != 0L ||
                file_info.pref <= 0L ||
                file_info.prfix <= 0L ||
                file_info.taandsl <= 0L ||
                file_info.tyvelp <= 0L ||
                file_info.sonaliik <= 0L)
                return false;
            for(int i=0; i<LOENDEID; i++)
                {
                if(file_info.loend[i] <= 0L) //m�ni loend v�ib puududa
                    return false;
                }
            return true;
            };

        /// S�nastiku struktuuri kohta k�iva infi lugemiseks.
        //
        /// @throw VEAD,
        /// CFSFileException,CFSMemoryException,CFSRuntimeException
        void ReadFileInfo(const CFSFileName *pDctName);

        /// S�nastiku struktuuri kohta k�iva infi /salvestamiseks
        //
        /// @throw VEAD,
        /// CFSFileException,CFSMemoryException,CFSRuntimeException
        bool WriteFileInfo(void);
        //bool WriteFileInfo(FILE_INFO &fi);

        void DctVer(
            int *versionMS,
            int *versionLS
            )
            {
            *versionMS=file_info.VersionMS;
            *versionLS=file_info.VersionLS;
            };

        /// S�nastiku struktuuri kohta k�iva infi lugemiseks/salvestamiseks
        //
        /// @return
        /// - @a ==true OK
        /// - @a ==false Jama
        bool c_read( // ==0:ok; ==-1:jama
            const long     offset,
            void     *pBuffer,
            const int len
            );

    private:
        void InitClassVariables(void)
            {
            file_info.bt_offset= 0L;
            file_info.sa_offset= 0L;
            file_info.tyveL6ppudeAlgus= 0L;
            file_info.piiriKr6nksud= 0L;
            //
            file_info.VersionMS= 0;
            file_info.VersionLS= 0;
            file_info.buf_size= 0;
            //
            file_info.tyveKr6nksud= 0L;
            file_info.ends= 0L;
            file_info.groups= 0L;
            file_info.gr= 0L;
            file_info.forms= 0L;
            file_info.fgr= 0L;
            file_info.suf= 0L;
            file_info.sufix= 0L;
            file_info.vaba1= 0L;
            file_info.vaba2= 0L;
            file_info.pref= 0L;
            file_info.prfix= 0L;
            file_info.taandsl= 0L;
            file_info.tyvelp= 0L;
            file_info.sonaliik= 0L;
            for(int i=0; i<LOENDEID; i++)
                file_info.loend[i]= 0L;
            }
    };
#endif
