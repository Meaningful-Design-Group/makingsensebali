[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Carcasas

Alojamientos de exterior para el nodo DIY de calidad del aire de Making Sense Bali. Todo lo
que hay en esta carpeta se ha impreso y desplegado.

> ## Construye [`node-v3.2/`](node-v3.2/).
> Ensamblaje sin tornillos, montaje moldeado en el cuerpo, cinco piezas impresas.
> Fab Lab Bali, septiembre de 2026.

| | |
|---|---|
| [`node-v3.2/`](node-v3.2/) | **Canónico.** Encaje a presión completo sin tornillos, montaje en pared y en poste integrado. Ocho STL publicados, el CAD fuente sigue faltando. |
| [`node-v3.1/`](node-v3.1/) | Reemplazado por la v3.2. El mismo cuerpo ensamblado con 11 tornillos más un soporte de pared aparte. Se conserva porque hay unidades en campo. |
| [`node-v2/`](node-v2/) | Retirado. Construido, desplegado, colocalizado junto a un Smart Citizen Kit y **falló dos veces**. Se conserva por las notas de fallo, que son lo más reutilizable que hay aquí. |
| [`previous-iterations/`](previous-iterations/) | El linaje de carcasas anterior a la V3: v1-box → v2-lantern → v3-gourd → v4-column → v5 pine cone. Retirado, documentado. |
| [`LICENSES/`](LICENSES/) | Hardware CERN-OHL-W-2.0 · Documentación CC-BY-SA-4.0 · Software MIT |

**¿Buscas el trabajo paramétrico de la torre meru?** Ese es un estudio de diseño aparte, sin
imprimir, y vive en [`../enclosure-research/`](../enclosure-research/). Ver
[Dos vías](#dos-vías-y-por-qué-están-separadas) más abajo.

## Nomenclatura

Fab Lab Bali numera generaciones completas de nodo. Este repositorio numeraba antes las
iteraciones de carcasa por separado como `bayu-vN`, lo que producía dos nombres para un
mismo objeto y una colisión con la línea de investigación. **El esquema `bayu-vN` está
retirado.** La correspondencia, para quien lea commits, issues o carpetas de Drive antiguos:

| Carpeta ahora | Antes | Fab Lab Bali lo llama |
|---|---|---|
| `node-v3.2/` | `node-v3.2/` | Node V3.2 |
| `node-v3.1/` | `node-v3.1/` | Node V3.1 |
| `node-v2/` | `node-v2/` | Node V2 |

`node-v3.1/` y Node V3.1 son los mismos seis archivos STL, verificados byte a byte contra la
publicación de Fab Lab Bali — no deducidos de los nombres de archivo.

Ten en cuenta que `previous-iterations/archive/v2-lantern/` **no** es `node-v2/`. El linaje
antiguo de carcasas y las generaciones de nodo pasan ambos por el número 2 y no están
relacionados.

## Dos vías, y por qué están separadas

| | Esta carpeta | [`../enclosure-research/`](../enclosure-research/) |
|---|---|---|
| Origen | Fab Lab Bali | Estudio paramétrico de junio de 2026 |
| Forma | Cuerpo horizontal compacto | Torre meru modular, retícula gyroid |
| Flujo de aire | Entrada por la parte inferior; BME680 junto a la radio | Chimenea: BME680 abajo, XIAO arriba, todas las aberturas hacia abajo |
| Cadena de herramientas | CAD a mano, publicaciones STL | Generadores build123d + Rhino |
| **Impreso** | **Sí — desplegado** | **No. Nada.** |
| Validado térmicamente | No | No |

Ambos sistemas de numeración usan `vN` a secas, y por eso ya no comparten carpeta.

**La posición honesta.** La evaluación en campo del Node V2 produjo dos requisitos: entrada
de aire por arriba o por los lados abiertos, y el BME680 fuera del compartimento de
electrónica y bajo una pantalla. La generación V3 no cumple ninguno de los dos — resuelve un
tercer problema, la reabsorción del aire de salida, con un conducto. La vía de investigación
cumple los dos, en pantalla, sin haberse impreso nunca. Ninguna de las dos vías está
terminada. `node-v3.2/` es canónico porque es el único diseño que cualquiera puede construir
hoy, no porque la cuestión del flujo de aire esté resuelta.

Hasta que una v3.2 no se haya colocalizado junto a un SCK, **trata sus canales de
temperatura y humedad como no verificados y espera que los picos de PM se lean bajos.** Eso
no es motivo para dejar de desplegar — es el motivo por el que la campaña exige una primera
semana de colocalización para cada nodo nuevo.

## Antes de que esto esté listo para replicarse

Ordenado por lo que bloquea la reutilización, no por esfuerzo:

1. **Publicar el CAD fuente de la v3.2** (y de la v3.1). Solo STL significa que nadie fuera
   de Fab Lab Bali puede modificarlo. Esto importa más en la v3.2: cada unión es un encaje a
   presión ajustado, y un gancho en voladizo no se puede reajustar a partir de una sopa de
   triángulos.
2. **Colocalizar una v3.2 junto a un SCK durante una semana** y publicar el Δ°C y el retardo
   de PM. O el cuerpo compacto reproduce los errores de la V2 o no, y nadie lo sabe.
3. **Reexportar `OUTFLOW_DUCT_HM3301.stl`** — 1 borde abierto, 1 triángulo degenerado,
   arrastrados sin cambios desde la v3.1, donde ya estaban señalados.
4. **Parámetros de impresión.** Primero el material: el PLA no sobrevivirá a un techo
   tropical, y en un diseño de encaje a presión la orientación de impresión decide si los
   ganchos sobreviven al montaje.
5. **Costo.** No existe precio para esta construcción en ninguna moneda. Es la primera
   pregunta que hace cada banjar.
6. **Fotografías del montaje.** Todas las imágenes de ambas carpetas son renders CAD.

Los puntos 1 y 2 deciden si otro Fab Lab puede construir esto y confiar en lo que reporta, o
solo está mirando fotos de él.

## CAD del Node V2

`Meaningful-Design-Group/Enclosure-DIY-Node-V2` contiene exactamente un archivo,
`Enclosure DIY Node V2.f3z`, sin README y sin licencia. Responde al propio TODO bloqueante
de la documentación del Node V2:

```bash
git clone https://github.com/Meaningful-Design-Group/Enclosure-DIY-Node-V2 /tmp/v2cad
mkdir -p hardware/diy-node/enclosure/node-v2/cad
cp "/tmp/v2cad/Enclosure DIY Node V2.f3z" hardware/diy-node/enclosure/node-v2/cad/
```

Después, archiva ese repositorio con su descripción apuntando aquí. Un único hogar público por diseño.

## Textos de licencia

Ver [`LICENSES/README.md`](LICENSES/README.md) — dos comandos `curl`. No los transcribas
a mano.
