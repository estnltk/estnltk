#include "stdfsc.h"
#include "fstype.h"

#include "fsexception.h"

void FSThrowMemoryException()
{
	throw CFSMemoryException();
}
