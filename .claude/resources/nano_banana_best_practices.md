# Nano Banana (Gemini Image Generation) - Best Practices

## Model Overview

**Two Tiers:**
- **Gemini 2.5 Flash Image**: $0.039/image, 1024px, optimized for speed (~22 sec), 500 free daily requests
- **Nano Banana Pro (Gemini 3 Pro)**: Up to 4K, Google Search grounding, professional-grade (released Nov 20, 2025)

**Core Strengths:**
- Best-in-class text rendering (logos, infographics, diagrams)
- Conversational editing (iterative refinement through follow-ups)
- Character/brand consistency across multiple generations
- 10x cheaper than competitors with fast generation

**Limitations:**
- Fonts can be inconsistent (requires iteration)
- Over-smoothing on detailed elements
- Weaker artistic stylization vs Midjourney
- Complex typography struggles

## Optimal Use Cases

✅ **Perfect For:**
- Infographics and social media carousels
- Product mockups and marketing materials
- Diagrams and technical documentation
- Business graphics requiring readable text
- High-volume production workflows
- Mobile-optimized content

❌ **Not Ideal For:**
- Hyper-realistic artistic photography
- Complex typography with multiple custom fonts
- Fine detail preservation in technical renders

## Prompt Engineering Best Practices

### 1. Structure: Narrative Over Keywords
**DO:** Write descriptive paragraphs
```
Create a LinkedIn carousel post image with a gradient background transitioning
from soft pale red at the top to white at the bottom. The main title should be
very large, occupying 60% of the frame, centered, with specific words highlighted
in bright red for emphasis.
```

**DON'T:** Use keyword lists
```
LinkedIn post, gradient, red, white, large text, centered
```

### 2. Be Hyper-Specific
- **Colors**: Use descriptive names (soft pale red, bright red) instead of hex codes
- **Typography**: Specify size relationships (VERY LARGE = 60-80% of frame, medium, small)
- **Layout**: Define positioning (center-positioned, top right corner, below title)
- **Composition**: Include negative space, overlay effects, readability optimization

### 3. Positive Framing
**DO:** "Make text very large and bold for mobile readability"
**DON'T:** "Don't make text too small"

### 4. Include Visual Context
- Camera angle/perspective (if relevant)
- Lighting style (professional, clean, high contrast)
- Design aesthetic (minimal, tech, modern, professional)
- Target medium (LinkedIn post, Instagram carousel, mobile-optimized)

### 5. Leverage Multi-Turn Refinement
Generate → Review → Request specific changes in follow-up prompts:
- "Make the title text 20% larger"
- "Shift the gradient to start higher in the frame"
- "Increase contrast on the accent color"

## Text-Heavy Design Best Practices

### Infographics & Carousels
- **Text hierarchy**: Define 3-4 clear size levels (VERY LARGE title, medium subtitle, small annotations)
- **Contrast**: Specify high contrast between text and background
- **Spacing**: Request "plenty of negative space" and "clean minimal design"
- **Overlays**: Use semi-transparent overlays behind text for readability
- **Mobile optimization**: Explicitly request "optimized for mobile readability"

### Sequential Content (Carousel Series)
- **Numbering**: Place slide numbers consistently (e.g., "top right corner: '1/10'")
- **Brand consistency**: Reference the same color palette, fonts, layout in all prompts
- **Template approach**: Create one successful slide, then replicate structure with new content

### Typography
- **Font specification**: Name specific fonts (DM Sans, Arial, Helvetica)
- **Weight**: Specify bold (700), semi-bold (600), regular (400)
- **Size dominance**: State percentage of frame (title occupies 60%, subtitle 20%, etc.)
- **Color highlights**: Specify which words/numbers to emphasize ("Make '95%' and 'FAIL' in bright red")

## Workflow Optimization

### Batch Generation
- Maintain consistent prompt structure across series
- Use descriptive file naming (`slide_01_title.png`, `slide_02_paradox.png`)
- Generate all at once to ensure brand consistency
- Review batch, then iterate on outliers

### Quality Control
1. **Generate** with detailed prompt
2. **Review** at mobile preview size (how users will see it)
3. **Iterate** with specific refinement requests
4. **Validate** text readability on small screens

### Cost Management
- Gemini 2.5 Flash: $0.039/image (use for most work)
- 500 free daily requests on Flash tier
- Reserve Pro tier for final deliverables requiring 4K

## Common Pitfalls & Fixes

| Issue | Solution |
|-------|----------|
| Text too small on mobile | Explicitly request "VERY LARGE text occupying 60-80% of frame" |
| Inconsistent fonts | Specify font name, weight, and size relationships clearly |
| Low contrast | Request "high contrast" and use color overlays behind text |
| Cluttered design | Request "clean minimal design with plenty of negative space" |
| Color inaccuracy | Use descriptive color names consistently across all prompts |
| Over-smoothing | Iterate with "preserve sharp edges on text and graphics" |

## Example Prompt Template

```
Create a [format] with [background description].

SLIDE NUMBER (position): '[number]' in [size] text

MAIN TITLE (size, positioning):
'[title text]'
Make '[specific words]' in [color], rest in [color]

SUBTITLE (size, positioning):
'[subtitle text]'
In [color]

BOTTOM TEXT (size, positioning):
'[reference text]'
In [color]

Use [font name], [weight], [design aesthetic],
[layout details], [special effects], optimized for [medium].
```

## Competitive Positioning

**Choose Gemini When:**
- Need readable text in images
- Producing high-volume content
- Cost-efficiency matters
- Speed is important
- Business/professional aesthetic

**Choose Midjourney When:**
- Hyper-realistic artistic quality needed
- Photography-style imagery
- Artistic stylization priority

**Choose DALL-E 3 When:**
- Complex prompt fidelity required
- Rich style variation needed
- Advanced editing capabilities necessary

## Resources

- **Official Documentation**: Google AI Studio (aistudio.google.com)
- **API Access**: Gemini API via Google Cloud
- **Pricing**: $0.039/image (Flash), tier-based for Pro
- **Daily Limits**: 500 free requests (Flash tier)

---

*Last Updated: November 21, 2025*
*Based on research across 12 sources including official documentation, user feedback, and comparative analysis*