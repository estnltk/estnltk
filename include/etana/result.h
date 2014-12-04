
/*
 Loend mitmesugustest vigadest, mis v�ivad tekkida standardsete 
 alamprogrammide kasutamisel. (C) Tarmo Vaino 1992
 */

#ifndef RESULT_H
#define RESULT_H

    typedef enum
       	{
        ALL_RIGHT       =  0,	//k�ik l�ks korda                           
       	CRASH           =  1,	//totaalselt p�hjak�rbenud                  

       	FILE_NOT_FOUND  =  2,   //ei leidnud sellist faili       (vt errno) 
       	TOO_MENY_FILES  =  3,   //liiga palju selliseid faile               

       	ILL_LINE_LEN    =  4,	//liiga pikk rida lugemiseks                
       	ILL_SYNTAX      =  5,	//s�ntaksi viga                             

       	ILL_ALLOC       =  6,	//eba�nnestunud m�lu reserveerimine         
       	ILL_CREAT       =  7,	//eba�nnestunud faili loomine    (vt errno) 
       	ILL_OPEN        =  8,	//eba�nnestunud faili avamine    (vt errno) 
       	ILL_READ        =  9,	//eba�nnestunud failist lugemine (vt errno) 
       	ILL_WRITE       = 10,	//eba�nnestunud faili kirjutamine          
       	ILL_CLOSE       = 11,   //eba�nnestunud faili sulgemine  (vt errno) 
       	ILL_SEEK        = 12,	//eba�nnestunud lseek            (vt errno) 
       	ILL_FILELENGTH  = 13,   //eba�nnestunud filelength	     (vt errno) 

       	ILL_CURDIR      = 14    //eba�nnestunud jooksva kataloogi m��rtamine 
       	} RESULT;

#endif
