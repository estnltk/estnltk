#include <stdlib.h>
#include <stdio.h>
#include <string.h>

struct nlist {       /* table entry */
  struct nlist *next;   /* next entry in chain */
  char *name;           /* defined name */
  char *defn;           /* replacement text */
};

struct chain
{
  char *text;
  struct chain *next;
};

struct def {
  struct def *next;
  char *condition;
  struct  chain *addition;
};

#define HASHSIZE 2003
#define MAXLEN 256


static struct nlist *hashtab[HASHSIZE]; /* pointer table */

/* hash:  form hash value for string s */
unsigned hash(char *s)
{
  unsigned hashval;

  for (hashval = 0; *s != '\0'; s++)
  hashval = *s + 37 * hashval;
  return hashval % HASHSIZE;
}

/* lookup:  look for s in hashtab */
struct nlist *lookup(char *s)
{
  struct nlist *np;

  for (np = hashtab[hash(s)]; np != NULL; np = np->next)
    if (strcmp(s, np->name) == 0) return np;  /* found */
    return NULL;        /* not found */
}

/* install:  put (name, defn) to hashtab */
struct nlist *install(char *name, char *defn)
{
  struct nlist *np;
  unsigned hashval;

  np = (struct nlist *) malloc(sizeof(*np));
  if (np == NULL || (np->name = strdup(name)) == NULL) return NULL;
  hashval = hash(name);
  np->next = hashtab[hashval];
  hashtab[hashval] = np;
  if ((np->defn = strdup(defn)) == NULL) return NULL;
  return np;
}

/* undef:  free memory allocated by h-table */
void undef(void)
{
  struct nlist *np, *q;
  int i;

  for (i = 0; i < HASHSIZE; i++)
    for (np = hashtab[i]; np != NULL; np = q) {
      q = np->next;
      free(np->name);
      free(np->defn);
      free(np);
    }
  //fprintf(stderr,"Lõpp\n");
}

/* usage:  display user information */
void usage(void)
{
  fprintf(stderr,"\nKasutus:  tagger <lexicon> <input> <output>\n");
  exit(1);
}

/* terminate:  end after error */
void terminate(void)
{
  undef();
  exit(1);
}

void norm(char *s)
{
  char *a;
  int l,i;

  for(a=s;*a==' ';a++);
  if (a!=s) memmove(s,a,a-s);
  l=strlen(s);
  for(i=l;s[i]==' ';i--) s[i]='\0';
}
/* file2hash:  load data from file to the hash table */
void file2hash(char *filename)
{
  FILE *lexicon;
  char name[MAXLEN], defn[MAXLEN];
  int n;

  if ((lexicon = fopen(filename, "rt")) == NULL) {
    fprintf(stderr,"Ei leidnud faili.\n");
    exit(1);
  }
  n = 0;
  while (fgets(name, MAXLEN, lexicon) != NULL) {
    name[strlen(name)-1] = '\0';
    fgets(defn, MAXLEN, lexicon);
    defn[strlen(defn)-1] = '\0';
    if (install(name, defn) == NULL) {
      fprintf(stderr,"Mälu otsas (%d sõna loetud)\n", n);
      fclose(lexicon);
      terminate();
    }
    n++;
  }
  fclose(lexicon);
  //fprintf(stderr,"Sõnu loetud:  %d\n", n);
}

/* copy:  copy one word from source to dest */
void copy(char dest[], char source[])
{
  int i;

  for (i = 0; source[i] != '\0' && source[i] != '+' && source[i] != ' '; i++)
    dest[i] = source[i];
  dest[i] = '\0';
}

/* copy:  copy one word from source to dest */
void copy_name(char dest[], char source[])
{
  int i, j=0;
  for (i = 0; source[i] == '\t' || source[i] == ' ' || source[i] == '"'; )  i++;
  for (; source[i] != '\0' && source[i] != '"'; i++)
    dest[j++] = source[i];
  if (strstr(source, "ma\" V "))
    dest[j-2] = '\0';
  else
    dest[j] = '\0';
}

/* find_next:  return pointer to next word begin in *s */
char *find_next(char *s)
{
  for (; s[0] == ' ' || s[0] == '/'; s++) ;
  if (strlen(s) == 0) return NULL;
  return s;
}

struct def *find_structure(char *string)
{
  char *nool, *toru, *konj, *s;
  char *buff[50];
  struct def *df, *p, *q;
  struct chain *t, *r;

  s=string;
  if ((df = (struct def *) malloc(sizeof(*df)))==NULL) return NULL;

  p=df;
  q=NULL;

  df->next=NULL;

  do
  {
    nool=strchr(s,'*');
    if (nool==NULL)
    {
      fprintf(stderr,"Syntax error in lexicon: %s\n",string);
      return NULL;
    }
    *nool='\0';
    if ((p->condition=strdup(s))==NULL) return NULL;
    norm(p->condition);
    *nool='*';
    s=nool+1;
    r=NULL;
    toru=strchr(s,'|');
    konj=strchr(s,'&');

    if ((t = (struct chain *) malloc(sizeof(*t)))==NULL) return NULL;
    p->addition=t;

    while(toru!=NULL)
    {
      if (konj!=NULL && konj<toru) {toru=NULL; break;}
      *toru='\0';
      if ((t->text=strdup(s))==NULL) return NULL;
      norm(t->text);
      t->next=NULL;
      if (r==NULL) r=p->addition; else {r->next=t;r=t;}
      *toru='|';
      s=toru+1;
      toru=strchr(s,'|');
      if ((t = (struct chain *) malloc(sizeof(*t)))==NULL) return NULL;
    }
    if (toru==NULL)
    {
       if (konj!=NULL)
       {
	 *konj='\0';
	 if ((t->text=strdup(s))==NULL) return NULL;
	 norm(t->text);
	 t->next=NULL;
	 if (r==NULL) r=t; else {r->next=t;r=t;}
	 *konj='&';
       }
       else
       {
	 if ((t->text=strdup(s))==NULL) return NULL;
	 norm(t->text);
	 t->next=NULL;
	 if (r==NULL) r=t; else {r->next=t; r=t;}
       }
     }
     if (q==NULL) q=df;
     else {q->next=p; q=p;}
     p->next=NULL;
     if (konj)
     {
       s=konj+1;
       if ((p = (struct def *) malloc(sizeof(*df)))==NULL) return NULL;
       p->next=NULL;

     }

  }
  while(konj!=NULL);
/*     printf("%s :\n",string);
     for (q=df;q!=NULL;q=q->next)
     {
       printf("%s ",q->condition);
       for (t=q->addition;t!=NULL;t=t->next) printf("%s ",t->text);
       printf("\n");
     }
*/
  return df;
}

char control(char *where, char *whatw)
{
  char what[MAXLEN];
  char *b;
  int n;

  b=where;
  strcpy(what, whatw);
  n=strlen(what);
  what[n]=' ';
  what[n+1]='\0';

  while(b)
  {
      b=strstr(b,what);
      if (b==NULL) return 0;
      { if (*(b-1)==' ' || b==where) return 1;
       else b=b+1;
      }
  }
  return 0;
}

char satisfied(char *cond, char *word)
{
  char *sp,*t;

  t=cond;
  sp=strchr(cond,' ');
  while (sp)
  {
    *sp='\0';
    if (!control(word,t)) {*sp=' '; return 0;}
    *sp=' ';
    for(t=sp+1;*t==' ';t++);
    sp=strchr(t,' ');
  }
  if (sp==NULL)
  {
    if (*t=='\0') return 1;
    if (control(word,t)) return 1;
  }
  return 0;
}

/* work:  main procedure */
void work(char *fn1, char *fn2)
{
  FILE *input, *output;
  char line[MAXLEN], name[MAXLEN], *ptr_plus, *ptr_slash, *bookmark;
  char head[MAXLEN], body[MAXLEN], tale[MAXLEN], word[MAXLEN];
  struct nlist *np;
  struct def *defp,*r;
  struct chain *p;
  int count;
  char ok;

  //fprintf(stderr,"Sisend:  %s\n", fn1);
  if (strcmp(fn1,"stdin")==0) {
     input=stdin;
  } else {
  if ((input = fopen(fn1, "rt")) == NULL) {
    fprintf(stderr,"Sisendfaili ei õnnestunud avada\n");
    terminate();
  }
  }
  //fprintf(stderr,"Väljund:  %s\n", fn2);
  if (strcmp(fn2,"stdout")==0) {
     output=stdout;
  } else {
    if ((output = fopen(fn2, "wt")) == NULL) {
    fprintf(stderr,"Väljundfaili ei õnnestunud avada\n");
    fclose(input);
    terminate();
    }
  }
  while (fgets(line, MAXLEN, input) != NULL) {
    ok=0;
    if (line[strlen(line) - 1] == '\n') 
    {
      line[strlen(line) - 1] = ' ';
      line[strlen(line)] = '\0';
    }
    if (*line == ' ' || *line == '\t') // && (ptr_plus = strchr(line, '+'))!=NULL)
    {
      //bookmark = find_next(line);           /*leiab sona kuni esimese slashini */
      //copy(name, bookmark);                 /*kopeerib kuni plussini */
      copy_name(name, line);                 /*kopeerib algvormi, verb ilma -ma */
      np = lookup(name);                    /*otsib tabelist */
      if (np != NULL)
      {                                     /*kui leidis */
	//ptr_slash = strchr(line, '/');
	ptr_slash = strstr(line, "\" ");
	strncpy(head, line, ptr_slash - line + 1); // + 2); /*head=sona+lopp slashid*/
	head[ptr_slash - line + 1] = '\0'; // + 2
	//bookmark = find_next(ptr_slash);
	//ptr_slash = strchr(bookmark, '/');
	//if (ptr_slash==NULL)
	//{
	//  ptr_slash=line+strlen(line)-1;
	//  printf("Syntax error in input: %s\n", line);
	//}
	//count = ptr_slash - bookmark;
	//strncpy(body, bookmark, count);            /*body=slashide vahel */
	strcpy(body, ptr_slash + 1);            /*body=kuni lõpuni */
	//body[count] = '\0';
	//strcpy(tale, ptr_slash);                   /*tale=viimased slashid...*/
        tale[0]='\0';

	defp=find_structure(np->defn);
	r=defp;
	while(r)
	{
	  strcpy(word,body);
	  if (satisfied(r->condition,word))
	  {
	    p=r->addition;
	    while(p!=NULL)
	    {
	      if (!control(word,p->text))  /*NB! sp->addition on märgendite komb */
	      {
		strcat(word, p->text);
		if (word[strlen(word)-1]!=' ') strcat(word, " ");
		fputs(head, output);
		fputs(word, output);
		fputs(tale, output);
		fputs("\n", output);
		strcpy(word,body);
		ok=1;
	      }
	      p=p->next;
	    }
	  }
	  r=r->next;
	}
      }/*if leidus tabelis */
    }/*if oli tolgendus */
    if (ok==0)
    {
      fputs(line, output);
      fputs("\n", output);
    }
  }/*kuni on ridu */

if (input!= stdin) {fclose(input);}
if (output!= stdout) {fclose(output);}
/*  if (strcmp(fn1,"stdin")!=0) { fclose(input);}
  if (strcmp(fn2,"stdout")!=0) { fclose(output);}*/
}

/* main program */
int main(int argc, char *argv[])
{
int i;

if (argc != 4)usage();
if (strcmp(argv[1], argv[2]) == 0) usage();
if (strcmp(argv[1], argv[3]) == 0) usage();
if (strcmp(argv[2], argv[3]) == 0) usage();
//fprintf(stderr,"Leksikon:  %s\n", argv[1]);
for (i = 0; i < HASHSIZE; i++) hashtab[i] = NULL;
file2hash(argv[1]);
work(argv[2], argv[3]);
undef();
return 0;
}
