Вот подробный и эффективный промпт, который превратит нейросеть в профессионального научного редактора. 

Я разделил его на **основной промпт** (который можно просто скопировать) и **дополнительные настройки**, чтобы вы могли адаптировать его под свои нужды.

### Основной промпт (скопируйте и вставьте)

```text
Act as an expert academic editor and a native English speaker with extensive experience in publishing papers in high-impact peer-reviewed journals. 

Your task is to proofread, edit, and improve the following excerpt from a scientific article. 

Please focus on the following aspects:
1. Grammar & Mechanics: Correct all grammatical errors, typos, spelling mistakes, and punctuation issues. Use [American/British] English.
2. Academic Style & Tone: Ensure the tone is formal, objective, and scholarly. Replace informal, vague, or weak vocabulary with precise academic terminology.
3. Clarity & Flow: Rewrite awkward or overly complex sentences to improve readability, logical flow, and coherence without altering the original meaning or scientific data.
4. Conciseness: Eliminate wordiness, redundancies, and fluff.

Output format:
1. First, provide the fully revised and polished version of the text.
2. Second, under the heading "Key Changes & Suggestions", provide a brief bulleted list of the most significant changes you made and explain why (e.g., explaining stylistic rewrites or pointing out unclear logic in the original text).
```

---

### 💡 Советы для получения наилучшего результата:

1. **Укажите вашу научную область:** Нейросеть лучше подберет термины, если будет знать контекст. В начале промпта можно добавить: 
   * *"The article is in the field of [Computer Science / Molecular Biology / Economics]."*
2. **Выберите вариант английского:** В пункте 1 не забудьте оставить только один вариант: **American** (для журналов США) или **British** (для европейских/британских журналов).
3. **Проверяйте по частям:** Не загружайте всю статью целиком (Abstract, Introduction, Methods, Results, Discussion). Нейросети работают гораздо качественнее, если давать им текст кусками по 300–800 слов.
4. **Управление степенью вмешательства:** 
   * Если вам нужно, чтобы ИИ **только исправил ошибки**, но не переписывал ваш авторский стиль, замените пункты 2 и 3 на: *"Do not rewrite the text heavily. Only fix strict grammatical errors, typos, and awkward phrasing. Preserve my original voice."*
   * Если текст написан плохо и нужен **глубокий рерайт**, добавьте: *"Feel free to heavily restructure sentences and paragraphs to achieve a native-level academic flow."*

### Версия промпта на русском (если вы общаетесь с ИИ на русском, хотя для английского текста лучше использовать английский промпт):

> «Действуй как профессиональный англоязычный редактор научных статей с многолетним опытом работы в рецензируемых журналах. Твоя задача — проверить и улучшить текст моей научной статьи на английском языке. 
> 
> Исправь все грамматические ошибки, опечатки и пунктуацию. Улучши академический стиль: замени неформальные слова на научные термины, сделай текст более лаконичным, убери "воду". Перефразируй корявые и неестественные предложения, чтобы текст читался легко и логично, как у носителя языка, но строго сохрани исходный научный смысл. Используй [американский/британский] английский.
> 
> Сначала выдай готовый исправленный текст. Затем напиши список основных изменений с объяснением, почему ты перефразировал те или иные моменты.
> 
> Текст: [ВСТАВИТЬ ТЕКСТ]»