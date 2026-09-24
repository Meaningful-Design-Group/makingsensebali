[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Node V3.2 — carcasa canónica actual

*El **DIY Environmental Sensor Node V3.2** de Fab Lab Bali. Esta carpeta se llamaba `bayu-v7`
hasta septiembre de 2026 — ver [Nomenclatura](#nomenclatura-lea-esto-antes-de-buscar-en-el-repo).*

Carcasa de exterior impresa en 3D para el nodo DIY de calidad del aire de Making Sense Bali.
*Bayu* — viento. Toda la generación V3 es un argumento sobre el flujo de aire, y la v7 es la
iteración que deja de usar tornillos.

**Etapa:** imprimible, lista para campo a la espera de la co-ubicación. Todavía no está lista para replicación — no hay fuente CAD.
**Reemplaza a:** [`../node-v3.1/`](../node-v3.1/) (= Node V3.1) y todo lo que hay en [`../previous-iterations/`](../previous-iterations/)
**Licencia:** CERN-OHL-W-2.0 (hardware) · CC-BY-SA-4.0 (esta documentación)
**Fuente:** *Dokumentasi Teknis: DIY Environmental Sensor Node V3*, Fab Lab Bali, septiembre de 2026. Traducido del indonesio.

![Vista despiezada del ensamble del Node V3.2](img/01-exploded-v32.png)

## Contenido

- [Nomenclatura](#nomenclatura-lea-esto-antes-de-buscar-en-el-repo)
- [Qué cambió respecto a v6](#qué-cambió-respecto-a-v6--node-v31)
- [Qué corrige y qué no corrige este diseño](#qué-corrige-y-qué-no-corrige-este-diseño)
- [Arquitectura híbrida](#arquitectura-híbrida--qué-se-puede-sustituir)
- [Flujo de aire](#flujo-de-aire)
- [Piezas impresas](#piezas-impresas)
- [Ajustes de impresión](#ajustes-de-impresión)
- [Lista de materiales](#lista-de-materiales)
- [Cableado](#cableado)
- [Ensamblaje](#ensamblaje)
- [Montaje](#montaje)
- [Firmware y flujo de datos](#firmware-y-flujo-de-datos)
- [Problemas conocidos en estos archivos](#problemas-conocidos-en-estos-archivos)
- [Lo que todavía falta en esta documentación](#lo-que-todavía-falta-en-esta-documentación)

## Nomenclatura, lea esto antes de buscar en el repo

Dos sistemas de nomenclatura chocaron en este árbol de carpetas y ambos siguen en uso.

| Este repo | Fab Lab Bali | Qué es |
|---|---|---|
| `node-v3.1/` | **Node V3.1** | Ensamble atornillado, soporte de pared separado. Reemplazado. |
| `node-v3.2/` (aquí) | **Node V3.2** | Totalmente sin tornillos, montaje integrado. **Construya este.** |

`node-v3.1/` y Node V3.1 son los *mismos seis archivos STL* — verificado byte por byte, no
inferido de los nombres de archivo. El repo recibió las mallas en septiembre de 2026 sin el
documento que las describía; esta carpeta y [`../node-v3.1/`](../node-v3.1/) son ese
documento, que llega tarde.

El linaje de la carcasa cuenta v1-caja → v2-linterna → v3-calabaza → v4-columna → v5 piña →
v6 → v7. Fab Lab Bali cuenta generaciones de nodo completo: V1 → V2 → V3.1 → V3.2. Los dos
conteos no tienen relación y van a seguir chocando; la tabla de arriba es el mapeo.

## Qué cambió respecto a v6 (= Node V3.1)

| | v6 / Node V3.1 | **v7 / Node V3.2** |
|---|---|---|
| Tapa superior | Tornillos, colocados desde fuera del cuerpo | **Snap-fit de retén**, tres puntos de bloqueo en el perímetro interno |
| Retención de sensores y placa | Tornillos M2/M3 a través de placas de cubierta | **Ganchos snap-fit en voladizo** en cada pieza interna |
| Montaje en pared | Soporte impreso separado, atornillado | **Agujeros para tornillo moldeados** en la parte trasera del cuerpo |
| Montaje en poste | No soportado | **Ranuras integradas para amarres plásticos** en la parte trasera del cuerpo |
| Archivos de soporte de placa | 1 (los tornillos absorben la diferencia de ajuste) | **2** — elija según la mainboard, el espaciado de los ganchos difiere |
| Archivos de cubierta BME680 | 1 | **2** — el breakout de Bosch y el Seeed Grove tienen footprints distintos |
| Piezas impresas para construir un nodo | 6 | **5** (el soporte de pared desapareció) |

Tornillos eliminados del ensamble: **11 por nodo** (4 × M3×10, 3 × M2×10, 2 × M2×5, 2 × M3×10).
Los únicos sujetadores que quedan son las tuercas de la antena SMA, que son componentes comerciales, no impresos.

![Comparación entre Node V3.1 y V3.2](img/13-v31-v32-comparison.png)

Por qué importa en campo: a un sensor que se abre sin destornillador se le limpia el sensor de
PM. A uno que necesita un destornillador, del tamaño correcto, y cuatro tornillos que no se
rueden por un techo, no.

## Qué corrige y qué no corrige este diseño

El nodo que reemplaza esta generación se co-ubicó junto a un Smart Citizen Kit y
[falló dos veces](../node-v2/README.es.md).
Siendo francos sobre cuáles de esas fallas resuelve la V3.2:

**Corregido — resucción del aire de salida.** En una carcasa compacta, el flujo de salida del
propio sensor de PM es reabsorbido por su entrada, y el nodo termina midiendo aire que ya
midió. La pieza [`OUTFLOW_DUCT_HM3301`](stl/OUTFLOW_DUCT_HM3301.stl) lleva el aire de salida
hacia un costado, lejos de la entrada. Esta es una corrección real para un problema real.

**No abordado — las dos fallas de campo documentadas.** Ninguna aparece en el documento
fuente, y la geometría indica que no se diseñó contra ninguna de las dos:

1. **Entrada por la parte inferior.** La evaluación de la V2 encontró que la entrada orientada
   hacia abajo restringía la circulación, de modo que los picos de PM llegaban tarde y
   aplanados. La entrada de la V3.2 sigue en la parte inferior del cuerpo ([`05-underside-intake-outflow.png`](../node-v3.1/img/05-underside-intake-outflow.png)).
   El primer requisito para la V3 en el informe de la V2 era *"entrada desde arriba o por los
   costados abiertos, no desde abajo."* Ese requisito no se cumple.
2. **Autocalentamiento del BME680.** La evaluación de la V2 encontró que la radio Wi-Fi del
   ESP32 calentaba el BME680 a través de una pared divisoria, empujando la temperatura por
   encima de la ambiente y arrastrando la RH hacia abajo con ella. La V3.2 sigue alojando el
   BME680 en un bolsillo del cuerpo principal, en el mismo volumen sellado que la radio, bajo
   una cubierta impresa plana — sin escudo de radiación, sin corte térmico.
   El segundo requisito del informe de la V2 tampoco se cumple.

<!-- TODO: esto necesita una decisión de Fab Lab Bali, no un arreglo de documentación. O bien
     (a) co-ubicar una V3.2 junto a un SCK y publicar el Δ°C y el retraso del PM — si el
     cuerpo compacto resulta no reproducir los errores de la V2, ese resultado vale más que
     la suposición; o (b) tratar el canal de temperatura como diagnóstico en lugar de
     ambiental y etiquetarlo así en el tablero. No lo deje implícito. -->

Hasta que se haya co-ubicado una V3.2, **trate sus canales de temperatura y humedad como no
verificados**, y espere que los picos de PM se lean bajos. Eso no es razón para dejar de
instalar — es razón para hacer la co-ubicación de la primera semana que la campaña ya le exige
a cada nodo nuevo.

## Arquitectura híbrida — qué se puede sustituir

El sentido del cuerpo V3 es que el stock local se acaba. Una sola carcasa, varias listas de
materiales.

**Mainboard** — elija una:

- **Seeed Grove Shield for XIAO.** Plug-and-play, sin soldadura. Acepta un XIAO ESP32-C3 o ESP32-S3.
- **PCB custom DIY.** Más barato, requiere soldadura. Acepta un XIAO ESP32-C3/S3, un ESP32-C3/S3
  Supermini, o el Seeed ESP32-S3 con LoRa integrado en la placa.

> **El Supermini y el XIAO no son compatibles pin a pin en el PCB DIY.** El I²C queda en D4/D5
> para el XIAO y en D8/D9 para el Supermini. Revise [Cableado](#cableado) antes de calentar el cautín.

![Opciones de mainboard en el compartimento](../node-v3.1/img/10-mainboard-options.png)

**Sensor ambiental** — breakout Bosch BME680, o Seeed Grove BME680. Footprints distintos,
así que imprima la cubierta correspondiente:
[`COVER_BME680_BOSCH.stl`](stl/COVER_BME680_BOSCH.stl) o
[`COVER_BME680_SEEED_STUDIO.stl`](stl/COVER_BME680_SEEED_STUDIO.stl).

**Sensor de PM** — solo Seeed Studio HM3301. No hay ninguna alternativa prevista en el diseño.

**Radio** — el cuerpo viene en dos variantes: un puerto SMA (Wi-Fi) o dos (Wi-Fi + LoRa
sub-GHz). LoRa solo está disponible en el Seeed ESP32-S3 con el módulo integrado en la placa.

**Alimentación** — USB Type-C, 5 V DC.

## Flujo de aire

El aire exterior entra por la entrada inferior hacia el ventilador propio del HM3301. El aire
ya medido sale por el ducto de extensión, que lo dirige hacia un costado y lejos de la entrada
para que no se vuelva a medir de inmediato.

![Entrada inferior y ducto de salida](../node-v3.1/img/05-underside-intake-outflow.png)

Lea eso junto con [Qué corrige y qué no corrige este diseño](#qué-corrige-y-qué-no-corrige-este-diseño)
— el ducto resuelve la resucción, no la restricción de la entrada.

## Piezas impresas

**Cinco piezas por nodo.** Dos de los ocho archivos son pares excluyentes, y las dos variantes
de cuerpo son una elección, no un conjunto.

| Pieza | Archivo | Cant. | Nota |
|---|---|---|---|
| Tapa superior | [`TOP_COVER.stl`](stl/TOP_COVER.stl) | 1 | Snap-fit de retén |
| Cuerpo principal — antena doble | [`MAIN_BODY_2_ANTENNA.stl`](stl/MAIN_BODY_2_ANTENNA.stl) | 1 | **o** ↓ — Wi-Fi + LoRa |
| Cuerpo principal — antena simple | [`MAIN_BODY_1_ANTENNA.stl`](stl/MAIN_BODY_1_ANTENNA.stl) | 1 | **o** ↑ — solo Wi-Fi |
| Cubierta BME680 — Seeed | [`COVER_BME680_SEEED_STUDIO.stl`](stl/COVER_BME680_SEEED_STUDIO.stl) | 1 | **o** ↓ |
| Cubierta BME680 — Bosch | [`COVER_BME680_BOSCH.stl`](stl/COVER_BME680_BOSCH.stl) | 1 | **o** ↑ |
| Cubierta HM3301 + soporte de placa — Grove Shield | [`COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl`](stl/COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl) | 1 | **o** ↓ |
| Cubierta HM3301 + soporte de placa — PCB DIY | [`COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl`](stl/COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl) | 1 | **o** ↑ |
| Ducto de salida | [`OUTFLOW_DUCT_HM3301.stl`](stl/OUTFLOW_DUCT_HM3301.stl) | 1 | Sin cambios respecto a v6 |

Las medidas se leyeron de las mallas el 2026-09-23, así que son reales. Nada de lo que está en
[Ajustes de impresión](#ajustes-de-impresión) lo es.

| Archivo | Caja envolvente (mm) | Triángulos |
|---|---|---|
| `TOP_COVER.stl` | 117.9 × 88.0 × 32.0 | 14,154 |
| `MAIN_BODY_2_ANTENNA.stl` | 113.9 × 94.0 × 28.9 | 5,544 |
| `MAIN_BODY_1_ANTENNA.stl` | 113.9 × 94.0 × 28.9 | 5,422 |
| `COVER_HM3301_BRACKET_BOARD_GROVE_SHIELD.stl` | 80.2 × 43.3 × 12.4 | 5,166 |
| `COVER_HM3301_BRACKET_BOARD_PCB_DIY.stl` | 80.2 × 43.3 × 13.9 | 2,472 |
| `OUTFLOW_DUCT_HM3301.stl` | 46.0 × 26.0 × 12.0 | 1,548 |
| `COVER_BME680_BOSCH.stl` | 45.9 × 26.1 × 3.4 | 1,936 |
| `COVER_BME680_SEEED_STUDIO.stl` | 45.9 × 26.1 × 2.2 | 640 |

El cuerpo creció 2 mm en Y respecto a v6 (92.0 → 94.0). Eso son las características de montaje
integradas en la cara trasera — los 2 mm son el soporte de pared, absorbido dentro del cuerpo.

Las piezas están exportadas en coordenadas de ensamble, no de impresión — la mayoría tiene un
mínimo en Z negativo. Los slicers las bajan a la cama, pero los archivos no vienen
preorientados para imprimir.

![Las piezas impresas](../node-v3.1/img/11-printed-parts-v31.png)

## Ajustes de impresión

<!-- TODO: no se conoce ninguno de estos. Ningún valor de esta tabla es real. Fab Lab Bali ya
     imprimió estas piezas — los ajustes existen en el perfil de slicer de alguien. Expórtelo. -->

| | |
|---|---|
| Material | TODO — **PETG o ASA**. El PLA fluye y se pandea en un techo de Bali; el README principal ya lo descarta |
| Altura de capa | TODO |
| Paredes / perímetros | TODO — los ganchos snap-fit son la ruta de carga aquí, así que esto no es cosmético |
| Relleno | TODO |
| Temperatura de nozzle / cama | TODO |
| Soportes | TODO — indicar por pieza |
| Orientación de impresión | TODO — indicar por pieza. En la v7 importa el doble: la dirección de las capas decide si un gancho en voladizo flexiona o se rompe |
| Tiempo de impresión estimado / masa de filamento | TODO |

Indique los requisitos de máquina en términos de taller — volumen de impresión mínimo,
diámetro de nozzle — y no por marca de impresora. Un laboratorio en otra ciudad tiene otra máquina.

**Las piezas snap-fit son más sensibles a la impresión que las atornilladas.** Un gancho en
voladizo impreso con las líneas de capa cruzando su raíz es un gancho que se rompe en el primer
ensamblaje. Hasta que se documente la orientación, imprima las cubiertas planas y cuente con
perder una.

## Lista de materiales

Ver [`bom.csv`](bom.csv) para la versión legible por máquina en las columnas Open-Make del repo.

| # | Componente | Especificación / modelo | Cant. | Nota |
|---|---|---|---|---|
| 1 | Procesador principal | XIAO ESP32-C3 / ESP32-S3, ESP32-C3/S3 Supermini, o Seeed ESP32-S3 con LoRa | 1 | Maestro en el bus I²C |
| 2 | Placa base | Seeed Grove Shield for XIAO **o** PCB custom DIY | 1 | Define qué STL de soporte de placa imprime |
| 3 | Sensor de PM | Seeed Studio HM3301 | 1 | PM2.5 / PM10 láser, I²C, dirección 0x40 |
| 4 | Sensor ambiental | Breakout Bosch BME680 **o** Seeed Grove BME680 | 1 | T / RH / presión / gas, I²C, 0x76 o 0x77 |
| 5 | Entrada de alimentación | USB Type-C | 1 | 5 V DC |
| 6 | Pigtail | SMA hembra a IPEX / U.FL | 1–2 | 1 para radio simple, 2 para doble |
| 7 | Antena externa | 2.4 GHz (+ LoRa sub-GHz si es doble) | 1–2 | |
| 8 | Juego de cables | JST-XH y Grove de 4 pines | 1 juego | Cableado interno |
| 9 | Amarres plásticos | 20–30 cm, 3–4 mm de ancho | 2 | Solo para montaje en poste |

**Sin precios.** La BoM de la V3.2 del documento fuente no tiene columna de precio, y la
campaña no tiene una cotización vigente para esta construcción. La
[BoM del Node V2](../node-v2/bom.csv) trae precios en IDR de una compra
anterior — úselos como orden de magnitud, no como cotización, y tenga en cuenta que la V2 usaba
otra mainboard.

<!-- TODO: costear esta construcción. Una cifra de costo es la pregunta más frecuente de los
     banjars y el único número que este documento no puede responder hoy. -->

## Cableado

Todos los sensores están en un mismo bus I²C, leídos en paralelo.

> **El HM3301 necesita 5 V.** Su ventilador y su láser no funcionan a 3.3 V. La tabla del Grove
> Shield del documento fuente dice 3.3 V; **el propio esquema del Grove Shield de ese documento
> dice 5 V**, igual que todas las demás tablas. El esquema es el correcto. Aquí está corregido.
> <!-- Reportado aguas arriba — ver "Lo que todavía falta en esta documentación". -->

### Grove Shield (XIAO ESP32-C3 / S3 / S3+LoRa)

| Componente | Pin del sensor | Pin de la mainboard | Señal |
|---|---|---|---|
| USB Type-C | VBUS / 5V | 5V / VIN | Entrada de alimentación (+5 V) |
| BME680 | VCC | 3.3V | Alimentación |
| | GND | GND | Tierra |
| | SDA | SDA (I²C dedicado) | Datos I²C |
| | SCL | SCL (I²C dedicado) | Reloj I²C |
| HM3301 | VCC | **5V** | Alimentación — *no 3.3 V; ver la nota de arriba* |
| | GND | GND | Tierra |
| | SDA | SDA (en paralelo con BME680) | Datos I²C |
| | SCL | SCL (en paralelo con BME680) | Reloj I²C |
| Módulo LoRa | Header | Header de conexión directa, ESP32-S3 | Conexión directa |

![Esquema de cableado del Grove Shield](img/07-wiring-grove-shield.png)
![Vista de protoboard del Grove Shield](img/10-breadboard-grove-shield.png)

### PCB DIY con XIAO ESP32-C3 / S3 / S3+LoRa

| Componente | Pin del sensor | Pin de la mainboard | Señal |
|---|---|---|---|
| Breakout USB Type-C | VBUS / 5V | 5V / VIN | Entrada de alimentación (+5 V) |
| BME680 | VCC | 3.3V | Alimentación |
| | GND | GND | Tierra |
| | SDA | **D4** | Datos I²C |
| | SCL | **D5** | Reloj I²C |
| HM3301 | VCC | 5V | Alimentación |
| | GND | GND | Tierra |
| | SDA | D4 (en paralelo con BME680) | Datos I²C |
| | SCL | D5 (en paralelo con BME680) | Reloj I²C |
| Módulo LoRa | Header | Header de conexión directa / SPI | Directo |

![PCB DIY con XIAO — esquema de cableado](img/08-wiring-pcb-diy-xiao.png)
![PCB DIY con XIAO — vista de protoboard](img/11-breadboard-pcb-diy-xiao.png)

### PCB DIY con ESP32-C3 / ESP32-S3 Supermini

| Componente | Pin del sensor | Pin de la mainboard | Señal |
|---|---|---|---|
| Breakout USB Type-C | VBUS / 5V | 5V / VIN | Entrada de alimentación (+5 V) |
| BME680 | VCC | 3.3V | Alimentación |
| | GND | GND | Tierra |
| | SDA | **D8** | Datos I²C |
| | SCL | **D9** | Reloj I²C |
| HM3301 | VCC | 5V | Alimentación |
| | GND | GND | Tierra |
| | SDA | D8 (en paralelo con BME680) | Datos I²C |
| | SCL | D9 (en paralelo con BME680) | Reloj I²C |
| Módulo LoRa | Header | Header de conexión directa / SPI | Directo |

![Esquema de cableado del Supermini](img/09-wiring-pcb-diy-supermini.png)
![Vista de protoboard del Supermini](img/12-breadboard-pcb-diy-supermini.png)

## Ensamblaje

Sin destornillador. Cada unión interna es un snap fit.

1. **Cuerpo.** Pase el o los pigtails SMA por el o los agujeros de antena de
   `MAIN_BODY_1_ANTENNA.stl` o `MAIN_BODY_2_ANTENNA.stl` y apriete la tuerca desde afuera.
   Este es el único sujetador de toda la construcción.
2. **BME680.** Deje caer el sensor en su bolsillo en el piso del cuerpo. Presione la cubierta
   correspondiente — Bosch o Seeed — hasta que los ganchos en voladizo hagan clic.
3. **HM3301 y ducto.** Asiente el sensor de PM en su compartimento. Coloque
   `OUTFLOW_DUCT_HM3301.stl` en el canal de salida. Presione la cubierta HM3301 correspondiente —
   Grove Shield o PCB DIY — sobre el sensor hasta que sus ganchos enganchen.
4. **Mainboard.** Presione la placa hacia abajo sobre los ganchos en voladizo moldeados en la
   cubierta del HM3301. Conecte los cables JST/Grove del USB-C, el BME680 y el HM3301, y clipe
   el pigtail en el puerto U.FL.
5. **Cierre.** Coloque `TOP_COVER.stl` y presione los cuatro lados hasta que los retenes hagan clic.

![Disposición interna](img/02-internal-layout.png)
![Ganchos snap-fit en voladizo](img/03-cantilever-snapfit-hooks.png)
![Tapa superior con snap-fit de retén](img/04-detent-snapfit-top-cover.png)

Soporte de placa, según la mainboard:

| | |
|---|---|
| ![Soporte Grove Shield](img/05-bracket-grove-shield.png) | ![Soporte PCB DIY](img/06-bracket-pcb-diy.png) |

<!-- TODO: fotografiar un ensamblaje real. Todas las imágenes aquí son renders CAD. Quien
     construya necesita ver el gancho enganchado, y cuánta fuerza es en realidad "hasta que hace clic". -->

## Montaje

Sin soporte impreso. Ambas opciones vienen moldeadas en la parte trasera del cuerpo.

- **Pared plana.** Ponga dos tornillos o clavos en la pared y cuelgue el cuerpo de los agujeros
  para tornillo moldeados.
- **Poste o árbol.** Pase dos amarres plásticos por las ranuras integradas, envuelva y apriete.

<!-- TODO: separación de tornillos y diámetro de agujero para la opción de pared; diámetro
     máximo de poste para las ranuras de amarres. Ambos se pueden leer del CAD, ninguno está en la fuente. -->

La ubicación importa más que el soporte. La altura de montaje, hacia dónde mira la entrada y
qué le da sombra están en la ficha de sitio de la campaña — ver la
[documentación del taller](../../../../docs/) antes de elegir un punto.

## Firmware y flujo de datos

Sin cambios en toda la generación V3. Ver [`../../firmware/`](../../firmware/) para el
sketch, y las notas de integración con Smart Citizen de la campaña para el transporte MQTT — los
nodos DIY publican en `device/sck/<device_token>/readings` sobre TLS en el 8883, y el token del
dispositivo es toda la identidad.

## Problemas conocidos en estos archivos

Encontrados por inspección de mallas el 2026-09-23, antes de la publicación:

- **`OUTFLOW_DUCT_HM3301.stl` tiene 1 arista abierta y 1 triángulo degenerado (de área cero).**
  Heredado sin cambios de v6, donde el mismo defecto se señaló y no se corrigió. Los slicers
  suelen repararlo en silencio, lo que significa que el resultado es lo que haya decidido su
  slicer. Reexportar desde la fuente.
- **Las otras siete piezas son estancas** y no tienen triángulos degenerados. Vale la pena notar
  que el `Main_Body.stl` de v6 tenía 4 aristas abiertas y los cuerpos de v7 no tienen ninguna —
  el cuerpo se reexportó limpio en algún punto entre ambos.
- **No se publica fuente CAD.** Ver [`cad/README.md`](cad/README.md). Este es el bloqueo para
  llamar al diseño listo para replicación, y es el mismo bloqueo que tiene v6.

## Lo que todavía falta en esta documentación

Diez puntos abiertos, greppables como `TODO` en la fuente de este archivo. Primero los bloqueantes:

1. **Fuente CAD.** Los STL son una exportación, no un diseño. Nadie fuera de Fab Lab Bali puede
   cambiar el ángulo de un gancho, mover un puerto o adaptar otro sensor.
2. **Una V3.2 co-ubicada.** Dos de las tres fallas documentadas de la V2 quedan sin atender en
   la geometría. Hasta que una unidad haya corrido una semana junto a un SCK, los canales T/RH
   no están verificados y los picos de PM son sospechosos.
3. **Ajustes de impresión.** No se conoce nada. En un diseño snap-fit, la orientación y el
   número de perímetros deciden si la cosa se ensambla siquiera.
4. **Costo.** Sin precio para esta construcción, en ninguna moneda.
5. **Fotografías del ensamblaje.** Todas las imágenes son renders.
6. **Separación de tornillos y diámetro de agujero para montaje en pared; diámetro máximo de poste.**
7. **Dimensiones exteriores ensambladas y masa.**
8. **Tiempo de armado**, en minutos, para alguien que nunca armó uno.
9. **Grado de protección contra ingreso.** La fuente V3 declara resistencia a salpicaduras para
   la generación pero no nombra ni ensayo ni grado.
10. **Elección de antena.** Ganancia, y si la variante de dos antenas tiene un problema de
    aislamiento medido entre los puertos de 2.4 GHz y sub-GHz.

Se corrigieron dos errores del documento fuente en lugar de copiarlos, y ambos deberían volver
a Fab Lab Bali:

- La tabla de cableado del Grove Shield le da 3.3 V al HM3301; su propio esquema da 5 V.
  Aquí se corrigió a 5 V. Seguir la tabla dejaría muertos el ventilador y el láser.
- La sección de ensamblaje de la V3.1 nombra `V3.1_Top_Cover.stl` y `V3.1_Wall_Bracket_Separate.stl`;
  no existen tales archivos en ninguna de las dos publicaciones. Los nombres reales son
  `TOP COVER.stl` y `BRACKET TO WALL.stl`. Documentado en [`../node-v3.1/`](../node-v3.1/).

---

*Making Sense Bali · Chapter Fab City Bali · alojado por Fab Lab Bali.
Hardware CERN-OHL-W-2.0 · documentación CC-BY-SA-4.0.*
