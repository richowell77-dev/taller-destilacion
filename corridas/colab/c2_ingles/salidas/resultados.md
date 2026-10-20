# Resultados del taller de destilación

| | Antes (base) | Después (destilado) |
|---|---|---|
| Nota media (1–10) | 2.08 | **2.83** |
| Aprobación (≥ 7) | 0% | **0%** |
| Pérdida de entrenamiento | 3.7904 | 2.9353 |

Uso del profesor: 102 llamadas · 17,032 tokens de entrada · 17,662 de salida · ≈ US$ 0.0105

## Ejemplos lado a lado

**Pregunta:** How can fine-tuning help a Chilean retailer answer customer questions in the company’s brand voice?

- Referencia del profesor: Fine-tuning trains a language model on examples of the retailer’s approved customer replies, helping it match the brand’s tone, phrasing, and service style—for example, sounding warm and concise in Spanish when answering about returns or delivery. It works best for consistent voice and response patterns; current details such as prices, stock, and policies should come from trusted, up-to-date company systems.
- Antes (nota 1): Fine-tuning is a crucial aspect of product development for a Chilean retailer to ensure that their products resonate with customers from around the world. Here's how it could be applied:

1. **Understanding cultural nuances**: A good retailer should have knowledge about local customs, traditions, an
- Después (nota 3): Fine-tune is used to create highly accurate responses for Chileans who ask about products or services that have been tested by other companies—such as health care, home goods, or travel. For example: “What does your product do?” “Does it cost more than another?” “Is there any difference between this

**Pregunta:** What common prompting mistakes cause AI tools to invent facts, and how can our team reduce that risk?

- Referencia del profesor: AI is more likely to invent facts when prompts are vague, contain unverified assumptions, demand certainty, or ask for current details without providing reliable sources. Reduce the risk by supplying approved documents and relevant context, asking the tool to separate facts from assumptions and flag unknowns, and requesting citations to specific sources. Verify important claims against those sources, especially in financial, legal, or customer-facing work. Treat confident wording as no substitute for evidence.
- Antes (nota 3): Common prompting mistakes causing AI tools to invent fact-based information include:

1. **Lack of context**: AI systems often rely on incomplete or inaccurate data sources for their training decisions. This includes missing important details about the topic being discussed, such as relevant definit
- Después (nota 1): Common prompts include:

  • “Generate a sentence from this paragraph.”
  • “Create a new fact about [topic] using the following data—[source], [target]. For example, ‘The average salary for software developers is $105,000.’”
  • “Use a sample of your own words or examples as evidence; verify it aga

**Pregunta:** How do we measure whether a RAG system is retrieving the right documents and giving accurate answers?

- Referencia del profesor: Evaluate retrieval and answers separately using a representative set of questions with expert-verified relevant documents and expected answers. For retrieval, measure Precision@k (how many top results are relevant), Recall@k (whether key documents appear), and ranking quality such as nDCG. For answers, assess correctness against trusted sources, faithfulness (no unsupported claims), completeness, and citation accuracy. Review failures by question type and track results over time—for example, whether a procurement-policy query retrieves the current policy and accurately reports its spending limit.
- Antes (nota 2): Measuring the effectiveness of a RAG system involves evaluating its performance on multiple metrics to ensure that it accurately retrieves relevant information from databases or other sources. Here's how you can assess this:

1. **Document Retrieval Rate**: This measures the percentage of retrieved 
- Después (nota 4): Use metrics such as: accuracy (correctly retrieved data) per query; recall—the percentage of relevant records that match what was asked for—for each document type; precision-recall curve to track how well it detects errors or missing information; false discovery rate by handling duplicate results; a

**Pregunta:** When should a Chilean company choose a simple workflow automation instead of an AI agent?

- Referencia del profesor: Choose simple workflow automation when the task follows stable, explicit rules, inputs are predictable, and every step must be consistent, fast, and easy to audit. For example, a Chilean company can automatically route expense claims by amount and cost center or validate invoice fields before sending them to its accounting system. Use an AI agent when the work involves ambiguous requests, changing context, or judgment that cannot be captured reliably in fixed rules.
- Antes (nota 3): A Chile-based company might consider using a simple workflow automation over an AI agent for several reasons:

1. **Cost savings**: Simple workflows can be more cost-effective than complex ones due to the lower overhead costs associated with implementing and maintaining them.

2. **Scalability**: Co
- Después (nota 5): Use a simple workflow for routine tasks or customer-facing processes when:

  • It’s easy to automate;
  • You have limited control over the process;
  • The task is repetitive or time-consuming;
  • You want human oversight without requiring high accuracy.
For example, use a simple workflow with cl

**Pregunta:** How do retrieval-augmented generation and fine-tuning differ for answering questions about our company’s internal documents?

- Referencia del profesor: Retrieval-augmented generation (RAG) searches approved internal documents when a question is asked, then uses relevant passages to answer. It is usually better for current company facts because documents can be updated without retraining, and answers can cite sources. Fine-tuning trains the model on examples to improve behavior, format, or domain-specific language; it does not reliably give it access to changing documents. For questions about policies, contracts, or sales figures, use RAG; consider fine-tuning for consistent response style.
- Antes (nota 2): Retrieval-augmented generation (RAG) is a technique used to generate new content based on existing data or information that has been previously retrieved from various sources such as databases, APIs, or external repositories like Google Cloud Platform's Cloud Storage Service. In the context of your 
- Después (nota 2): Retrieval-augmented generation is a more flexible approach that uses the current version of your document to generate new content; it can handle incomplete or outdated information without changing its meaning. Fine-tuning involves adjusting each sentence based on context, tone, and relevant facts—fo
