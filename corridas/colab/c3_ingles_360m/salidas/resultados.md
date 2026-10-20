# Resultados del taller de destilación

| | Antes (base) | Después (destilado) |
|---|---|---|
| Nota media (1–10) | 4.08 | **4.58** |
| Aprobación (≥ 7) | 8% | **0%** |
| Pérdida de entrenamiento | 3.5576 | 2.2604 |

Uso del profesor: 102 llamadas · 16,988 tokens de entrada · 17,711 de salida · ≈ US$ 0.0106

## Ejemplos lado a lado

**Pregunta:** When would fine-tuning make sense for a Chilean retailer, rather than using a general-purpose model with a prompt?

- Referencia del profesor: Fine-tuning makes sense when a retailer needs the same specialized behavior repeatedly and prompts alone are inconsistent—for example, classifying Chilean customer-service cases by local policies, matching products to a house-specific catalog style, or drafting replies in a consistent brand voice. It is most worthwhile when the retailer has many high-quality examples and can measure gains in accuracy, speed, or cost. For changing information such as prices, inventory, and promotions, keep a general model and provide current data through retrieval or tools instead.
- Antes (nota 4): Fine-tuning is more suitable when the retailer needs to leverage specific knowledge or context from their own data that can be easily extracted through training on a smaller dataset compared to a general-purpose model with a prompt.
- Después (nota 3): Fine-tuning is suitable when the retailer has highly relevant product categories or specific customer segments that require personalized guidance—for example, recommending products to customers who have purchased similar items before; setting prices based on sales trends; or providing recommendation

**Pregunta:** Why does a vague prompt often produce generic answers, and how can I make it more specific?

- Referencia del profesor: A vague prompt leaves the AI to guess your goal, audience, context, and preferred level of detail, so it often defaults to broadly applicable answers. Make it specific by stating the task, relevant business context, audience, constraints, and desired format. For example, instead of “Suggest ways to improve sales,” ask: “Recommend three low-cost ways a Chilean retailer can increase online sales this quarter, with expected impact and one KPI for each.”
- Antes (nota 8): A vaguely phrased question like "What is the best way to learn Python?" may lead to generic responses such as "Practice regularly." However, if you provide more context or specificity about what you're looking for (e.g., learning for a project, improving your skills), we can tailor our response acco
- Después (nota 6): A vague prompt usually produces generic answers because they don’t ask the right questions or provide context. To improve them: Ask for clear goals—what do you want to achieve with this text? What audience is your reader? What information should be included? Use relevant examples; avoid general stat

**Pregunta:** How does RAG reduce the risk of AI making up answers, and why can it still produce incorrect or unsupported responses?

- Referencia del profesor: RAG (retrieval-augmented generation) searches trusted documents—such as company policies or product manuals—and gives relevant passages to the AI as context. This makes answers more evidence-based and easier to verify than relying only on the model’s learned patterns. It can still be wrong if the source material is missing, outdated, or contradictory; retrieval finds irrelevant passages; or the model misreads or overstates what the passages say. RAG reduces hallucinations, but does not guarantee accuracy or support.
- Antes (nota 2): Rag reduces the risk of AI making up answers by ensuring that each response is generated based on a set of predefined rules and constraints. This helps to prevent the system from producing false information or providing incorrect answers. Additionally, Rag uses techniques such as data validation and
- Después (nota 3): RAG reduces the risk by checking each answer against a set of approved examples; if it doesn’t match, it rejects the response without storing it. It also checks whether the input is consistent with its knowledge base—for example, asking for information about a product that has been discontinued. How

**Pregunta:** How do AI agents differ from generative AI copilots that suggest content but leave each action to an employee?

- Referencia del profesor: A generative AI copilot drafts or recommends content, while an employee decides what to do and takes each action. An AI agent can pursue a defined goal by planning and completing multiple steps—such as checking inventory, drafting a supplier order, and submitting it—using connected business systems. Agents can act with less ongoing input, so companies need clear permissions, monitoring, and approval rules for consequential actions.
- Antes (nota 3): AI agents can be used as a tool for generating suggestions or ideas without the need of human intervention. They provide recommendations based on data analysis and machine learning algorithms. In contrast, generative AI copilots like those mentioned earlier focus on suggesting content while leaving 
- Después (nota 3): AI agents can automate routine tasks with high accuracy; they don’t have personal preferences or judgment. Generative AI copilots—such as a chatbot suggesting articles for employees without editing them—can improve productivity by freeing staff to focus on more creative work. They should be used onl

**Pregunta:** How could a Chilean retailer use an LLM to help forecast demand or draft product descriptions, and what should employees still review?

- Referencia del profesor: A Chilean retailer could use an LLM to summarize sales, promotions, seasonality, weather, and local events—such as CyberDay or Fiestas Patrias—to help planners estimate demand and flag stock risks. It could also draft product descriptions from approved specifications in clear Spanish. Employees should verify forecasts against sales and inventory data, and check descriptions for factual accuracy, prices, availability, safety or performance claims, brand tone, and compliance before publishing.
- Antes (nota 4): 1. Use an LLM for forecasting: An LLM can be used by the retailer to predict future sales based on historical data and market trends. This information can then be used to inform inventory management decisions, pricing strategies, and marketing campaigns.

2. Draft product descriptions: The retailer 
- Después (nota 5): A Chilean retailer can use an LLM for forecasting sales by analyzing historical data on customer purchases, seasonality, pricing trends, and competitor activity; it may also suggest new products based on unmet needs. Draft product descriptions using the model’s context: include relevant keywords, su
