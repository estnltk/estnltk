#include "stdfsc.h"
#include "fstype.h"

#include "fstime.h"

#include <time.h>

CFSTime::CFSTime()
{
#if defined (WIN32)
	m_Time=0;
	m_llFreq=0;
	LARGE_INTEGER llInt;
	QueryPerformanceFrequency(&llInt);
	m_llFreq=llInt.QuadPart;
#elif defined (UNIX)
	m_Time.tv_sec=0;
	m_Time.tv_usec=0;
#elif defined (MAC)
	m_Time=0;
#endif
}

CFSTime CFSTime::Now()
{
	CFSTime Time;
#if defined (WIN32)
	LARGE_INTEGER llInt;
	if (QueryPerformanceCounter(&llInt)==0) {
		return Time;
	}
	Time.m_Time=llInt.QuadPart;
#elif defined (UNIX)
	if (gettimeofday(&Time.m_Time, 0)!=0) {
		return Time;
	}
#elif defined (MAC)
	UnsignedWide MacTime;
	Microseconds(&MacTime);
	Time.m_Time=(ULONGLONG)MacTime.hi<<32 | MacTime.lo;
#endif
	return Time;
}

double CFSTime::GetSeconds() const
{
#if defined (WIN32)
	if (m_llFreq) {
		return (double)m_Time/m_llFreq;
	}
	else {
		return 0;
	}
#elif defined (UNIX)
	return (double)m_Time.tv_sec+(double)m_Time.tv_usec/1000000;
#elif defined (MAC)
	return (double)m_Time/1000000;
#endif
}

CFSTime CFSTime::operator +(const CFSTime &Time)
{
	CFSTime Time2=*this;
	Time2+=Time;
	return Time2;
}

CFSTime& CFSTime::operator +=(const CFSTime &Time)
{
#if defined (WIN32) || defined (MAC)
	m_Time+=Time.m_Time;
#elif defined (UNIX)
	m_Time.tv_sec+=Time.m_Time.tv_sec;
	m_Time.tv_usec+=Time.m_Time.tv_usec;
	if (m_Time.tv_usec>=10000000){ // 10sec
		while (m_Time.tv_usec>=1000000){ // 1sec
			m_Time.tv_sec++;
			m_Time.tv_usec-=1000000;
		}
	}
#endif
	return *this;
}

CFSTime CFSTime::operator -(const CFSTime &Time)
{
	CFSTime Time2=*this;
	Time2-=Time;
	return Time2;
}

CFSTime& CFSTime::operator -=(const CFSTime &Time)
{
#if defined (WIN32) || defined (MAC)
	m_Time-=Time.m_Time;
#elif defined (UNIX)
	m_Time.tv_sec-=Time.m_Time.tv_sec;
	m_Time.tv_usec-=Time.m_Time.tv_usec;
	if (m_Time.tv_usec<=-10000000){ // -10sec
		while (m_Time.tv_usec<=-1000000){ // -1sec
			m_Time.tv_sec--;
			m_Time.tv_usec+=1000000;
		}
	}
#endif
	return *this;
}

CFSStopper::CFSStopper()
{
	m_bStarted=false;
}

CFSStopper::~CFSStopper()
{
}

int CFSStopper::Start(){
	if (m_bStarted) {
		return -1;
	}
	m_Time-=CFSTime::Now();
	m_bStarted=true;
	return 0;
}

int CFSStopper::Stop()
{
	if (!m_bStarted) {
		return -1;
	}
	m_Time+=CFSTime::Now();
	m_bStarted=false;
	return 0;
}

void FSTimeLimiter(int iYear, int iMonth, int iDay)
{
	time_t secs=time(0);
#if defined (WIN32)
	tm now_s;
	localtime_s(&now_s, &secs);
	const tm *now=&now_s;
#else
	tm *now=localtime(&secs);
#endif
	if (now->tm_year+1900 > iYear) throw CFSException();
	if (now->tm_year+1900 == iYear) {
		if (now->tm_mon+1 > iMonth) throw CFSException();
		if (now->tm_mon+1 == iMonth) {
			if (now->tm_mday >= iDay) throw CFSException();
		}
	}
}
