// (c) 1996-97
// 1999.12.21 TV kohendatud vastavask uuendatud X2TABEL klassile

#define STRICT
#include <memory.h>
#include <string.h>
#include <stdlib.h>

#include "tmk2tx.h"    
#include "cxxbs3.h"

// {{ (C)2002

bool MKTAc::Start(const long offSet, CPFSFile *in)
    {
    assert( EmptyClassInvariant() );
    int i;

    in->Seek(offSet);
    if(in->ReadUnsigned<UB4,int>(&n)==false)
        return false;
    mktc=new MKTc[n];
    for(i=0; i < n; i++)
        {
        if(mktc[i].Read(in)==false)
            return false;
        }
    assert( ClassInvariant() );
    return true;
    }

void MKTAc::Stop(void)
    {
    if(mktc)
        delete [] mktc;
    InitClassVariables();
    assert( EmptyClassInvariant() );
    }

int MKTc::Compare(const MKTc *mktc, const int sortOrder)
    {
	FSUNUSED(sortOrder);
    assert( ClassInvariant() );

    int i, cmp;
    if((cmp=n - mktc->n)!=0)
        return cmp;
    for(i=0; i < n; i++)
        {
        if((cmp=mkt1c[i].lgNr - mktc->mkt1c[i].lgNr)!=0)
            return cmp;
        if((cmp=mkt1c[i].tyMuut.Compare(mktc->mkt1c[i].tyMuut))!=0)
            return cmp;
        }
    return 0; // v�rdsed
    }

bool MKTc::Read(CPFSFile *in)
    {
    if(in->ReadUnsigned<UB4,int>(&n)==false)
        {
        return false;
        }
    for(int i=0; i< n; i++)
        {
        if(in->ReadUnsigned<UB4,int>(&(mkt1c[i].lgNr))==false)
            {
            //ASSERT( false );
            return false;
            }
        if(in->ReadString(&(mkt1c[i].tyMuut))==false)
            {
            //ASSERT( false );
            return false;
            }
        if(mkt1c[i].tyMuut.GetLength()==0)
            {
            mkt1c[i].tyMuut=FSxSTR("");
            }
        }
    assert( ClassInvariant() );
    return true;
    }

bool MKTc::Write(CPFSFile *out)
    {
    assert( ClassInvariant() );
    if(out->WriteUnsigned<UB4,int>(n)==false)
        {
        assert( false );
        return false;
        }
    for(int i=0; i < n; i++)
        {
        if(out->WriteUnsigned<UB4,int>(mkt1c[i].lgNr)==false)
            {
            assert( false );
            return false;
            }
        // kirjutada koos '\0'-baidiga
        if(out->WriteStringB(&(mkt1c[i].tyMuut), true)==false)
            {
            assert( false );
            return false;
            }
        }
    return true;
    }

bool MKTc::WriteAsText(CPFSFile *out)
    {
    assert( ClassInvariant() );
    CFSbaseSTRING xStr;
    int i;

    for(i=0; i < n; i++)
        {
        xStr.Format(FSxSTR("%d,%s  "),
            mkt1c[i].lgNr, (const FSxCHAR *)(mkt1c[i].tyMuut));

        if(out->WriteString((const FSxCHAR *)xStr, (int)(xStr.GetLength())-1)==false) // kirjuta ilma '\0'-baidita
            return false;
        }
    out->WriteStringB(FSxSTR("\n"));
    return true;
    }
