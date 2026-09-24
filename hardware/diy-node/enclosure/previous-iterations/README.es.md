[English](README.md) · [Bahasa Indonesia](README.id.md) · **Español**

# Iteraciones anteriores

Diseños de carcasa retirados, conservados porque los fallos son el conocimiento más
reutilizable de este repositorio. Los requisitos de
[`../node-v3.2/`](../node-v3.2/) existen porque uno de estos diseños los enseñó.

> **Ninguno de estos es el diseño actual.** Construye [`../node-v3.2/`](../node-v3.2/).

| Iteración | Qué era | Retirado porque |
|---|---|---|
| [v5 "pine cone"](README.v5-and-earlier.es.md) | Cascarón paramétrico en OpenSCAD, diez hojas superpuestas; el desvío de la lluvia y la ventilación eran la misma geometría. Fuente: [`enclosure.scad`](enclosure.scad) · STL en [`stl/`](stl/) · renders en [`img/`](img/) | Reemplazado por la línea Fab Lab Bali V3, que es lo que Fab Lab Bali construye y despliega realmente. La v5 resolvía el encargo del flujo de aire de forma más convincente que la V3 — ver la nota más abajo. |
| [`archive/`](archive/) — v1-box, v2-lantern, v3-gourd, v4-column | Cuatro formas anteriores, cada una con sus propias notas | Cada una reemplazada por la siguiente; conservadas como registro de lo que se intentó |

**Node V2 no está aquí.** Vive en [`../node-v2/`](../node-v2/), hermana del diseño
actual, porque es una generación de *node* y no una iteración de carcasa, y porque
su evaluación de campo sigue siendo el documento más citado de este árbol.

## La nota de la v5 que conviene conservar

La v5 puso cada ranura de respiración en la sombra de lluvia de una escama e hizo correr una
chimenea desde una toma baja a la altura del BME680 hasta una salida alta bajo la tapa. Esa es
exactamente la topología de flujo de aire que pedía la co-ubicación del Node V2, y la línea V3
— que reemplaza a la v5 — **no** la mantiene: la V3 conserva una toma en la cara inferior y
deja el BME680 junto a la radio.

Así que la v5 está retirada por buenas razones (no es lo que construye Fab Lab Bali, y tampoco
llegó nunca a co-ubicarse), pero no es sin más peor que lo que la reemplazó. Quien retome el
problema del flujo de aire debería leer [`README.v5-and-earlier.es.md`](README.v5-and-earlier.es.md)
y [`../../enclosure-research/DESIGN_LOG.md`](../../enclosure-research/DESIGN_LOG.md)
antes de empezar desde cero.

## Nomenclatura

Por esta carpeta pasan dos conteos sin relación entre sí.

- **La línea de carcasas**, a la que pertenecen `archive/` y la v5:
  v1-box → v2-lantern → v3-gourd → v4-column → v5 "pine cone". Se detiene en la v5.
  Los diseños posteriores de este repo se numeraron brevemente `bayu-v6` y `bayu-v7`; ese
  esquema está retirado y esas carpetas son ahora [`../node-v3.1/`](../node-v3.1/) y
  [`../node-v3.2/`](../node-v3.2/). La tabla de equivalencias está en [`../README.es.md`](../README.es.md).
- **Las generaciones de node de Fab Lab Bali**: Node V1 → V2 → V3.1 → V3.2. Una vía
  aparte que comparte electrónica y firmware.

No leas `archive/v2-lantern/` y [`../node-v2/`](../node-v2/) como la misma generación.
Comparten un número y nada más.
