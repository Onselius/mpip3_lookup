# mpip3_lookup
En sökbar databas över avsnitt i morgonpasset i p3.

Avsnittet hämtas via sveriges radios öppna API och sparas i en SQLite databas.

Valfritt antal sökord matchas mot den beskrivning som finns för varje avsnitt.


Användning

Anges argumentet "update" vid körning så hämtas datumet på det senast sändna avsnittet och används som startdatum för att se om det kommit några nya avsnitt.

Anges inget argument skriver man in valfritt sökord och trycker på enter. Vill man söka på flera ord så separerar man dessa med mellanslag.
