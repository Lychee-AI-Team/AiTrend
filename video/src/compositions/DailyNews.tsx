import React from 'react';
import {Composition, Sequence, Audio, staticFile} from 'remotion';
import {Opening} from '../components/Opening';
import {DetailedHotspot} from '../components/DetailedHotspot';
import {QuickSummary} from '../components/QuickSummary';
import {Closing} from '../components/Closing';

interface VideoData {
  date: string;
  fps: number;
  totalFrames: number;
  scenes: SceneData[];
}

interface SceneData {
  id: string;
  type: 'opening' | 'detailed' | 'quick' | 'closing';
  startFrame: number;
  durationFrames: number;
  [key: string]: any;
}

interface DailyNewsProps {
  data: VideoData;
}

export const DailyNews: React.FC<DailyNewsProps> = ({data}) => {
  const {scenes, date} = data;
  
  return (
    <div style={{
      width: 1920,
      height: 1080,
      backgroundColor: '#0a0a0f',
      fontFamily: '"Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif',
      color: '#ffffff',
      overflow: 'hidden',
    }}>
      {scenes.map((scene) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          {renderScene(scene, date)}
        </Sequence>
      ))}
    </div>
  );
};

const renderScene = (scene: SceneData, date: string) => {
  switch (scene.type) {
    case 'opening':
      return (
        <>
          <Opening text={scene.text} date={date} />
          <Audio src={staticFile(scene.audioFile.replace('public/', ''))} />
        </>
      );
    
    case 'detailed':
      return (
        <>
          <DetailedHotspot
            rank={scene.rank}
            title={scene.title}
            text={scene.text}
            keyPoint={scene.keyPoint}
            source={scene.source}
          />
          <Audio src={staticFile(scene.audioFile.replace('public/', ''))} />
        </>
      );
    
    case 'quick':
      return (
        <>
          <QuickSummary items={scene.items} />
          {scene.audioFiles.map((file: string, idx: number) => (
            <Audio
              key={idx}
              src={staticFile(file.replace('public/', ''))}
              startFrom={idx === 0 ? 0 : undefined}
            />
          ))}
        </>
      );
    
    case 'closing':
      return (
        <>
          <Closing text={scene.text} />
          <Audio src={staticFile(scene.audioFile.replace('public/', ''))} />
        </>
      );
    
    default:
      return null;
  }
};
