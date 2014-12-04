#if !defined _FSC_H_
#define _FSC_H_

// FSC main header file

#include "stdfsc.h"
#include "fstype.h"

#include "fscinit.h"
#include "fstrace.h"
#include "fsblockalloc.h"
#include "fsdata.h"
#include "fsdll.h"
#include "fsexception.h"
#include "fsfile.h"
#include "fsfixalloc.h"
#include "fshugeinteger.h"
#include "fslist.h"
#include "fsmemory.h"
#include "fssmartptr.h"
#include "fsstring2.h"
#include "fsthread.h"
#include "fstime.h"
#include "fsutil.h"
#include "fsvar.h"
#include "fswav.h"

#if defined (WIN32) && !defined (WINRT)
	#include "fsreg.h"
#elif defined (UNIX)
#elif defined (MAC)
#endif

#endif // _FSC_H_
