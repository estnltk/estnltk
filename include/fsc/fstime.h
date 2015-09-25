/*
Copyright 2015 Filosoft OÜ

This file is part of Estnltk. It is available under the license of GPLv2 found
in the top-level directory of this distribution and
at http://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html .
No part of this file, may be copied, modified, propagated, or distributed
except according to the terms contained in the license.

This software is distributed on an "AS IS" basis, without warranties or conditions
of any kind, either express or implied.
*/
#if !defined _FSTIME_H_
#define _FSTIME_H_

#include "fsutil.h"
#include "fsexception.h"

/**
* Abstract timeclass for time-differences.
*/
class CFSTime{
public:
	CFSTime();

/**
* Creates time class and initializes it with current time.
* @return Current time.
*/
	static CFSTime Now();

/**
* Converts time to seconds.
* @return Time in seconds.
*/
	double GetSeconds() const;

/**
* Adds of subtracts times.
* @param[in] Time Time to add/subtract.
* @return Result of the operation.
*/
	CFSTime operator +(const CFSTime &Time);
	CFSTime& operator +=(const CFSTime &Time);
	CFSTime operator -(const CFSTime &Time);
	CFSTime& operator -=(const CFSTime &Time);

protected:
#if defined (WIN32)
	LONGLONG m_Time;
	LONGLONG m_llFreq;
#elif defined (UNIX)
	timeval m_Time;
#elif defined (MAC)
	ULONGLONG m_Time;
#endif
};

/**
* Measures time from start to stop.
*/
class CFSStopper{
public:
	CFSStopper();
	virtual ~CFSStopper();

/**
* Starts stopper.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int Start();

/**
* Stops stopper.
* @retval 0 OK.
* @retval !=0 Fail.
*/
	int Stop();

/**
* Converts measurement into seconds.
* @return time measured in milliseconds.
*/
	double GetTime() const { 
		return m_Time.GetSeconds(); 
	}

protected:
	bool m_bStarted;
	CFSTime m_Time;
};

/**
* Helper class that starts stopper on creation and stops on destruction.
* @sa CFSStopper
*/
class CFSAutoStopper{
public:
	DECLARE_FSNOCOPY(CFSAutoStopper);

/**
* Initializes class and starts stopper.
* @param[in] pStopper Stopper to be used.
*/
	CFSAutoStopper(CFSStopper *pStopper) {
		m_pStopper=(pStopper->Start()==0 ? pStopper : 0);
	}

/**
* Stops stopper.
*/
	virtual ~CFSAutoStopper() {
		if (m_pStopper) {
			m_pStopper->Stop();
		}
	}

protected:
	CFSStopper *m_pStopper;
};

void FSTimeLimiter(int iYear, int iMonth=1, int iDay=1);

#endif // _FSTIME_H_
