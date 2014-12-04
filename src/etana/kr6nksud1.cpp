
// 2000.07.14 TV puuduv initsialiseerimine lisatud
//

#include "cxxbs3.h"

bool LISAKR6NKSUD1::Start(cFILEINFO *cfi)
    {
    int suurus;
    int i;
    cfi->dctFile.Seek(cfi->file_info.piiriKr6nksud); // liigume �igele kohale
    if(cfi->dctFile.ReadUnsigned<UB4,int>(&suurus)==false)
        {
        assert( false );
        return false;        
        }
    liitPiirid.Start(suurus, 0);
    for(i=0;i < suurus; i++)
        {
        CFSbaseSTRING *xstr;
        if((xstr=liitPiirid.AddPlaceHolder())==NULL)
            return false;
        if(cfi->dctFile.ReadString(xstr)==false)
            {
            liitPiirid.Del();
            return false;        
            }
        }
    cfi->dctFile.Seek(cfi->file_info.tyveKr6nksud); // liigume �igele kohale
    if(cfi->dctFile.ReadUnsigned<UB4,int>(&suurus)==false)
        {
        assert( false );
        return false;        
        }
    if(suurus==0)
        {
        nKr6nksuBaiti=0; // t�hi pole midagi
        }
    else if(suurus & ~0xff)
        {
        nKr6nksuBaiti=2; // 2 baiti
        }
    else
        {
        nKr6nksuBaiti=1; // 1 baiti, no rohkem ikka ei ole!
        }    
    muudKr6nksud.Start((int)suurus, 0);
    for(i=0;i < suurus; i++)
        {
        CFSbaseSTRING *xstr;
        if((xstr=muudKr6nksud.AddPlaceHolder())==NULL)
            return false;
        if(cfi->dctFile.ReadString(xstr)==false)
            {
            muudKr6nksud.Del();
            return false;
            }
        }
    //cfi->dctFile.Close();
    return true;
    }

// public
int LISAKR6NKSUD1::LisaKdptr(   // 0==ok; -1==vigane kr�nksuklassi nr
    const TYVE_INF *dptr,
    FSXSTRING *xstrOut,             // v�ljundstring (sisendstring+kr�nksud)
    const FSXSTRING *xstrIn,        // sisendstring
    const int mitmes_ptr_is) 
    {
    int idxp= -1, idxk= -1, i, n, posPiir, posPala;

    CFSbaseSTRING *piir=NULL, *pala=NULL; // vaikimisi pole liits�napiiri ja kr�nkse
    if(mrfFlags.Chk(MF_POOLITA) && (idxp=dptr[mitmes_ptr_is].piiriKr6nksud-1) >= 0)
        {
        if((piir=liitPiirid[idxp])==NULL)
            {
            assert( false );
            idxp= -1;
            }
        }
    if(mrfFlags.Chk(MF_KR6NKSA) && (idxk=GetKr6nksuGrupiNr(dptr, mitmes_ptr_is)-1) >= 0)
        {
        if((pala=muudKr6nksud[idxk])==NULL)
            {
            assert( false );
            idxk= -1;
            }
        }
    n=xstrIn->GetLength();
    posPiir=posPala=0;
    *xstrOut = FSxSTR("");
    for(i=0; i<=n; i++)
        {
        if(idxp>=0 && i+1==(int)((*piir)[posPiir]))
            {
            posPiir++;
            *xstrOut += (*piir)[posPiir];
            posPiir++;
            }
        while(idxk>=0 && i+1==(int)((*pala)[posPala]))
            {
            posPala++;
            *xstrOut += (*pala)[posPala];
            posPala++;
            }
        *xstrOut += (*xstrIn)[i];
        }
    return 0;
    }

