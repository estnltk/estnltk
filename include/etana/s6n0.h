
#if !defined( SON0_H )
#define SON0_H

// 2002.05.27

#include <string.h>

#include "mrflags.h"
#include "tmplptrsrtfnd.h"
#include "tmk2t.h" // sealt AVTIDX ja TYVE_INF

class CTYVE_INF
    {
    private:
        FSxCHAR sonaLiik[2];    // s�naliik
	    int piiriKr6nksud;      // TV 990312
        _int16  lg_nr;
        _int16  lisaKr6nksud;
        AVTIDX idx; 

    public:
        CTYVE_INF(void)
            {
            sonaLiik[1]=0;
            };

        CTYVE_INF(
            const FSxCHAR _sonaLiik_,
            const int _piiriKr6nksud_,
            const int _lg_nr_,
            const int _lisaKr6nksud_,
            const int _tab_idx_,
            const int _blk_idx_)
            {
            sonaLiik[1]=0;
            Start(_sonaLiik_,_piiriKr6nksud_,_lg_nr_,_lisaKr6nksud_,_tab_idx_,_blk_idx_);
            };

        CTYVE_INF(const CTYVE_INF *ctyve_inf)
            {
            sonaLiik[1]=0;
            Start(ctyve_inf);
            };

        void Start(const CTYVE_INF &ti)
            {
            sonaLiik[0]=ti.sonaLiik[0];
            sonaLiik[1]=ti.sonaLiik[1];
            lg_nr=ti.lg_nr;
            lisaKr6nksud=ti.lisaKr6nksud;
            idx=ti.idx; //NB struktuuri omistamine
            };

        void Start(
            const FSxCHAR _sonaLiik_,
            const int _piiriKr6nksud_,
            const int _lg_nr_,
            const int _lisaKr6nksud_,
            const int _tab_idx_,
            const int _blk_idx_)
            {
            PutSonaLiik(_sonaLiik_);
            PutPiiriGrupiNr(_piiriKr6nksud_);
            PutLgNr(_lg_nr_);
            PutKr6nksuGrupiNr(_lisaKr6nksud_);
            PutTyMuutGrupiNr(_tab_idx_);
            PutTyMuutGrupisMitmes(_blk_idx_);
            };

        inline void Start(const CTYVE_INF *ctyve_inf)
            {
            Start(
                ctyve_inf->sonaLiik[0],
                ctyve_inf->piiriKr6nksud,
                ctyve_inf->lg_nr,
                ctyve_inf->lisaKr6nksud,
                ctyve_inf->idx.tab_idx,
                ctyve_inf->idx.blk_idx);
            };
        //----------------------
        inline void PutSonaLiik(
            const FSxCHAR _sonaLiik_) 
            {
            sonaLiik[0]=_sonaLiik_; 
            assert( sonaLiik[1] == 0 );
            };

        inline void PutPiiriGrupiNr(
            const int _piiriKr6nksud_) 
            {
            assert( _piiriKr6nksud_ > 0 );            
            piiriKr6nksud=_piiriKr6nksud_; 
            };

        inline void PutLgNr(
            const int _lg_nr_) 
            {
            assert( (_lg_nr_ & ~0x7FFF)==0 );            
            lg_nr=_lg_nr_; 
            };

        inline void PutKr6nksuGrupiNr(
            const int _lisaKr6nksud_) 
            {
            assert( (_lisaKr6nksud_ & ~0x7FFF)==0 );
            lisaKr6nksud=(_int16)_lisaKr6nksud_; 
            };

        inline void PutTyMuutGrupiNr(
            const int _tab_idx_) 
            { 
            assert( (_tab_idx_ & ~0x7FFF)==0 );
            idx.tab_idx=(_int16)_tab_idx_; 
            };

        inline void PutTyMuutGrupisMitmes(
            const int _blk_idx_)
            { 
            assert( (_blk_idx_ & ~0xFF)==0 );
            idx.blk_idx=(_uint8)_blk_idx_; 
            };
        //----------------------
        inline FSxCHAR *GetSonaLiigiStr(void)
            {
            assert( sonaLiik[1] == 0 );
            return sonaLiik;
            };

        inline FSxCHAR GetSonaLiik(void) const
            {
            return *sonaLiik;
            };

        inline int GetPiiriKr6nksud(void) const
            {
            return piiriKr6nksud;
            };

        inline int GetLgNr(void) const
            {
            return lg_nr;
            };

        inline int GetKr6nksuGrupiNr(void) const
            {
            return lisaKr6nksud;
            };

        inline int GetTabIdx(void) const
            {
            return idx.tab_idx;
            };

        inline int GetBlkIdx(void) const
            {
            return idx.blk_idx;
            };

        AVTIDX *GetAVTIDX(void)
            {
            return &idx;
            };
        //----------------------
    };


#endif
