[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Nodo DIY V2 — el nodo triangular compacto

*Making Sense Bali · Chapter Fab City Bali · construido y probado en Fab Lab Bali*

**Seeed Studio XIAO ESP32-C3 + Seeed Grove HM3301 + Bosch BME680**, los tres dispuestos uno al lado del otro sobre un mismo piso de chasis, dentro de una carcasa triangular impresa en 3D. Construido para poner un nodo de calidad del aire ambiente a escala de banjar, escuela y warung en Desa Serangan por más o menos lo que cuesta un teléfono.

> **Estado: construido, desplegado, evaluado en campo y superado por sus propios resultados.**
> Dos de los tres objetivos de diseño se cumplieron. El tercero no: la carcasa calienta su propio
> sensor de temperatura, y su toma de aire inferior llega tarde a los picos reales de contaminación.
> **No imprimas esta carcasa para un despliegue.** Lee primero
> [Evaluación](#evaluación--qué-mostró-la-prueba-de-campo) y construye
> [la piña](../enclosure/) en su lugar. Esta carpeta se conserva porque un diseño que falló por dos
> razones con nombre propio vale más para quien construya después que uno que simplemente funcionó.

> **Sobre el nombre, para que nadie pierda un día con esto.** "V2" aquí es la segunda generación
> del *nodo completo* según la numeración de Fab Lab Bali. **No** es
> `enclosure/archive/v2-lantern/`, que pertenece a un linaje de carcasas distinto
> (v1-box → v2-lantern → v3-gourd → v4-column → v5 piña). Dos líneas de diseño distintas, dos
> numeraciones distintas. La electrónica y el firmware son compartidos; las carcasas no tienen relación.

![Vista explosionada del conjunto Nodo V2](img/01-exploded-view.png)

## Contenido

- [Por qué se construyó](#por-qué-se-construyó)
- [El concepto](#el-concepto)
- [De dónde salió la forma](#de-dónde-salió-la-forma)
- [Arquitectura física y flujo de aire](#arquitectura-física-y-flujo-de-aire)
- [Electrónica](#electrónica)
- [Lista de materiales](#lista-de-materiales)
- [La placa base a medida](#la-placa-base-a-medida)
- [Distribución interna](#distribución-interna)
- [Placa inferior — energía, RF, aire](#placa-inferior--energía-rf-aire)
- [Montaje](#montaje)
- [Firmware y flujo de datos](#firmware-y-flujo-de-datos)
- [Evaluación — qué mostró la prueba de campo](#evaluación--qué-mostró-la-prueba-de-campo)
- [Qué tiene que hacer distinto la V3](#qué-tiene-que-hacer-distinto-la-v3)
- [Archivos](#archivos)
- [Qué le falta todavía a esta documentación](#qué-le-falta-todavía-a-esta-documentación)

## Por qué se construyó

Una estación de calidad del aire de grado de referencia cuesta más de lo que cualquier banjar, escuela o grupo vecinal de Bali va a reunir por su cuenta. La propia tabla de niveles de la campaña las sitúa en [USD 5.000–25.000+](../README.es.md#dónde-encaja-esto--los-niveles-de-sensores-de-la-campaña). Armar algo con sensores modulares baratos es la alternativa evidente, y de eso trata todo este árbol de carpetas.

Lo difícil no es la electrónica. Es la caja.

Una carcasa mal resuelta se convierte en una trampa: encierra dentro el calor residual de la microelectrónica, o ahoga el aire exterior antes de que llegue al sensor. En cualquiera de los dos casos el nodo informa números que describen el interior de una carcasa de plástico y no el aire del lugar donde lo colgaron — y los informa con la misma precisión convincente que una lectura correcta. Eso es lo que hace que el fallo sea peligroso y no solo molesto.

| | |
|---|---|
| Estación de referencia fija | ![Estación de monitoreo de referencia fija](img/02-ref-station-fixed.png) |
| Estación de referencia móvil | ![Estación móvil de monitoreo de calidad del aire](img/03-ref-station-mobile.png) |

## El concepto

Un chasis horizontal compacto. Todos los componentes van planos sobre un único piso en **configuración lado a lado (side-by-side)**, separados por un tabique interno, para que el nodo siga siendo lo bastante pequeño como para llevarlo en una mano y lo bastante presentable como para colgarlo en la pared de otra persona.

Tres objetivos de partida:

1. Recortar el costo de producción ~90% frente a una estación industrial estándar.
2. Producir una carcasa sólida, compacta, imprimible en una impresora 3D local y a salvo de salpicaduras.
3. Obtener lecturas ambientales diarias precisas.

Los objetivos 1 y 2 se sostuvieron. El 3 no — ver la evaluación.

> **Sobre la cifra del 90%.** El documento original la enuncia de dos formas: una vez como un recorte del 90% en el costo de producción del *chasis*, otra como un recorte del 90% en el costo de producción *total*. Ninguna de las dos versiones nombra la estación de referencia contra la que se mide, así que tal como está escrita la afirmación no se puede verificar. Contra el propio rango de Nivel 0 de la campaña el ahorro real es mucho mayor que el 90%, así que probablemente sea conservadora antes que inflada — pero quien la cite a un financiador debería nombrar primero una estación concreta y su precio. <!-- TODO: elegir una estación de referencia con nombre y precio, y enunciar la afirmación una sola vez, en una sola forma. -->

| | |
|---|---|
| ![Diagrama de la vista inferior del chasis triangular](img/04-bottom-view-diagram.png) | ![Wireframe del interior del chasis](img/05-chassis-interior-wireframe.png) |

## De dónde salió la forma

La distribución de compartimentos está tomada directamente de la arquitectura de carcasa de la **estación Smart Citizen Kit (SCK 2.3)** — el documento original nombra la modularidad, la limpieza y el minimalismo como lo que tomó de ella. Conviene notar que la columna vertebral de calibración de la propia campaña es el **SCK 2.1** ([tabla de niveles](../README.es.md#dónde-encaja-esto--los-niveles-de-sensores-de-la-campaña)); el 2.3 es un kit posterior, así que esto es un préstamo de la línea de producto y no de la estación exacta contra la que después se midió el Nodo V2.

| | |
|---|---|
| ![Estación SCK desplegada en campo](img/06-sck-station-deployed.png) | ![Diagrama explosionado de la estación SCK](img/07-sck-station-exploded.png) |

Camprodon, G., González, Ó., Barberán, V., Pérez, M., Smári, V., de Heras, M.Á., Bizzotto, A., *Smart Citizen Kit and Station: An open environmental monitoring system for citizen participation and scientific experimentation*, HardwareX 6 (octubre de 2019). <https://www.sciencedirect.com/science/article/pii/S2468067219300203>

## Arquitectura física y flujo de aire

La carcasa es un triángulo obtuso en planta, con el interior dividido por tabiques. El recorrido del aire, tal como se diseñó:

- Los componentes van planos sobre un único piso de chasis. Un tabique mecánico separa el módulo principal (XIAO ESP32-C3) del compartimento de sensores.
- El aire exterior entra por **debajo** de la caja a través de una rejilla pequeña, atraviesa el interior en horizontal y sale por el **costado**.
- El sensor de gas y microclima BME680 va dentro del chasis principal, **mirando hacia abajo** (al suelo), sin ninguna cúpula de protección contra radiación por fuera.

Esas dos últimas decisiones son justamente las que revocó la prueba de campo. Aquí están escritas tal como se diseñaron, no como recomendación.

![Vista superior con los tres compartimentos](img/08-upper-view-compartments.png)

## Electrónica

Dos sensores comparten un mismo bus I²C como esclavos del maestro XIAO ESP32-C3.

| Desde el microcontrolador (XIAO) | Al sensor | Función | Color de cable |
|---|---|---|---|
| GND (pin 13) | BME680 + HM3301 | Tierra común | Negro |
| 5V (pin 14) | Sensor de polvo HM3301 | Alimentación principal 5 V | Rojo |
| 3V3 (pin 12) | Sensor de gas BME680 | Alimentación lógica 3,3 V | Amarillo |
| D4 (pin 5) | BME680 + HM3301 | Datos serie (bus SDA) | Violeta |
| D5 (pin 6) | BME680 + HM3301 | Reloj serie (bus SCL) | Azul |

Direcciones I²C, según el firmware compartido: **HM3301 en `0x40`**, **BME680 en `0x76`** (cae a `0x77` si SDO está tirado a 3V3).

**El pin 14 está serigrafiado `5V`** en la placa; el documento original lo llama VUSB. En un XIAO suele ser el raíl VBUS del USB, pero el Nodo V2 lo alimenta al revés — desde el jack DC de la placa inferior, a través de la bornera de la placa base. En cualquier caso, el ventilador y el láser del HM3301 son lo único que cuelga de los 5 V, así que un XIAO alimentado solo desde sus pads BAT dejaría muerto al sensor de polvo. La lista de materiales no incluye ninguna celda, así que este montaje nunca llega a ese caso; importa si alguien lo adapta. <!-- TODO: confirmar en una unidad física si el jack DC retroalimenta el pad de 5V o va cableado directo al conector del sensor. -->

| | |
|---|---|
| ![Diagrama de cableado](img/10-wiring-diagram.png) | ![Esquemático](img/11-schematic.png) |

## Lista de materiales

Versión legible por máquina, con columnas de aprovisionamiento: **[`bom.csv`](bom.csv)**.

| # | Componente | Especificación | Cant. | Unitario (IDR) | Total (IDR) |
|---|---|---|---|---|---|
| 1 | Seeed Studio XIAO ESP32-C3 | MCU RISC-V, Wi-Fi/BLE, USB-C | 1 | 165.000 | 165.000 |
| 2 | Seeed Grove HM3301 | Sensor de partículas por dispersión láser | 1 | 700.000 | 700.000 |
| 3 | CJMCU-680 (BME680) | Placa breakout de sensor ambiental 4 en 1 | 1 | 282.000 | 282.000 |
| 4 | Carcasa impresa Nodo V2 | Caja triangular a medida, PETG | 1 | 65.000 | 65.000 |
| 5 | Accesorios de cableado | Jumpers Dupont hembra + cable Grove de 4 pines | 1 lote | 35.000 | 35.000 |
| 6 | Tornillo M2 × 6 mm | Cabeza plana, acero al carbono (NINDEJIN) | 15 | 200 | 3.000 |
| 7 | Tornillo M3 × 6 mm | Cabeza plana, acero al carbono (NINDEJIN) | 4 | 300 | 1.200 |
| 8 | Tornillo M3 × 10 mm | Cabeza plana, acero al carbono (NINDEJIN) | 4 | 400 | 1.600 |
| 9 | Tornillo M3 × 14 mm | Cabeza plana, acero al carbono (NINDEJIN) | 2 | 500 | 1.000 |
| | | | | **Total** | **Rp 1.253.800** |

El documento original da estas cifras sin decir dónde ni cuándo se compraron las piezas, así que tómalas como el costo de un montaje en Indonesia y no como una lista de precios. La [nota de aprovisionamiento del README principal](../README.es.md) es mejor guía para quien vaya a pedir: el HM3301 es el que manda en el costo, y pedirlo directo a Seeed suele salir más barato que la venta local al público cuando es un lote. Cualquier tornillo de cabeza plana equivalente sustituye a los de marca.

<!-- TODO: dónde y cuándo se compraron las piezas, y si estos son precios minoristas o de distribuidor. -->
<!-- TODO: equivalente en USD + el tipo de cambio IDR/USD en la fecha de compra, para que la cifra siga siendo comparable con los costos en USD citados en ../README.es.md. -->
<!-- TODO: qué cubren los Rp 65.000 de la carcasa (solo filamento, o filamento más tiempo de máquina) y la masa de PETG en gramos, para poder recalcularlo en cualquier lugar. -->

## La placa base a medida

Los cables Dupont sueltos en un chasis tan apretado se convierten en un problema de mantenimiento en la primera visita de servicio, así que el XIAO no se cablea directamente. Va soldado sobre una **perfboard de 3 × 7 cm** que hace de pequeña placa portadora.

**Cara superior.** El XIAO en el centro. Un conector JST/Grove de 4 pines a cada lado da a los sensores una conexión plug-and-play. Una bornera de tornillo verde recibe la entrada de alimentación principal.

**Cara inferior.** Cableado punto a punto con hilo rígido. Rojo (5 V / 3,3 V) y negro (GND) en paralelo como bus de alimentación; verde y azul distribuyen el bus I²C (SDA y SCL) en paralelo a ambos conectores de sensor.

| | |
|---|---|
| ![Placa base, cara superior](img/13-mainboard-top.jpg) | ![Placa base, cara inferior](img/14-mainboard-bottom.jpg) |

> **Conflicto de código de colores, sin resolver.** La tabla de cableado de arriba dice **violeta = SDA, azul = SCL**. Los jumpers de la propia perfboard usan **verde y azul** para esas mismas dos señales. Ambas afirmaciones vienen del documento original. Sea cual sea la correcta, los dos códigos de color se contradicen, y quien replique siguiendo uno mientras mira una foto del otro va a intercambiar SDA y SCL — lo que se manifiesta como "sensor no encontrado" y te manda a perseguir un fallo de alimentación que no existe. <!-- TODO: revisar una unidad física, elegir un código de color y corregir el otro. -->

## Distribución interna

La carcasa impresa divide el piso en horizontal, con torretas de tornillo integradas que fijan cada pieza en su sitio.

**Bahía izquierda — polvo.** El módulo láser HM3301, fijado con cuatro tornillos M2 directamente al chasis inferior.

**Bahía central — el cerebro.** La placa base sobre perfboard con el XIAO, asentada en su canal a una separación deliberada del sensor de polvo para que nada haga cortocircuito.

**Punta del triángulo — microclima.** El BME680 (la PCB violeta) en la esquina más aguda de la carcasa, desplazado hacia atrás en dirección a la ranura del chasis para que capte más rápido los cambios de temperatura y humedad exteriores.

![Distribución interna de una unidad construida](img/15-internal-layout-built.jpg)

## Placa inferior — energía, RF, aire

Todas las interfaces externas se concentran en la placa blanca inferior, lo que mantiene los costados limpios y los conectores fuera de la lluvia.

- **Entrada de energía.** Un jack DC hembra, soldado y protegido con termorretráctil amarillo, que lleva 5 V DC a la bornera de la placa base.
- **RF.** Un pigtail SMA atraviesa la placa, con una antena omni de 2,4 GHz externa apuntando hacia abajo y de lado para que el enlace Wi-Fi sobreviva a los muros de un edificio de banjar.
- **Aire.** Una rejilla circular justo debajo del ventilador de admisión del HM3301, que es la entrada principal de aire ambiente del nodo.

| | |
|---|---|
| ![Render de la vista inferior con anotaciones](img/09-bottom-view-render.png) | ![Placa inferior de una unidad construida](img/16-base-plate-io.jpg) |

## Montaje

Herramientas: soldador, destornillador que corresponda a tus tornillos, alicate de corte y pelacables, pistola de calor o encendedor para el termorretráctil. <!-- TODO: tiempo de montaje. El documento original no registra ninguno; las ~3 horas del README principal son para otro montaje. -->

1. **Imprime la carcasa** en PETG, no en PLA — [el PLA se ablanda a las temperaturas de un techo balinés](../README.es.md). <!-- TODO: altura de capa, número de perímetros, relleno, temperaturas de nozzle/cama, orientación de impresión, soportes, tiempo de impresión. Nada de esto está en el documento original y todo hace falta para reimprimir la pieza. -->
2. **Arma la placa base.** Suelda el XIAO al centro de la perfboard de 3 × 7 cm, los dos conectores Grove/JST a cada lado y la bornera de tornillo. Después traza los buses por debajo, punto a punto: rojo y negro en paralelo para la alimentación, las dos líneas I²C en paralelo hacia ambos conectores.
3. **Monta el herraje de la placa inferior.** Suelda los cables del jack DC, aísla las uniones con termorretráctil y monta el pigtail SMA. Hazlo antes de que entre nada en la carcasa: la placa se trabaja mucho mejor vacía.
4. **Monta el sensor de polvo.** HM3301 en la bahía izquierda, cuatro tornillos M2 × 6 en las torretas del chasis, ventilador de admisión mirando a la rejilla circular.
5. **Monta la placa base.** Perfboard en el canal central, atornillada, verificando la separación con el sensor de polvo.
6. **Monta el BME680** en la punta del triángulo, desplazado hacia atrás hacia la ranura del chasis.
7. **Conecta.** Cable Grove del conector de la placa base al HM3301; los cuatro cables del BME680 al otro conector. Antena al XIAO. Cables del jack DC a la bornera.
8. **Flashea y comprueba** antes de cerrar la carcasa — ver más abajo. Edita `SC_DEVICE_TOKEN` en el sketch con el token de Smart Citizen propio de este nodo antes de flashear, y después provisiona el Wi-Fi en el primer arranque a través del portal cautivo `MakingSenseBali-XXXX`. En la salida serie, `[hm3301] online at 0x40` nombra su dirección; la línea del BME680 solo informa que respondió, no en cuál de `0x76` / `0x77` lo hizo.
9. **Cierra** con los tornillos M3 (6, 10 y 14 mm; las torretas de la carcasa determinan cuál va dónde).

> Los pasos 2, 5 y 7 son los tres que más necesitan una foto cenital con las piezas etiquetadas. Las dos fotos de la placa base cubren razonablemente el paso 2; los pasos 5 y 7 dependen hoy de una única foto general del interior. <!-- TODO: fotografiar los pasos 5 y 7. -->

**Antes de desplegar**, recubre la cara soldada de la perfboard con recubrimiento conforme de silicona, enmascarando las aberturas de los sensores y el conector USB-C. Bali está por encima del 80% de humedad relativa buena parte del año y las placas sin recubrir se corroen en 6–12 meses; el razonamiento y el producto están en [el README principal](../README.es.md).

## Firmware y flujo de datos

El Nodo V2 corre el sketch compartido de nodo DIY de la campaña sin más cambios de código que el token de Smart Citizen propio de cada dispositivo: **[`../firmware/diy_node/`](../firmware/diy_node/)**. El mismo archivo apunta tanto al XIAO ESP32-S3 como al ESP32-C3 — el mapeo de pines D4/D5 se resuelve por variante de placa, así que nada en él es específico de un chip.

Cada 60 segundos el XIAO direcciona cada sensor por turno vía I²C, empaqueta las lecturas como JSON y las publica por Wi-Fi vía MQTT en el puerto 8883 a `mqtt.smartcitizen.me`, donde las lee el tablero de la campaña. La conexión es TLS pero **la validación de certificado está desactivada** en esta versión del firmware (`net.setInsecure()`) — suficiente para un kit de taller, no para un nodo cuyos datos entran en un argumento de política pública. El propio sketch lo dice donde ocurre.

IDs de canal del catálogo global de Smart Citizen que publica este nodo:

| ID | Canal | Unidad |
|---|---|---|
| 233 / 234 / 235 | HM3301 PM1.0 / PM2.5 / PM10.0 | µg/m³ |
| 237 / 238 | BME68X temperatura / humedad (ver nota) | °C, %HR |
| 239 | BME68X presión | kPa |
| 240 | BME68X resistencia de gas | Ω (bruto) |
| 241 | BME68X IAQ | índice, aproximación abierta |

> **Los canales 237 / 238 se llaman "heat-compensated" en el catálogo de Smart Citizen.** El firmware publica los valores del BME680 tal cual, sin aplicar ninguna compensación de carcasa. En este nodo en particular el nombre promete algo que el dato no lleva — que es justamente el error que la evaluación acabó midiendo.

![Diagrama de integración del sistema](img/12-system-integration-diagram.png)

> **Documentación contra código, señalado.** El documento original describe lecturas brutas que se "filtran mediante una función de cálculo de calibración local para eliminar el error del chasis" antes de publicarse. **Esa función no existe en el firmware enlazado.** El firmware publica temperatura y humedad en bruto, más una aproximación de IAQ en el dispositivo explícitamente no calibrada. Dos razones por las que importa: la función descrita no existe, y si alguien la agrega, choca con la política declarada de la campaña de que [las correcciones viven en la capa de procesamiento del tablero, no en el firmware](../README.es.md) — las correcciones en firmware no son auditables, las del tablero quedan versionadas. El autocalentamiento que encontró la evaluación es un error real que sí pide una corrección real; su lugar es el pipeline de datos. <!-- TODO: retirar esta afirmación de circulación, o apuntar al código que realmente la implementa. -->

## Evaluación — qué mostró la prueba de campo

El Nodo V2 se puso a funcionar junto a una estación de referencia Smart Citizen Kit. Dos resultados, que apuntan en direcciones opuestas.

**La temperatura lee alto.** La radio Wi-Fi del XIAO ESP32-C3 emite calor de forma continua. Al estar junto al BME680 en un único compartimento cerrado, ese calor conduce a través del plástico y llega al sensor. La temperatura del Nodo V2 quedó muy por encima del clima real fuera de la carcasa. La humedad relativa se equivoca junto con ella: un sensor que está en aire más caliente que el ambiente lee ese aire como más seco de lo que realmente está el aire exterior. El documento original solo reporta el error de temperatura, así que trata la consecuencia sobre la humedad como una inferencia y no como un resultado medido.

**Las partículas llegan tarde.** Poner la toma de aire debajo de la caja restringe la circulación de partículas. Cuando el polvo ambiente se disparó, el Nodo V2 respondió tarde: el aire nuevo entraba despacio por la estrecha rejilla inferior, la línea de tendencia se aplanó y el pico real de contaminación nunca llegó al registro. Para una campaña cuyo argumento entero se apoya en capturar eventos de quema abierta, un nodo que suaviza los picos es peor que uno simplemente ruidoso.

Ninguno de los dos fallos se anuncia. Los dos producen datos de apariencia verosímil. Ese es justamente el motivo de dejarlos escritos.

## Qué tiene que hacer distinto la V3

1. **Admisión por arriba o por los costados abiertos, no por abajo.** La entrada mirando hacia abajo quedó refutada. La V3 vuelve a un recorrido de aire vertical.
2. **Sacar el BME680 del compartimento principal.** Tiene que quedar fuera de la bahía de electrónica, bajo una cúpula de protección solar multilamas (multi-louvered solar radiation shield), para que lea aire ambiente y no el escape del microcontrolador.

Ambas cosas ya están resueltas en [la carcasa piña v5 vigente](../enclosure/), que pone cada ranura de respiración en la sombra de lluvia de una escama y hace correr una chimenea desde una admisión baja a la altura del BME680 hasta un escape alto bajo la tapa. Si la V3 va a ser un diseño nuevo y no la adopción de la v5, esa carpeta es lo primero que hay que leer.

Hay una tercera lección que la evaluación implica sin enunciar: **la compacidad y el aislamiento térmico están en conflicto directo**, y la V2 eligió compacidad sin poner precio a ese intercambio. Una carcasa que aloja una radio y un sensor de temperatura en un mismo volumen cerrado va a informar la temperatura de la radio. O los separas físicamente, o aceptas que el canal de temperatura es diagnóstico y no ambiental — y lo dices en el tablero.

## Archivos

| Qué | Dónde |
|---|---|
| Firmware (compartido con toda la familia de nodos DIY) | [`../firmware/diy_node/`](../firmware/diy_node/) |
| Lista de materiales, legible por máquina | [`bom.csv`](bom.csv) |
| Fotos, renders y diagramas | [`img/`](img/) |
| Archivos de la carcasa Nodo V2 | [Carpeta de Google Drive](https://drive.google.com/file/d/1OdK7mdnLc2XkGRntHOQXK7PGmcP8E4bJ/view?usp=sharing) — **todavía no está en este repo** |
| Artículo de referencia de la estación SCK | [HardwareX 6 (2019)](https://www.sciencedirect.com/science/article/pii/S2468067219300203) |
| Carcasa recomendada actualmente | [`../enclosure/`](../enclosure/) |

## Qué le falta todavía a esta documentación

Dicho sin rodeos, porque quien lea merece saber cuáles son huecos y no descubrirlos frente a la impresora.

- **El archivo CAD fuente no está aquí, y el STL tampoco.** La carcasa vive en una carpeta de Google Drive fuera del repo. Hoy por hoy nadie puede reimprimir esta carcasa desde el repositorio, y si el enlace de Drive se cae, el diseño desaparece. Este es el único hueco realmente bloqueante: [el hardware abierto necesita a la vez la fuente editable y la exportación lista para fabricar](https://open-make.github.io/Hardware-template-guide/), y esta carpeta no tiene ninguna de las dos.
- **No hay parámetros de impresión.** Altura de capa, perímetros, relleno, temperaturas, orientación, soportes, tiempo. La pieza no se puede reproducir de forma consistente sin ellos.
- **No hay dimensiones de la carcasa ni espesor de pared**, así que el diseño no se puede adaptar ni verificar.
- **El código de colores SDA/SCL se contradice a sí mismo** entre la tabla de cableado y la perfboard.
- **La afirmación de la "calibración local"** no tiene código que le corresponda.
- **No hay números medidos de los fallos.** "Lee más caliente" y "llega tarde" son los hallazgos correctos, pero un Δ°C contra el SCK y un retardo en minutos permitirían al siguiente diseño fijarse un objetivo en lugar de una dirección. Si los datos de esa colocación conjunta todavía existen, su lugar es este.
- **Once tornillos sin destino.** La lista compra 15 tornillos M2 × 6; cuatro fijan el HM3301 y el resto no aparece en ningún paso de montaje.
- **No hay notas de reparación ni de disposición final.** Aceptable en esta etapa; obligatorio antes de que alguien llame a este diseño listo para replicar.

Documentado siguiendo la [Open-Make Hardware Template Guide](https://open-make.github.io/Hardware-template-guide/) — Colomb, J. (2025), *Guide and template for hardware project documentation*, Zenodo, [doi:10.5281/zenodo.14725490](https://doi.org/10.5281/zenodo.14725490). Etapa de desarrollo: **prototipado**, evaluado y superado.

## Licencia

MIT, igual que el repositorio principal. La referencia de la estación SCK es obra de sus propios autores, citada arriba. Haz un fork para Making Sense [tu lugar] — y si construyes la V3 que este diseño reclama, devuélvela a una carpeta al lado de esta.
