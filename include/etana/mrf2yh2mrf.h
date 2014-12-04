
#if !defined( MRF2YH2MRF_H )
#define MRF2YH2MRF_H

#include <assert.h>
#include "ctulem.h"
#include "tloendid.h"

typedef struct
    {
    const FSWCHAR* p_key;
    const FSWCHAR* p_yhTag;
    } MRF2YH_LOEND;

typedef struct
    {
    const FSWCHAR* p_key;
    const FSWCHAR* p_Tag1;
    const FSWCHAR* p_Tag2;
    } MRF2YH_LOEND2;


/**  Lisab morfanalüüsile ühestaja-mürgendid */
class MRF2YH2MRF
    {
	public:
        /// Argumentideta konstruktor
        //
        /// Reserveerib mälu ja initsialiseerib loendid.
        /// @attention Kõik vajalikud loendid on programmi sissekirjutatud,
        /// nii et sõnastikustpole vaja  midagi lugeda. 
        /// Seega pole vajadust ka argumentidega konstruktori järele.
        /// @throw VEAD,
        /// CFSMemoryException, CFSRuntimeException
		MRF2YH2MRF(void) // void-konstruktor
			{
			InitClassVariables();
			}

        /// Lisab ühestajamärgendid
        //
        /// Tõstab koma sisaldavad anaüüsid lahku 
        /// ja lisab ühestajamärgendid.
        /// @throw VEAD,
        /// CFSMemoryException, CFSRuntimeException
        void FsTags2YmmTags(
            MRFTULEMUSED* p_mTulemused) const;

        void FsTags2YmmTags(
            const FSXSTRING* pS6na,
            MRFTUL* p_mTul,
			FSXSTRING& yhmarg1,
			FSXSTRING& yhmarg2,
			FSXSTRING& yhmarg3	) const;

        bool EmptyClassInvariant(void) const
            {
            return ClassInvariant();    
            }

		bool ClassInvariant(void) const
			{
			// TODO::Argumentidega starditud klassi invariant
            return
                punktuatsioon.ClassInvariant()
                && sona.ClassInvariant()
                && rr.ClassInvariant()
                && yksTeine.ClassInvariant()
                && kaanded.ClassInvariant()
                && poorded.ClassInvariant()
                && ase.ClassInvariant()
                && noomTags.ClassInvariant()
                && asxrr.ClassInvariant()
                && sidec.ClassInvariant()
                && eesJaTaga.ClassInvariant()
                && eesVoiTaga.ClassInvariant()
                && muut1.GetLength()>0
                && verb_v_adj.GetLength()>0
                && yks_v_teine_sonaliik.GetLength()>0
                && sid_variandid.GetLength()>0;
			}

	private:
        LOEND<MRF2YH_LOEND,FSWCHAR*> punktuatsioon;
        LOEND<MRF2YH_LOEND,FSWCHAR*> sona;
        LOEND<MRF2YH_LOEND,FSWCHAR*> rr;
        LOEND<MRF2YH_LOEND,FSWCHAR*> yksTeine;
        LOEND<MRF2YH_LOEND,FSWCHAR*> kaanded;
        LOEND<MRF2YH_LOEND,FSWCHAR*> poorded;
        LOEND<MRF2YH_LOEND,FSWCHAR*> ase;
        LOEND<MRF2YH_LOEND,FSWCHAR*> noomTags;
        LOEND<MRF2YH_LOEND,FSWCHAR*> asxrr;
        LOEND<MRF2YH_LOEND,FSWCHAR*> sidec;
        LOEND<MRF2YH_LOEND2,FSWCHAR*> eesJaTaga;
        LOEND<MRF2YH_LOEND,FSWCHAR*> eesVoiTaga;

        CFSWString muut1;
        CFSWString verb_v_adj;
        CFSWString yks_v_teine_sonaliik;
        CFSWString sid_variandid;

        const FSWCHAR* Kaane( // välja ühestajamärgend
            const FSXSTRING* p_vorm) const;

        const FSWCHAR*  Poore( // välja ühestajamärgend
            const FSXSTRING* p_vorm) const;

        void Kaas2Yh( // välja ühestajamärgend
            const FSXSTRING* p_sona,
            FSXSTRING& p_lisa1,
            FSXSTRING& p_lisa2) const;

        /// Reserveerib mälu ja initsialiseerib loendid.
		void InitClassVariables(void);

		// Need on illegaliseed-{{
		MRF2YH2MRF(const MRF2YH2MRF&){assert(false);} 
		MRF2YH2MRF& operator=(const MRF2YH2MRF&) {assert(false); return *this; }
		// }}-Need on illegaliseed
    };

#endif


