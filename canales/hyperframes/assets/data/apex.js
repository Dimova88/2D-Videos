window.HPD = window.HPD || {};
/* Datos de Fórmula 1. Fuentes y fecha de consulta, en MARCAS.md:
   · récord de parada en boxes: Guinness World Records (McLaren / Lando Norris,
     Lusail, 8 de octubre de 2023): 1,80 s. Anterior: Red Bull 1,82 s (Brasil 2019).
   · velocidad punta en carrera: 372,6 km/h, Juan Pablo Montoya, Monza, 2005.
   · Monza: 5,793 km, 11 curvas. · Mundial 2024: 24 Grandes Premios.
   · margen de victoria más pequeño: 0,010 s (Gethin a Peterson, Monza 1971).
   Nada de esto se ha estimado: si un número no estaba publicado, no entra. */
window.HPD.apex = {
  races2024: 24,
  pitStop: 1.80, pitCrew: 20, wheels: 4,
  pitTeam: "McLaren", pitRace: "Qatar 2023",
  topSpeed: 372.6, topYear: 2005, topDriver: "Montoya",
  circuit: "Monza", lengthKm: 5.793, corners: 11,
  smallestMargin: 0.010, marginYear: 1971,
  avgSpeed: 250.706,
  // trazado esquemático (no es un plano a escala): 11 curvas, recta principal abajo
  layout: [[120, 520], [700, 520], [800, 500], [846, 456], [828, 414], [872, 366],
    [844, 322], [884, 278], [844, 242], [690, 226], [556, 190], [430, 156],
    [332, 166], [302, 214], [268, 248], [230, 236], [196, 262], [206, 306],
    [242, 318], [290, 312], [320, 342], [300, 374], [318, 402], [362, 406],
    [420, 432], [398, 488], [300, 520]],
};
