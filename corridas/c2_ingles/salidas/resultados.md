# Resultados del taller de destilación

| | Antes (base) | Después (destilado) |
|---|---|---|
| Nota media (1–10) | 2.33 | **2.5** |
| Aprobación (≥ 7) | 0% | **0%** |
| Pérdida de entrenamiento | 3.8173 | 2.902 |

Uso del profesor: 102 llamadas · 17,128 tokens de entrada · 18,059 de salida · ≈ US$ 0.0107

## Ejemplos lado a lado

**Pregunta:** How does fine-tuning compare with retrieval-augmented generation for answering questions about our company’s policies and products?

- Referencia del profesor: Fine-tuning teaches a model how to respond—such as using your company’s tone or following a specific workflow—but it is not the best way to keep policy and product facts current. Retrieval-augmented generation (RAG) searches approved company documents at question time and uses them to answer, making updates easier and answers easier to verify. For questions like “What is our return policy?”, RAG is usually the better choice. Fine-tuning can complement it when you also need consistent language or task behavior.
- Antes (nota 2): Fine-tuning is a technique used to improve the accuracy of responses by adjusting parameters or features that influence how well they capture relevant information from the user's input data. In contrast, retrieval-augmented generation (RAG) focuses on generating answers based solely on existing know
- Después (nota 2): Fine-tuning is a way to test the accuracy of answers against actual responses—for example, asking whether a policy will be enforced by law or not; then retraining it on new examples that match those rules. Retrieval-augmented generation can answer more complex queries but may require human review be

**Pregunta:** What are common prompt-writing mistakes that lead to vague, inaccurate, or overly confident answers?

- Referencia del profesor: Common mistakes include giving a vague task (“analyze our performance”) without defining the goal, audience, or success criteria; omitting key context such as market, time period, or source data; combining too many requests; using ambiguous terms; and failing to specify the desired format. Asking for current facts without providing sources can invite fabricated details. Leading questions, or demanding certainty when evidence is limited, can produce biased or overconfident answers. State assumptions, request evidence, and ask the model to flag uncertainty.
- Antes (nota 3): When it comes to writing a response for a user's query, there are several common pitfalls that can lead to unclear, inaccurate, or overly confident responses:

1. **Lack of specificity**: Providing too much information upfront without specifying the purpose or scope is crucial. Users often ask about
- Después (nota 4): Common mistake: Using a question as the sole basis for a response without checking its accuracy; using it only when asked—not enough context is needed; providing too much detail but not sufficient information; failing to test assumptions before testing results; including irrelevant details unless th

**Pregunta:** How do we measure whether a RAG system is retrieving the right information and giving reliable answers, rather than just sounding convincing?

- Referencia del profesor: Build a test set of real business questions with verified answers and source documents. Measure retrieval precision and recall: did the system find the right evidence, without burying it in irrelevant results? Score answer correctness, factual support by retrieved sources, and citation accuracy separately. Test whether it abstains when evidence is missing or conflicting. Have domain experts review edge cases, then monitor these measures and user-reported errors in production. Track task outcomes, not fluency: a polished answer without verifiable evidence is a failure.
- Antes (nota 2): Measuring the effectiveness of a RAG system can be challenging due to its subjective nature. However, there are several methods that can help evaluate the accuracy and reliability of a RAG system:

1. **Data quality checks**: Verify if the data used for training the model has been properly cleaned, 
- Después (nota 3): Use metrics such as accuracy (the percentage of relevant data retrieved), relevance—whether it’s useful for what you need to answer, consistency across sources, and human review)—and reliability: check that retrieval times match expected usage; don’t rely on vague or unsupported claims; test against

**Pregunta:** Can an AI agent reliably handle supplier invoices and purchase approvals, or should a human review every decision?

- Referencia del profesor: An AI agent can reliably automate routine checks—such as matching invoices to purchase orders, validating amounts and flagging missing information—if it uses approved systems, clear rules and audit logs. A human need not review every low-risk match. Escalate exceptions, high-value purchases, new suppliers, bank-detail changes and policy overrides for human approval. Keep approval limits and separation of duties in place, and regularly sample decisions to catch errors or drift.
- Antes (nota 3): An AI agent can be trained to perform various tasks such as invoice processing, order approval, payment handling, etc., but it cannot directly manage the actual process of receiving payments from suppliers due to its lack of knowledge about these processes. Therefore, humans would need to manually v
- Después (nota 3): An agent can process invoice receipts but cannot verify the accuracy of sales data; approve purchases only when approved by authorized parties—typically customers who have valid contracts with the vendor. Human reviewers check compliance, such as payment terms, delivery dates, and return policies. F

**Pregunta:** Can an LLM understand a customer’s intent, or is it mainly matching patterns in language? What does that distinction mean for a bank in Chile?

- Referencia del profesor: An LLM can often infer a customer’s likely intent from context, but it does so through learned language patterns—not human understanding. It can misread Chilean expressions, ambiguous requests, or unusual cases. For a Chilean bank, this makes it useful for routing queries, summarizing requests, or drafting answers, but risky as the sole decision-maker for credit, fraud, or complaints. Use local testing, privacy safeguards, clear escalation to staff, and human review for consequential decisions.
- Antes (nota 1): An LLM (Licensed to Lend) can only match the pattern of words used by customers when they refer to their account balance with another company. It doesn't have any knowledge about the context or meaning behind those terms; instead, it relies on linguistic similarity based solely on word frequency. Th
- Después (nota 2): An LLM can recognize the context of what customers say—whether they need help with something like checking account balances or making payments; whether their answer matches what someone else might ask (e.g., “Do you have any questions?”); how often they will hear from them; when they may be asked ag
