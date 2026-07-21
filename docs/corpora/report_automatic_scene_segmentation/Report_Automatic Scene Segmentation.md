# Automatic Scene Segmentation in Narrative Texts

## Report in the Context of the EmoEvent-Project

### Overview / Purpose

This report stands in the context of our CHR-conference submission *EmoEvent: *xxx. It gives full details on our applied Gemini-pipeline focused on automatically and semantically segmenting literary texts into narrative scenes. Overall, we follow the the LLM-based approach evaluated by Zehe et al. (2025). By using human-labelled texts from our close-reading approach, Gemini’s performance on the mentioned task is evaluated. In the end, we segment texts from our distant-reading approach by using Gemini.

### Data Description

We use texts two from our close-reading approach: *Das Erdbeben in Chili *by Heinrich von Kleist (1807) and *Die Gänsemagd*, a fairy tale of the Brothers Grimm’s Household Fairy Tales (edition from XXXX).

For Kleist’s text, we reused manual scene annotations created in the context of the GermAn Prose dataset (Hatzel et al. 2026). For the fairy tale, we used the same annotation guidelines and collected the respective annotation data.

| Text | Sentences | Scenes | Scene Rate |
|------|-----------|--------|------------|
| Das Erdbeben in Chili | 71 | 7 | 9.9% |
| Die Gänsemagd | 245 | 14 | 5.7% |
| **Both together** | **316** | **21** | **6.7%** |

Our distant-reading approach reuses the dProse-dataset (Gius et al. 2020). From this corpus, we created a subsample of 327 texts with approximately the same length. Overall, our dProse-sample comprises 120,369 sentences.

### Task Definition

*Binary labelling task for sentences, related to Zehe et al. (1-2 Sents)*

*Scene definition goes back to Gius et al. (evtl. look up in Zehe paper) (2 Sents)*

### Model Selection and Evaluation

In their paper, Zehe et al. (2025) pursue and compare two approaches: one with LLMs, the other with traditional Machine Learning (ML)-techniques. While, in their setting, the ML-approach achieved better results, we decided to move on with current LLMs, mainly due to the missing availability of respective training data.

To decide which LLM to use, we compared different state-of-the-art LLMs such as Gemini 2.5 Pro or Claude Opus 4 and experimented with varying settings, e.g. considering the reasoning-mode (see below).

Based on the prompt specified by Zehe et al., we used the following prompt:

![](Report_Automatic_Scene_Segmentation_assets/image_1.png)

*Quickly explain what is different to Zehe et al and why (2-3 Sents?)*

*Add one note to the context sizes, temperature and whatever is important here (1 Sent)*

Finally, to evaluate the models’ results, we report …

*🡪Quickly explain the used metrics: exact and relaxed F1-Score (in line with Zehe et al.) (1-2 Sents)*

We considered our two texts – Das Erdbeben in Chili and Die Gänsemagd – as gold standard. The following table presents the results of the different models’ overall performance:

| Rank | Model | Reasoning mode | Exact F1 (tol0) | Relaxed F1 (tol3) |
|------|-------|----------------|-----------------|-------------------|
| 1 | Gemini 2.5 Pro | On | **0.50** | **0.76** |
| 2 | Gemini 2.5 Pro | Low | 0.49 | 0.72 |
| 3 | Claude Opus 4 | Off | 0.44 | 0.61 |
| 4 | GPT-4.1 | Off | 0.42 | 0.62 |
| 5 | Claude Sonnet 4 | Off | 0.35 | 0.50 |

Given that our best combination exceeds not only Zehe et al.’s reported relaxed F1-score of 0.45 (with gpt-4o) for their LLM-approach, but also the relaxed F1-score of 0.68 for the ML-approach, we consider the results to be sufficient and decided to move on with Gemini 2.5 Pro with reasoning mode.

### Application to dProse-Dataset

*Write 1 to 2 sentences on the application to dProse (mention i.e. the overall costs and batch-processing, evtl. the overall runtime – or whatever you deem relevant) (1-2 Sents)*

*Mention corpus stats: scene share, median scene length (1 Sent)*

To verify that Gemini’s segmentation approximates our preceding analyses with the other two texts, we took random samples from dProse and checked the annotations manually for plausibility.

### Final Remarks

Write something on potential optimization approaches (e.g. post-processing by rules such as “do not allow consecutive borders”) and pick up the observation of over-segmentation which becomes also visible in the corpus stats *(2-3 Sents)*

Eventually: back-ref to Zehe paper. Just in case, they write something relevant *(1 Sent)*

Mention our reflections on A. there are indeed some REAL false positive borders and B. there are also some “false positive” borders where we could still understand the model’s choice. -> model seems to be more fine-grained *(2 Sents)*
