BEGIN 	  {finv=0;}
/^[A-Z]/  {cap=1;print;next;}
/^[a-z]/  {cap=0;}
/=mine/   {mine=1;}
/=nud/    {nud=1;}
/=tud/    {tud=1;}
/=dud/    {tud=1;}
/=nu[+]/  {nu=1;}
/=tu[+]/  {tu=1;}
/=du[+]/  {tu=1;}
/=v[+]/   {v=1;}
/=tav/    {tav=1;}
/=dav/    {tav=1;}
/=mata/   {mata=1;}
/=ja/     {ja=1;}
/_V_.* ps. /         {finv=1;}
/_V_.* neg /         {finv=1;}
/_V_ aux neg \/\//   {finv=0;}
/_V_.* quot /        {finv=1;}
/_V_.* impf imps/    {finv=1;}
/_V_.* pres imps/    {finv=1;}
/^ [ ]*####/ {print; next;}
/^  / {printf("    "); for (i=1;i<=NF-1;i++ ) printf("%s ",$i);
       if (cap) printf("#cap ");
       if (mine) printf("#mine ");
       if (nud)  printf("partic #nud ");
       if (tud)  printf("partic #tud ");
       if (nu)  printf("#nu ");
       if (tu)  printf("#tu ");
       if (v) printf("partic #v ");
       if (tav) printf("partic #tav ");
       if (mata) printf("partic #mata ");
       if (ja) printf("#ja ");
       if (finv) {printf("#FinV "); finv=0;}
       print "// ";
       mine=nud=tud=nu=tu=v=tav=mata=ja=0;  
     }

/^[^ ]/ {cap=mine=nud=tud=nu=tu=v=tav=mata=ja=0; print;}
