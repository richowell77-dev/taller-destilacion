# Resultados del taller de destilación

| | Antes (base) | Después (destilado) |
|---|---|---|
| Nota media (1–10) | 1 | **1.08** |
| Aprobación (≥ 7) | 0% | **0%** |
| Pérdida de entrenamiento | 3.147 | 2.6524 |

Uso del profesor: 102 llamadas · 16,888 tokens de entrada · 16,141 de salida · ≈ US$ 0.0098

## Ejemplos lado a lado

**Pregunta:** ¿En qué casos le conviene a una empresa chilena ajustar finamente un modelo en vez de usar instrucciones detalladas o RAG?

- Referencia del profesor: Conviene ajustar finamente cuando la empresa necesita un comportamiento consistente y repetible que las instrucciones no logran sostener: clasificar reclamos con criterios propios, redactar respuestas con un tono específico o extraer datos siempre en el mismo formato. Es más atractivo si existen muchos ejemplos representativos y el uso es frecuente, por posibles mejoras de calidad, velocidad o costo. No es la mejor opción para incorporar información que cambia seguido: para tarifas, políticas o normativa vigente, suele convenir RAG. Si la tarea es simple, pruebe primero con instrucciones.
- Antes (nota 1): Espero que la empresa no pueden ser más informada sobre las opciones para realizarse el procesamiento de estas maneras:

1. **Introducción**: La empresa puede ayudarte al usuario con una introducción de la capacidad de la entrada del modelo.

2. **Preguntas**: La empresa puede ayudarte al usuario co
- Después (nota 1): La empresa puede revisarlas por el tercer lado del documento; seleciona las fuentes que están disponibles para verificación y consulta con datos actualizados. Para mantener la información correcta, vuelva a recomendar los resultados finales después de su ejecución. Por ejemplo, si no hay datos previ

**Pregunta:** ¿Cómo diseñar un prompt para que un asistente interno responda consultas sobre políticas de recursos humanos usando documentos de la empresa?

- Referencia del profesor: Define el rol y alcance: responder solo sobre políticas de RR. HH. usando los documentos internos entregados. Indica que debe priorizar la versión vigente, citar el nombre del documento y la sección, y distinguir entre información explícita e inferencias. Si no encuentra respaldo, hay contradicciones o la consulta requiere una decisión, debe decirlo y derivar a RR. HH., sin inventar. Incluye reglas de privacidad: no revelar datos personales ni información ajena a la consulta. Prueba el prompt con preguntas frecuentes, casos ambiguos y políticas desactualizadas.
- Antes (nota 1): En este caso, se pueden creer con una manera más eficiente: utilizan el cualquiera de las siguientes modalidades para escribir los comentarios algo o medio a través del prompt:

1. **El primer comentario**: La primera vez que le dice "el primer comentario" no podría ser mal nuevo, ya que también hay
- Después (nota 1): Pueden crear una información con datos o respuestas aplicables: preguntes por el cliente; resultados del proceso; pruebas ejemplares; tareas actualizadas; calidad y costo de los procedimientos; contratos reales; etiquetas y modalidades; cambios externos; resumen y retención. En estrategias de seguri

**Pregunta:** ¿Qué costos y recursos debería considerar una empresa antes de implementar RAG en sus operaciones?

- Referencia del profesor: Considere costos de modelos (API o infraestructura propia), embeddings, base de datos vectorial, almacenamiento y procesamiento de documentos; además de integración con sistemas, seguridad, control de acceso y cumplimiento de privacidad. Presupueste preparación y actualización de datos, evaluación de respuestas, monitoreo, soporte y consumo variable según uso. Necesitará especialistas en datos, desarrollo, seguridad y áreas de negocio, además de tiempo para probar y ajustar. Por ejemplo, una empresa con contratos desordenados deberá digitalizarlos, depurarlos y definir quién puede consultar cada documento.
- Antes (nota 1): La empresa que se desea implementar la rica entrada de la riqueza de la economia está disponible como el "Rag" (Regula de Salud). Establece las opciones de creación e iniciatas para hacerlo ahora:

1. Creación de línea: La empresa puede crear un lugar con una capacidad más grande del lado anterior, 
- Después (nota 1): El rango de dato: 10% para el modelo (establece la información a partir del sistema) o más sobre los resultados; dependiendo de las entregas y suficientemente pruebas. La respuesta: "La empresa no requiere que sean todos los datos correctamente." Completa consultas con cambios y revisarlos por medid

**Pregunta:** ¿Qué diferencia hay entre usar un agente de IA en la nube y ejecutarlo dentro de la infraestructura de la empresa?

- Referencia del profesor: En la nube, el proveedor opera la infraestructura: suele ser más rápido de implementar y escalar, pero los datos se procesan fuera de la empresa y hay dependencia de conectividad y proveedor. Dentro de la infraestructura propia, la empresa mantiene mayor control sobre datos, seguridad y cumplimiento, pero debe asumir costos de equipos, operación y actualización. Por ejemplo, un chatbot de ventas puede partir en la nube; un agente que consulta datos financieros sensibles podría requerir operación interna.
- Antes (nota 1): El mismo que se hace ahora: "La infraestructuración del empresa" (the structure of the organization). En este caso, el agente de IA no puede ser una cosa más importante para hacerlo. Estos códigos son las siguientes:

1. **Inventory**: El agente de IA lo ayudará al gobierno con los servicios y benef
- Después (nota 1): Un agente de IA no puede ser una fuente o ajustante; su código ya existe, pero el resultado se encuentra por medio del sistema. Por ejemplo, si un agente está utilizando una base de datos para verificar información, también pueden tener respaldo con los datos actuales. Sin embargo, el agente no tien

**Pregunta:** ¿Qué diferencia hay entre usar un LLM general y conectarlo a documentos internos mediante generación aumentada por recuperación (RAG)?

- Referencia del profesor: Un LLM general responde con conocimientos aprendidos durante su entrenamiento, que pueden no incluir información interna o actualizada de la empresa. Con RAG, antes de responder, busca documentos internos relevantes y los usa como contexto; por ejemplo, puede contestar sobre políticas de beneficios o procedimientos vigentes. Esto mejora la pertinencia y permite indicar fuentes, sin reentrenar el modelo. Aun así, puede equivocarse y requiere controles de acceso y calidad documental.
- Antes (nota 1): El diferencio entre usando un LLM general y conectarlo a documentos internos mediante generación aumentada por recuperación (RAG) ha sido claramente desafícil para los estudantes que han acercado el llamado.

En la primera parte, el LLM general puede ser utilizado como una oportunidad para crecer nu
- Después (nota 1): Un LLM general puede ser utilizado para el contrato o la respuesta que se requiere; no permite verificar datos más complexas. Por ejemplo, si una persona consulta informaciones comunes al cliente, ya queda fuera del documento, podríamos revisar su resumen antes de retirar los resultados. Concurso RA
