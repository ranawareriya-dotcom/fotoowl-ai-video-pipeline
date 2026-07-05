import React from 'react';
import {
  Composition,
  Sequence,
  AbsoluteFill,
  Img,
  staticFile,
  interpolate,
  useCurrentFrame,
  Easing,
} from 'remotion';

const FPS = 30;
const WIDTH = 1080;
const HEIGHT = 1920;
const SCENE_DURATION_SECONDS = 6;
const SCENE_DURATION_FRAMES = SCENE_DURATION_SECONDS * FPS; 
const FADE_DURATION_FRAMES = 15; 

interface SceneContentProps {
  imageSrc: string;
  caption: string;
  zoomFactor?: number;
}

const SceneContent: React.FC<SceneContentProps> = ({
  imageSrc,
  caption,
  zoomFactor = 1.15,
}) => {
  const frame = useCurrentFrame();

  const scale = interpolate(frame, [0, SCENE_DURATION_FRAMES], [1, zoomFactor], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill style={{ backgroundColor: 'black' }}>
      <Img
        src={staticFile(imageSrc)}
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'cover',
          transform: `scale(${scale})`,
        }}
      />
      <AbsoluteFill
        style={{
          justifyContent: 'flex-end',
          alignItems: 'center',
          paddingBottom: 80,
        }}
      >
        <div
          style={{
            color: 'white',
            fontSize: 48,
            fontFamily: 'Montserrat, sans-serif',
            textAlign: 'center',
            textShadow: '2px 2px 4px rgba(0,0,0,0.7)',
          }}
        >
          {caption}
        </div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const FotoOwlReel: React.FC = () => {
  const scenes = [
    { file: 'img1.jpg', caption: 'the quiet promise' },
    { file: 'img3.jpg', caption: 'a tender world' },
    { file: 'img2.jpg', caption: 'forever\'s embrace' },
  ];

  let currentGlobalStartFrame = 0;
  const allElements: React.ReactNode[] = [];

  scenes.forEach((scene, index) => {
    const isFirstScene = index === 0;
    const isLastScene = index === scenes.length - 1;

    // 1. Render the incoming scene's fading-in part (if not the first scene)
    if (!isFirstScene) {
      allElements.push(
        <Sequence
          key={`fade-in-${index}`}
          from={currentGlobalStartFrame}
          durationInFrames={FADE_DURATION_FRAMES}
        >
          <AbsoluteFill
            style={{
              opacity: interpolate(
                useCurrentFrame(),
                [0, FADE_DURATION_FRAMES],
                [0, 1],
                {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                  easing: Easing.ease,
                }
              ),
            }}
          >
            <SceneContent imageSrc={scene.file} caption={scene.caption} />
          </AbsoluteFill>
        </Sequence>
      );
    }

    // 2. Render the current scene's main, fully opaque duration
    const mainContentFrom = isFirstScene ? 0 : currentGlobalStartFrame + FADE_DURATION_FRAMES;
    const mainContentDuration = SCENE_DURATION_FRAMES - (isFirstScene || isLastScene ? 0 : FADE_DURATION_FRAMES);

    allElements.push(
      <Sequence
        key={`scene-${index}-main`}
        from={mainContentFrom}
        durationInFrames={mainContentDuration}
      >
        <SceneContent imageSrc={scene.file} caption={scene.caption} />
      </Sequence>
    );

    // 3. Render the outgoing scene's fading-out part (if not the last scene)
    if (!isLastScene) {
      allElements.push(
        <Sequence
          key={`fade-out-${index}`}
          from={currentGlobalStartFrame + SCENE_DURATION_FRAMES}
          durationInFrames={FADE_DURATION_FRAMES}
        >
          <AbsoluteFill
            style={{
              opacity: interpolate(
                useCurrentFrame(),
                [0, FADE_DURATION_FRAMES],
                [1, 0],
                {
                  extrapolateLeft: 'clamp',
                  extrapolateRight: 'clamp',
                  easing: Easing.ease,
                }
              ),
            }}
          >
            <SceneContent imageSrc={scene.file} caption={scene.caption} />
          </AbsoluteFill>
        </Sequence>
      );

      // Advance currentGlobalStartFrame for the next scene's start (accounting for overlap)
      currentGlobalStartFrame += SCENE_DURATION_FRAMES - FADE_DURATION_FRAMES;
    } else {
      // For the last scene, simply add its full duration
      currentGlobalStartFrame += SCENE_DURATION_FRAMES;
    }
  });

  return <AbsoluteFill>{allElements}</AbsoluteFill>;
};

export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="FotoOwlReel"
      component={FotoOwlReel}
      durationInFrames={3 * SCENE_DURATION_FRAMES - (3 - 1) * FADE_DURATION_FRAMES}
      fps={FPS}
      width={WIDTH}
      height={HEIGHT}
    />
  </>
);
