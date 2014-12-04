
// (C) 2002, suvi

#if !defined(TMK2TX_H)
#define TMK2TX_H

#include "tyybid.h"
#include "mrflags.h"
#include "post-fsc.h"

#define MAX_TYVEDE_ARV  100 // endiselt oluline
#define TYVE_MAX_PIKKUS 40  // pole enam oluline
/* mingi ürgne pärandvara; ei kasutata enam
typedef struct
{
    int n;

    struct
    {
        char tyvi[TYVE_MAX_PIKKUS];
        int lgNr;
    } t[MAX_TYVEDE_ARV];
} TYVED;

typedef struct
{
    _int16 n;

    struct
    {
        _int16 lgNr;
        char *tyMuut;
    } mkt[MAX_TYVEDE_ARV];
} MKT;
*/
// {{ 2002 UC kompatiibel versioon

class MKT1c
{
public:
    int lgNr;
    CFSbaseSTRING tyMuut;

    void Start(const MKT1c &mkt1c)
    {
        lgNr = mkt1c.lgNr;
        tyMuut = mkt1c.tyMuut;
    };
};

class MKTc
{
public:
    int n;
    MKT1c mkt1c[MAX_TYVEDE_ARV];

    MKTc(void) : n(0)
    {
    }

    MKTc(MKTc &mktc)
    {
        int i;
        n = mktc.n;
        for (i = 0; i < n; i++)
        {
            mkt1c[i].lgNr = mktc.mkt1c[i].lgNr;
            mkt1c[i].tyMuut = mktc.mkt1c[i].tyMuut;
        }
    }

    void Start(const MKTc &mktc)
    {
        n = mktc.n;
        int i;
        for (i = 0; i < n; i++)
        {
            mkt1c[i].Start(mktc.mkt1c[i]);
        }
    }
    int Compare(const MKTc *mktc, const int sortorder = 0);
    bool Read(CPFSFile *in);
    bool Write(CPFSFile *out);
    bool WriteAsText(CPFSFile *out);

    bool EmptyClassInvariant(void) const
    {
        return n == 0;
    };

    bool ClassInvariant(void) const
    {
        return n >= 0;
    };
};

class MKTAc
{
public:
    int n;
    MKTc *mktc;

    MKTAc(void)
    {
        InitClassVariables();
        assert(EmptyClassInvariant());
    };

    MKTc* operator[] (const int idx) const
    {
        assert(ClassInvariant());
        assert(idx >= 0 && idx < n);     
        return ( idx >= 0 && idx < n) ? mktc + idx : NULL;
    };

    MKT1c *Get(const int grupp, const int grupis)
    {
        assert(ClassInvariant());
        assert(grupp >= 0 && grupp < n);
        assert(grupis >= 0 && grupis < mktc[grupp].n);

        return &(mktc[grupp].mkt1c[grupis]);
    }

    bool Start(const long offSet, CPFSFile *in);

    void Stop(void);

    ~MKTAc(void)
    {
        Stop();
    };

    bool EmptyClassInvariant(void) const
    {
        return n == 0 && mktc==NULL;
    };

    bool ClassInvariant(void) const
    {
        return n >= 0 && mktc != NULL;
    };

private:
    void InitClassVariables(void)
    {
        n = 0;
        mktc = NULL;
    }
};

// }} 2002 UC kompatiibel versioon



#endif


