import {Composition, Sequence, AbsoluteFill, staticFile} from 'remotion';
export const FotoOwlReel = () => (<AbsoluteFill><Sequence from={0} durationInFrames={90}><img src={staticFile('img_00.jpg')} /></Sequence></AbsoluteFill>);
export const RemotionRoot = () => (<Composition id='FotoOwlReel' component={FotoOwlReel} durationInFrames={900} fps={30} width={1080} height={1920} />);
