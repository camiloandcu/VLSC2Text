# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Oyentes que quieren aprender señas básicas de la Lengua de Señas Colombiana (LSC) desde cero: familias, docentes, compañeros, personal de atención. Abren la página en su celular, lo apoyan contra algo a 1 o 2 metros y practican con las dos manos libres. Mientras hacen la seña casi no pueden tocar la pantalla, así que necesitan leerla de lejos.

## Product Purpose

Enseñar y practicar cinco señas de la LSC (Café, Aromática, Hola, ¿Qué necesitas?, Con gusto) con retroalimentación de la cámara. La persona ve cómo se hace cada seña, la intenta y recibe una corrección concreta hasta lograrla. Después hace un repaso mezclado. Éxito: alguien sin conocimientos previos logra las cinco señas y entiende qué corregir cuando falla.

## Positioning

La cámara evalúa el intento en el propio dispositivo con un modelo validado con personas que no vio al entrenar (98,5% en validación por persona). La retroalimentación dice qué corregir (altura de las manos, una o dos manos, encuadre), no solo si acertó.

## Operating Context

- Celular apoyado a distancia, cámara frontal, luz doméstica. Escritorio como caso secundario.
- Presentación pública el 27 nov 2026, ante los demás grupos y el jurado del LatAm IA Challenge.
- Enlace privado por ahora.

## Capabilities and Constraints

- MediaPipe Holistic corre en el navegador; al servidor viaja solo el esqueleto. El video nunca sale del dispositivo.
- Reconoce solo cinco señas aisladas. No es un traductor y no debe presentarse como tal.
- La guía de cada seña es una animación de esqueleto derivada del dataset, sin caras. No se muestran los videos de los firmantes en un enlace compartido (manual del reto, §8.4).
- El encuadre importa: de la cintura hacia arriba y con los codos visibles. Con la cámara demasiado cerca, la accuracy medida cayó de 90% a 82%.
- Si la confianza es menor a 0,7, la app responde «no estoy seguro» en lugar de adivinar.
- Nombre del producto: pendiente de aprobación. Propuesta: «Seña a seña».

## Brand Commitments

Lenguaje cotidiano y cálido. Lo técnico se reduce a una línea de privacidad. Nada de jerga de aprendizaje automático en la experiencia principal.

## Evidence on Hand

- Accuracy del modelo: 98,49% LOSO y 97,99% anidada (docs/07).
- Prueba con cámara propia: 82% con el encuadre cercano y 90% con buen encuadre, en 60 y 30 clips (artifacts/camera_trial).
- No hay testimonios ni validación con personas sordas todavía. Las pistas de cada seña no están validadas por un intérprete: no presentarlas como enseñanza certificada.

## Product Principles

1. Aprender primero, demostrar después: el recorrido enseña; el reconocimiento sirve a la práctica.
2. Una corrección a la vez, accionable y en palabras cotidianas.
3. Legible a dos metros: lo importante se ve sin acercarse al teléfono.
4. Honestidad sobre los límites: cinco señas, no es un traductor, «no estoy seguro» cuando corresponde.
5. Privacidad por diseño: el video no sale del dispositivo.

## Accessibility & Inclusion

Uso con manos ocupadas y a distancia: texto grande, estados visibles por color e ícono, sin depender de tocar durante la seña. Contraste WCAG AA. Respetar `prefers-reduced-motion` en todo lo que no sea la guía misma.
