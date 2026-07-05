"""
Remotion API reference documents for the RAG store.

Chunking strategy: ONE CHUNK PER COMPONENT/FUNCTION, each a runnable
self-contained snippet plus a one-line description. Unlike prose style
guides, code references should NEVER be split mid-snippet (a chunk that
cuts off a JSX block is worse than useless - it teaches the model broken
syntax). So chunk boundaries = component boundaries, always whole and
compilable in isolation. Each entry is tagged with the error_types it's
useful for, so the Compiler & Fixer can retrieve by error type on retry.
"""

REMOTION_SNIPPETS = [
    {"id": "remotion_sequence", "topic": "Sequence", "error_types": ["timing", "missing_import"],
     "text": "Sequence controls when a child renders, in frames. "
             "import {Sequence} from 'remotion'; "
             "<Sequence from={30} durationInFrames={90}><Scene/></Sequence> "
             "renders Scene starting at frame 30 for 90 frames."},

    {"id": "remotion_ken_burns", "topic": "Ken Burns zoom (useCurrentFrame + interpolate)",
     "error_types": ["remotion_api", "type"],
     "text": "Ken Burns zoom effect: "
             "import {useCurrentFrame, interpolate, Img} from 'remotion'; "
             "const frame = useCurrentFrame(); "
             "const scale = interpolate(frame, [0, 90], [1, 1.15], {extrapolateRight: 'clamp'}); "
             "<Img src={imgSrc} style={{transform: `scale(${scale})`}} />"},

    {"id": "remotion_crossfade", "topic": "Crossfade between two scenes",
     "error_types": ["remotion_api", "timing"],
     "text": "Crossfade using opacity interpolation across an overlap window: "
             "const opacity = interpolate(frame, [start, start+15], [0, 1], "
             "{extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}); "
             "apply to the incoming scene's style.opacity while the outgoing scene "
             "fades from 1 to 0 over the same window."},

    {"id": "remotion_caption_text", "topic": "Caption/text overlay with AbsoluteFill",
     "error_types": ["remotion_api", "syntax"],
     "text": "Text captions use AbsoluteFill for full-frame positioning: "
             "import {AbsoluteFill} from 'remotion'; "
             "<AbsoluteFill style={{justifyContent:'flex-end', alignItems:'center', "
             "paddingBottom: 80}}><div style={{color:'white', fontSize:48}}>"
             "{caption}</div></AbsoluteFill>"},

    {"id": "remotion_composition_registration", "topic": "Registering a Composition",
     "error_types": ["missing_import", "remotion_api"],
     "text": "Every Remotion project registers compositions in an entry file: "
             "import {Composition} from 'remotion'; "
             "export const RemotionRoot = () => (<><Composition id='FotoOwlReel' "
             "component={FotoOwlReel} durationInFrames={900} fps={30} width={1080} "
             "height={1920} /></>); the id must match what render.ts passes to "
             "selectComposition/renderMedia."},

    {"id": "remotion_slide_transition", "topic": "Slide transition using translateX",
     "error_types": ["remotion_api", "timing"],
     "text": "Slide transition: "
             "const x = interpolate(frame, [start, start+12], [width, 0], "
             "{extrapolateLeft:'clamp', extrapolateRight:'clamp'}); "
             "style={{transform: `translateX(${x}px)`}}"},

    {"id": "remotion_render_entrypoint", "topic": "Node render entrypoint (@remotion/renderer)",
     "error_types": ["missing_import", "unknown"],
     "text": "Programmatic render entrypoint: "
             "import {bundle} from '@remotion/bundler'; "
             "import {renderMedia, selectComposition} from '@remotion/renderer'; "
             "const bundleLocation = await bundle(entryPoint); "
             "const composition = await selectComposition({serveUrl: bundleLocation, "
             "id: 'FotoOwlReel', inputProps}); "
             "await renderMedia({composition, serveUrl: bundleLocation, "
             "codec: 'h264', outputLocation, inputProps});"},

    {"id": "remotion_common_type_error", "topic": "Common TypeScript prop type errors",
     "error_types": ["type"],
     "text": "Common fix: durationInFrames, fps, width, height must be plain numbers, "
             "not strings. staticFile() must be used for local asset paths instead of "
             "relative paths: import {staticFile} from 'remotion'; src={staticFile('img1.jpg')}"},
]
