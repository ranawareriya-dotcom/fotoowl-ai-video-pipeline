"""
Style guide documents for the RAG store.

Chunking strategy: ONE CHUNK PER (style, facet) PAIR, not per-style-monolith.
A single "cinematic" document covering pacing+color+captions+transitions all
at once would force the retriever to return one giant blob even when the
Storyboard Writer only needs the transition guidance. Splitting by facet
means retrieval is precise: querying "cinematic transitions" returns just
that chunk, not 400 words of unrelated caption-tone advice. Each chunk is
still self-contained (repeats the style name) so it makes sense in isolation
when retrieved without its siblings.
"""

STYLE_GUIDE_DOCS = [
    # --- cinematic ---
    {"id": "style_cinematic_pacing", "style": "cinematic", "facet": "pacing",
     "text": "Cinematic style pacing: scenes hold for 3-6 seconds each, favor slow "
             "Ken Burns zooms over hard cuts, allow silence/negative space between "
             "emotional beats rather than rushing to the next image."},
    {"id": "style_cinematic_captions", "style": "cinematic", "facet": "caption_tone",
     "text": "Cinematic style captions: short, understated, poetic fragments rather "
             "than full sentences. Avoid exclamation marks. Think film subtitle, not "
             "social media caption. Example: 'the quiet before' rather than 'Amazing moment!!'"},
    {"id": "style_cinematic_transitions", "style": "cinematic", "facet": "transitions",
     "text": "Cinematic style transitions: crossfades and slow dissolves only. No "
             "slide/wipe transitions - they read as corporate/PowerPoint, breaking "
             "the emotional tone."},
    {"id": "style_cinematic_color", "style": "cinematic", "facet": "color",
     "text": "Cinematic style color treatment: warm, slightly desaturated grade. "
             "Prefer images with warm dominant colors (amber, warm white, soft gold) "
             "when selecting the subset for the reel."},

    # --- upbeat ---
    {"id": "style_upbeat_pacing", "style": "upbeat", "facet": "pacing",
     "text": "Upbeat style pacing: fast cuts, 1-2 seconds per scene, rhythmic and "
             "energetic. Use more scenes total to keep momentum rather than lingering."},
    {"id": "style_upbeat_captions", "style": "upbeat", "facet": "caption_tone",
     "text": "Upbeat style captions: bold, punchy, exclamatory. Short punchy phrases "
             "with energy - 'Let's go!', 'Best day ever'. Emoji-adjacent tone is fine."},
    {"id": "style_upbeat_transitions", "style": "upbeat", "facet": "transitions",
     "text": "Upbeat style transitions: hard cuts and quick zoom transitions. Avoid slow "
             "crossfades - they kill momentum."},
    {"id": "style_upbeat_color", "style": "upbeat", "facet": "color",
     "text": "Upbeat style color treatment: bright, saturated, high contrast. Prefer "
             "images with vivid dominant colors when selecting the subset."},

    # --- corporate ---
    {"id": "style_corporate_pacing", "style": "corporate", "facet": "pacing",
     "text": "Corporate style pacing: moderate, even pacing, 3-4 seconds per scene, "
             "consistent rhythm throughout - no dramatic speed-ups or slow-downs."},
    {"id": "style_corporate_captions", "style": "corporate", "facet": "caption_tone",
     "text": "Corporate style captions: professional, factual, complete sentences. "
             "State names/roles/context plainly. No slang, no exclamation marks."},
    {"id": "style_corporate_transitions", "style": "corporate", "facet": "transitions",
     "text": "Corporate style transitions: subtle slide or fade transitions, consistent "
             "throughout the whole reel. Consistency matters more than variety here."},
    {"id": "style_corporate_color", "style": "corporate", "facet": "color",
     "text": "Corporate style color treatment: neutral, clean, minimal grading. Prefer "
             "well-lit, evenly composed images; deprioritize candid/blurry shots."},

    # --- minimal (fallback / general) ---
    {"id": "style_minimal_captions", "style": "minimal", "facet": "caption_tone",
     "text": "Minimal caption style: use captions sparingly or not at all. When used, "
             "keep to 2-4 words maximum, let the imagery carry the narrative."},
]
