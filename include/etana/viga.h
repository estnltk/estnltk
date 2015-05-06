#if !defined( VIGA_H )
#define VIGA_H

#include <errno.h>
#include <string.h>
#include <stdlib.h>
#include <stdio.h>
#if defined( __GNUC__ )
#include <sys/param.h>
#define _MAX_PATH MAXPATHLEN
#endif

#include "post-fsc.h"
#include "etmrfverstr.h"

#if defined(UNICODE)
#define Tmain       wmain
#define Tprintf     wprintf
#define Tfprintf    fwprintf
#define Tfscanf     fwscanf
#define Tsscanf     swscanf
#define Tfopen      _wfopen
#else
#define Tmain       main
#define Tprintf     printf
#define Tfprintf    fprintf
#define Tfscanf     fscanf
#define Tsscanf     swscanf
#define Tfopen      fopen
#endif

/** Mis moodilis viga oli(2baiti). */
enum MISTYKIS
{
    /** pole häda miskit */
    ERR_TYKID_OK,
    /** jama sisendi avamise/lugemisega (failist) */
    ERR_INPUT,
    /** jama väljundi avamise/kirjutamisega (faili) */
    ERR_OUTPUT,
    /** jama sisendi/väljundi avamise/kirjutamisega (faili) */
    ERR_IO,
    /** morfi mootor */
    ERR_MORFI_MOOTOR,
    /** morfi põhisõnastik */
    ERR_MORFI_PS6N,
    /** morfi lisasõnastik */
    ERR_MORFI_LS6N,
    /** ühestaja mootor */
    ERR_HMM_MOOTOR,
    /** ühestaja andmefail */
    ERR_HMM_DATA,
    /** lausestaja mootor */
    ERR_ELA_MOOTOR,
    /** lausestaja andmefail */
    ERR_ELA_DATA,
    /** sünteka mootor */
    ERR_GEN_MOOTOR,
    /** anal/sünt mootori ühisosa (näit LYLI, MORF0) */
    ERR_MG_MOOTOR,
    /** tesaurus */
    ERR_SAURUS,
    /** jumal teab mis koht */
    ERR_X_TYKK,
};

/** Mis häda oli (2baiti) */
enum MISVIGA
{
    /** pole häda miskit */
    ERR_POLE_VIGA,
    /** faili lõpp, aga muidu ok */
    ERR_EOF,
    /** ei leidnud või ei saanud avatud */
    ERR_OPN,
    /** ei saanud loetud/seekitud */
    ERR_RD,
    /** ei saanud kirjutatud */
    ERR_WRITE,
    /** mäda andmefail */
    ERR_ROTTEN,
    /** mäda DLL */
    ERR_ROTTENDLL,
    /** liiga pikk failinimi */
    ERR_2LONGFN,
    /** mälust tuli puudu */
    ERR_NOMEM,
    /** lubamatu (omist, copy-constr) operaator */
    ERR_OPERATOR,
    /** lubamatu meetod/parameeter */
    ERR_ARGS,
    /** sobimatu parameetri väärtus */
    ERR_ARGVAL,
    /** ei suutnud ühestajamärgendit väljaarvutuda */
    ERR_YHMRG,
    /** puudulikult initsialiseeritud klass */
    ERR_INIT,
    /** lubamatu NULL-viit argumendina */
    ERR_NULLPTR,
    /** mistahes muu jama */
    ERR_MINGIJAMA,
};

/** Klass vea kohta käiva info käitlemiseks */
class VEAD
{
public:

    enum
    {
        MSGBUFSIZE = 1024
    };

    /** Veakood, ei soovita seda otse kasutada */
    int errNo;
    /** Rea number, kus jama tekkis */
    int line;
    /** Faili nimi, kus jama tekkis */
    const char* file;
    /** Faili versioon */
    const char* versioon;
    /** Veateade (globaalse skoobiga) */
    const char* msg;
    /** <ul><li> @a ==true 8bitine msgBuf <li> @a ==false wcharidest msgBuf  </ul> */
    bool charMsgBuf;

    /** Lokaalse skoobiga veateade */
    union TMSGBUFF
    {
        /** Lokaalse skoobiga teade koosneb 8bitistest */
        char a[MSGBUFSIZE + 4];
        /** Lokaalse skoobiga teade koonseb wchar'idest */
        FSWCHAR w[MSGBUFSIZE + 4];
    } msgBuf;

    VEAD(void)
    {
        InitEmtyClassVariables();
    }

    VEAD(const VEAD& viga)
    {
        InitEmtyClassVariables();
        operator=(viga);
    }

    /** Veateade throw'ga edastamiseks
     * 
     * @param[in] misMoodul Mis moodulis jama tekkis (enum MISVIGA)
     * @param[in] misViga Mis jama tekkis (enum MISVIGA)
     * @param[in] _file_ Lähtekoodi fail (makro __FILE__)
     * @param[in] _line_ Lähtekoodi rida (makro __LINE__)
     * @param[in] _versioon_ Viit globaalse skoobiga veateate stringile 
     * @param[in] _msg_ Kopeeritakse lokaalsesse puhvrisse (piiratud pikkusega)
     */
    VEAD(const MISTYKIS misMoodul, const MISVIGA misViga, const char* _file_,
        const int _line_, const char* _versioon_ = NULL,
        const char* _msg_ = NULL)
    {
        InitEmtyClassVariables();
        Viga(misMoodul, misViga, _file_, _line_, _versioon_, _msg_, (char*) NULL);
    }

    VEAD(const MISTYKIS misMoodul, const MISVIGA misViga, const char* _file_,
            const int _line_, const char* _versioon_, const char* _msg_,
            const char* _msgbuf_)
    {
        InitEmtyClassVariables();
        Viga(misMoodul, misViga, _file_, _line_, _versioon_, _msg_, _msgbuf_);
    }

    VEAD(const MISTYKIS misMoodul, const MISVIGA misViga, const char* _file_,
            const int _line_, const char* _versioon_, const char* _msg_,
            const FSWCHAR* _msgbuf_)
    {
        InitEmtyClassVariables();
        Viga(misMoodul, misViga, _file_, _line_, _versioon_, _msg_, _msgbuf_);
    }
    
    /**  Veateade throw'ga edastamiseks
     * 
     * Tulevikus jääb alles ainult selliste parameetritega variant. 
     * @param _file_ -- Lähtekoodi fail (makro __FILE__)
     * @param _line_ -- Lähtekoodi rida (makro __LINE__)
     * @param _constTxt_ -- veateade, globaalse slooboga string
     * @param _nonConstTxt1_ -- veateade, kopeeritakse lokaalsesse puhvrisse
     * @param _nonConstTxt2_ -- veateade, kopeeritakse lokaalsesse puhvrisse
     */
    VEAD(const char* _file_, const int _line_, const char* _constTxt_, 
            const char* _nonConstTxt1_=NULL, const char* _nonConstTxt2_=NULL)
    {
        InitEmtyClassVariables();
        Viga(_file_, _line_, _constTxt_, _nonConstTxt1_, _nonConstTxt2_);
    }    

    VEAD & operator=(const VEAD& viga)
    {
        if (&viga != this)
        {
            errNo = viga.errNo;
            line = viga.line;
            file = viga.file;
            versioon = viga.versioon;
            msg = viga.msg;
            if ((charMsgBuf = viga.charMsgBuf) == true)
                FSStrCpy(msgBuf.a, MSGBUFSIZE + 4, viga.msgBuf.a);
            else
                FSStrCpy(msgBuf.w, MSGBUFSIZE + 4, viga.msgBuf.w);
        }
        return *this;
    }

    /**  Veateade throw'ga edastamiseks
     * 
     * Tulevikus jääb alles ainult selliste parameetritega variant. 
     * @param _file_ -- Lähtekoodi fail (makro __FILE__)
     * @param _line_ -- Lähtekoodi rida (makro __LINE__)
     * @param _constTxt_ -- veateade, globaalse slooboga string
     * @param _nonConstTxt1_ -- veateade, kopeeritakse lokaalsesse puhvrisse
     * @param _nonConstTxt2_ -- veateade, kopeeritakse lokaalsesse puhvrisse
     */
    int Viga(const char* _file_, const int _line_, const char* _constTxt_, 
                        const char* _nonConstTxt1_, const char* _nonConstTxt2_)
    {
        errNo = (int) ERR_X_TYKK | ((int) ERR_MINGIJAMA) << 16;
        line = _line_;
        file = _file_;
        versioon = etMrfVersionString;
        msg = _constTxt_;
        
        charMsgBuf = true;
        msgBuf.a[0] = '\0';

        CFSAString msgTmp;
        if(_nonConstTxt1_!=NULL)
            msgTmp += _nonConstTxt1_;
        if(_nonConstTxt2_!=NULL)
        {
            if(msgTmp.GetLength() > 0)
                msgTmp += " : ";
            msgTmp += _nonConstTxt2_;
        }
        int msgTmpLen = (int) msgTmp.GetLength();
        if (msgTmpLen > MSGBUFSIZE)
        {
            memmove(msgBuf.a, (const char*)msgTmp, MSGBUFSIZE * sizeof (char));
            FSStrCpy(msgBuf.a + MSGBUFSIZE, 4, "...");
        }
        else
            FSStrCpy(msgBuf.a, MSGBUFSIZE + 4, (const char*)msgTmp);
        return errNo;         
    }
    
    
    /**
     *
     * @param[in] misMoodul
     * @param[in] misViga
     * @param[in] _file_
     * @param[in] _line_
     * @param[in] _versioon_
     * @param[in] _msg_
     * @param[in] _msgbuf_
     * @return
     */
    int Viga(const MISTYKIS misMoodul, const MISVIGA misViga, const char* _file_,
             const int _line_, const char* _versioon_, const char* _msg_,
             const char* _msgbuf_)
    {
        errNo = (int) misMoodul | ((int) misViga) << 16;
        line = _line_;
        file = _file_;
        versioon = _versioon_;
        msg = _msg_;
        charMsgBuf = true;
        if (_msgbuf_ == NULL)
            msgBuf.a[0] = '\0';
        else
        {
            int msgLen = (int) FSStrLen(_msgbuf_);
            if (msgLen > MSGBUFSIZE)
            {
                memmove(msgBuf.a, _msgbuf_, MSGBUFSIZE * sizeof (char));
                FSStrCpy(msgBuf.a + MSGBUFSIZE, 4, "...");
            }
            else
                FSStrCpy(msgBuf.a, MSGBUFSIZE + 4, _msgbuf_);
        }
        return errNo;
    }

    /**
     *
     * @param[in] misMoodul
     * @param[in] misViga
     * @param[in] _file_
     * @param[in] _line_
     * @param[in] _versioon_
     * @param[in] _msg_
     * @param[in] _msgbuf_
     * @return
     */
    int Viga(const MISTYKIS misMoodul, const MISVIGA misViga, const char* _file_,
             const int _line_, const char* _versioon_, const char* _msg_,
             const FSWCHAR* _msgbuf_)
    {
        errNo = (int) misMoodul | ((int) misViga) << 16;
        line = _line_;
        file = _file_;
        versioon = _versioon_;
        msg = _msg_;
        charMsgBuf = false;
        if (_msgbuf_ == NULL)
            msgBuf.w[0] = FSWCHAR('\0');
        else
        {
            int msgLen = (int) FSStrLen(_msgbuf_);
            if (msgLen > MSGBUFSIZE)
            {
                memmove(msgBuf.w, _msgbuf_, MSGBUFSIZE * sizeof (FSWCHAR));
                FSStrCpy(msgBuf.w + MSGBUFSIZE, 4, FSWSTR("..."));
            }
            else
                FSStrCpy(msgBuf.w, MSGBUFSIZE + 4, _msgbuf_);
        }
        return errNo;
    }

    void Print(void) const
    {
        if (errNo != 0)
        {
            fprintf(stderr, "%s:%d [%x] ", file, line, errNo);
        }
        if (versioon)
            fprintf(stderr, "(%s)\n", versioon);
        if (msg != NULL)
            fprintf(stderr, "%s", msg);
        if (charMsgBuf == true)
        {
            if (msg != NULL && msgBuf.a[0] != '\0')
                fprintf(stderr, " : ");
            if (msgBuf.a[0] != '\0')
                fprintf(stderr, "%s", msgBuf.a);
        }
        else
        {
            if (msg != NULL && msgBuf.w[0] != FSWCHAR('\0'))
                fprintf(stderr, " : ");
            if(msgBuf.w[0] != FSWCHAR('\0'))
                fprintf(stderr, "%s", 
                        (const char*)FSStrWtoA(msgBuf.w, FSCP_UTF8));
        }
        fprintf(stderr, "\n");
    }

    CFSAString Teade(void) const
    {
        extern const char *etMrfVersionString;
        CFSAString teade;
        teade.Format("%s:%s:%d - ", etMrfVersionString, file, line);
        if (msg != NULL)
            teade += msg;
        if (charMsgBuf == true)
        {
            if (msg != NULL && msgBuf.a[0] != '\0')
                teade += " : ";
            teade += msgBuf.a;
        }
        else
        {
            if (msg != NULL && msgBuf.w[0] != FSWCHAR('\0'))
                teade += " : ";
            teade += FSStrWtoA(msgBuf.w, FSCP_UTF8);
        }
        return teade;
    }    
    
    void Clear(void)
    {
        InitEmtyClassVariables();
    }
private:

    void InitEmtyClassVariables(void)
    {
        errNo = 0;
        line = -1;
        file = NULL;
        versioon = NULL;
        msg = NULL;
        charMsgBuf = true;
        msgBuf.a[0] = '\0';
    }
};

/** @brief Lisab main funktsioonile veakäsitluse
 *
 * @param int @argc
 * Vastav parameeter @a main funktsioonist.
 * @param FSTCHAR ** @argv
 * Vastav parameeter @a main funktsioonist.
 * @param FSTCHAR ** @envp
 * Vastav parameeter @a main funktsioonist.
 * @param const FSTCHAR * @ext
 * Väljundfaili laiend vaikimisi (asendab sisendfaili nimes viimasele
 * punktile järgneva osa. Kui sisendfaili nimi ilma punktita, kleebime otsa.
 * @return
 * @a main funktsiooni poolt tagastatav väärtus (@a EXIT_SUCCESS või @a EXIT_FAILURE)
 */
template <class MAIN>
int MainTemplate(int argc, FSTCHAR ** argv, FSTCHAR ** envp, const FSTCHAR * ext)
{
    try
    {
        //MAIN m(argc, argv, envp, ext);
        FSCInit();
        MAIN m;
        m.Start(argc, argv, envp, ext);
        m.Run();
        FSCTerminate();
        return EXIT_SUCCESS;
    }
    catch (VEAD& viga)
    {
        viga.Print();
        FSCTerminate();
        return EXIT_FAILURE;
    }
    catch (CFSFileException& isCFSFileException)
    {
        fprintf(stderr, "FSC [%x]\nFSC : S/V viga\n", isCFSFileException.m_nError);
        FSCTerminate();
        return EXIT_FAILURE;
    }
    catch (CFSMemoryException&)
    {
        fprintf(stderr, "FSC\nLiiga vähe vaba mälu\n");
        FSCTerminate();
        return EXIT_FAILURE;
    }
    catch (CFSRuntimeException&)
    {
        fprintf(stderr, "FSC\nJooksis kokku\n");
        FSCTerminate();
        return EXIT_FAILURE;
    }
    catch (...)
    {
        fprintf(stderr, "Tundmatu throw()\n");
        FSCTerminate();
        return EXIT_FAILURE;
    }
}
#endif


