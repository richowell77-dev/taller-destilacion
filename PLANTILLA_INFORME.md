# Informe individual · Taller de destilación en pequeño

**Nombre:** ______________________  **Fecha de entrega:** ____________  **Dominio elegido:** ______________________

> Extensión sugerida: 6 a 10 páginas (sin contar anexos). Entregar como PDF junto con la carpeta del proyecto comprimida
> (`destila.py` modificado, `taller_destilacion.ipynb` ejecutado, `datos/`, `salidas/`). Evita incluir tu `.env`.

## 1. Caso y dominio (Bloque 2)
- Empresa o área (puede ser ficticia) y problema que resolvería un asistente especializado.
- Dominio y temas definidos en `CONFIG` (pega el bloque).
- Por qué un modelo pequeño local tiene sentido aquí (costo, privacidad, latencia) y qué perderías frente a la API.

## 2. Datos del profesor (Bloque 2)
- Cantidad de pares generados, distribución por tema, costo en tokens y USD (`profesor.resumen()`).
- Revisión humana: 10 respuestas del profesor leídas a mano. ¿Cuántas corregirías o descartarías? ¿Por qué?
- Cambios que hiciste a los prompts del profesor (si los hubo) y qué efecto tuvieron.

## 3. Línea base (Bloque 3)
- Nota media y aprobación del estudiante **antes** de entrenar; `resultados.png` de la corrida base.
- Tres respuestas del modelo base comentadas.

## 4. Experimentos (Bloques 3 y 4)
Completa una fila por corrida. Mínimo cuatro corridas, cambiando una sola variable por vez.

| # | Cambio respecto a la anterior | n datos | épocas | lr | r LoRA | Nota antes | Nota después | Aprobación | Tiempo | Observación |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | configuración por defecto | | | | | | | | | |
| 2 | | | | | | | | | | |
| 3 | | | | | | | | | | |
| 4 | | | | | | | | | | |

- Gráfico comparativo de las corridas (nota después por corrida) y curva de pérdida de la mejor.
- ¿Detectaste sobreajuste? Evidencia (pérdida baja y nota estancada, respuestas memorizadas).

## 5. Auditoría del juez (Bloque 4)
- 10 ítems de `salidas/examen_despues.jsonl` calificados por ti con la misma rúbrica (1–10), en una tabla: nota del juez, tu nota, diferencia, comentario.
- Acuerdo juez–humano (p. ej. correlación o % dentro de ±1 punto). ¿Qué sesgos observas? ¿Qué cambiarías en el prompt del juez?

## 6. Modelo final y demostración (Bloque 5)
- Configuración final y resultados (tabla antes/después, por tema).
- Cinco preguntas nuevas, dentro y fuera del dominio, respondidas por el modelo base y el destilado lado a lado.
- Limitaciones observadas (repeticiones, idioma, alucinaciones) y cómo las mitigarías.

## 7. Reflexión (Bloque 5)
Máximo una página: ¿cuándo conviene destilar y cuándo seguir usando la API? Considera costo por consulta, privacidad,
calidad mínima aceptable, mantenimiento del modelo, licencias (términos de OpenAI, Apache 2.0 de SmolLM2) y riesgos.

## Anexos
- Diff o lista de cambios en `destila.py`.
- Registro de problemas técnicos y cómo los resolviste.
- Uso de asistentes de IA en la elaboración del informe (declaración breve).
