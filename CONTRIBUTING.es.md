[English](CONTRIBUTING.md) · [Bahasa Indonesia](CONTRIBUTING.id.md) · **Español**

# Contribuir a Making Sense Bali

Una campaña de sensado ambiental liderada por la comunidad en Bali, anclada en
[Fab Lab Bali](https://fablabbali.com). Sensores, reportes de residentes y las
herramientas que los conectan.

No hace falta programar para contribuir, ni pedir permiso para empezar. Abre un *issue* o
un *pull request*.

## Una regla antes que todas: nunca publiques a una persona

Este repositorio maneja reportes de residentes, algunos de los cuales han dicho
abiertamente que tienen miedo de hablar sobre la quema cerca de sus casas. El anonimato
aquí no es un extra: es la razón por la que la gente participa.

Por lo tanto, en cualquier *issue*, *pull request*, captura, log pegado o dato de prueba:

- **Sin números de teléfono, nombres, cuentas de WhatsApp ni IDs de chat.**
- **Sin coordenadas exactas de un reporte.** Los reportes publicados se desplazan
  deliberadamente al centroide de un desa. No lo deshagas, y no pegues coordenadas
  precisas de datos privados en un *issue* público.
- **Sin fotografías originales de los reportes.** Las publicadas tienen el EXIF eliminado;
  las originales permanecen privadas.
- **Sin marcas de tiempo al minuto** en reportes individuales. Una hora precisa en un
  reporte repetido identifica a alguien por su rutina.

Si encuentras algo de lo anterior ya publicado en este repositorio, es un problema de
seguridad, no un *bug*: escribe a tomas@fab.city en lugar de abrir un *issue* público.

## Qué resulta útil

**Hardware.** Diseños de carcasa, variantes del nodo, arreglos de campo. La regla es
*fuente y exportación, siempre*: un `.step` o `.scad` junto al `.stl`, para que el
siguiente laboratorio pueda modificar y no solo imprimir. Las contribuciones solo de
exportación se aceptan, pero se marcan como incompletas. Empieza en
`hardware/diy-node/enclosure/` — el diseño actual es `bayu-v6/`, y `previous-iterations/`
explica qué falló en cada diseño retirado.

**Firmware y herramientas.** `hardware/diy-node/firmware/`, `tools/`, `worker/`. Las notas
de integración con Smart Citizen están en `docs/`. Si añades un canal de sensor, lee
primero las reglas de honestidad de datos: sin ceros falsos, sin NaN, promediar en vez de
muestrear. Una lectura fallida no debe aportar nada, porque en un panel `PM = 0` es
indistinguible del aire limpio.

**Traducciones.** Todo se publica en inglés, bahasa indonesio y español. El inglés es
canónico; los otros dos son traducciones. Las cadenas están en `i18n.js` — añade la clave
a los tres diccionarios o el sitio recurrirá al idioma base en silencio. La calidad del
bahasa importa más: este sitio atiende primero a residentes balineses.

**Conocimiento comunitario.** [`docs/community-knowledge.md`](docs/community-knowledge.md)
está destilado del grupo comunitario [Bali Air Dispatch](https://baliairdispatch.com/). Si
algo allí está equivocado, incompleto o afirmado con más confianza de la que la evidencia
sostiene, corregirlo es una contribución real.

**Replicación.** Si construyes un nodo, o haces un *fork* como *Making Sense [tu ciudad]*,
cuéntanoslo. Lo que tuviste que cambiar para conseguir piezas localmente le sirve más al
siguiente laboratorio que cualquier cosa que podamos escribir desde aquí.

**Reportar.** La contribución de menor esfuerzo y de la que vive la campaña:
[reporta lo que veas](https://bali-aq.fab.city/report). Anónimo, sin cuenta, sin teléfono.

## Cómo enviar

1. Haz *fork* y una rama desde `main`. Nómbrala por lo que hace — `hardware/…`, `docs/…`,
   `fix/…`.
2. Un *pull request* por asunto. Un PR que arregla un *bug* *y* reorganiza una carpeta son
   dos PR.
3. Describe qué cambiaste y, en hardware, contra qué lo probaste. "Impreso y desplegado
   tres semanas en Denpasar" vale más que un render.
4. Puedes escribir en español o bahasa en los *issues* y descripciones de PR. Los
   comentarios en el código, en inglés, para que los lea el mayor número de personas.

No hay CLA. Al contribuir aceptas que tu trabajo se publique bajo las licencias siguientes.

## Licencias

| Qué | Licencia |
|---|---|
| Software — firmware, herramientas, sitio | MIT |
| Hardware — CAD, STL, diseño mecánico | CERN-OHL-W-2.0 |
| Documentación, imágenes, conocimiento comunitario | CC-BY-SA-4.0 |
| Datos de reportes publicados | CC-BY-4.0 |

CERN-OHL-W es débilmente recíproca: un taller puede fabricar y vender nodos
comercialmente, y las mejoras al diseño regresan al proyecto.

## Mapa del repositorio

```
hardware/diy-node/     carcasas (bayu-v6 es la actual), firmware, herramientas
dashboard/             panel de sensores en vivo
docs/                  metodología, conocimiento comunitario, notas de plataforma
reports/               el pipeline de reportes y el panel de moderación
worker/                Cloudflare worker que hace de proxy a OpenAQ
data/                  datos de reportes publicados y moderados — escritos por máquina
i18n.js                todas las cadenas del sitio, en tres idiomas
```

`data/` lo escribe una sincronización automática. No lo edites a mano.

## Contacto

Tomas Diez — tomas@fab.city. Para cualquier cosa que toque la identidad o la seguridad de
una persona, escribe por correo en vez de abrir un *issue*.
