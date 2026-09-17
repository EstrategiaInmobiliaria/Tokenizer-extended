program SumaCondicional;
var
  a, b, suma: integer;
begin
  writeln('=== SUMA CON CONDICIONAL (Pascal) ===');
  write('Ingresa el primer numero: ');
  readln(a);
  write('Ingresa el segundo numero: ');
  readln(b);
  
  suma := a + b;
  writeln('La suma es: ', suma);
  
  { Condicional: si la suma es mayor a 100 }
  if suma > 100 then
    writeln('ALTO')
  else
    writeln('BAJO');
end.
