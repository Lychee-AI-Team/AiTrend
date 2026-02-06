import React from 'react';
import {Composition, Sequence, registerRoot} from 'remotion';

// 测试B: DailyNews 无音频版本

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

// 加载数据
const loadInputData = () => {
  const inputPath = process.env.REMOTION_INPUT;
  if (inputPath && typeof window === 'undefined') {
    try {
      const fs = require('fs');
      const data = fs.readFileSync(inputPath, 'utf-8');
      return JSON.parse(data);
    } catch (e) {
      console.error('Failed to load:', e);
    }
  }
  return {
    date: '2026-02-06',
    fps: 30,
    totalFrames: 6300,
    scenes: [{
      id: 'test',
      type: 'opening',
      startFrame: 0,
      durationFrames: 90,
      text: '测试场景 - 无音频'
    }]
  };
};

const inputData = loadInputData();

// 简化的场景组件
const SimpleScene = ({text, bgColor}: {text: string, bgColor: string}) => (
  <div style={{
    width: 1920,
    height: 1080,
    backgroundColor: bgColor,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    color: '#ffffff',
    fontSize: 60,
    fontFamily: 'sans-serif',
  }}>
    {text}
  </div>
);

const DailyNewsNoAudio: React.FC = () => {
  const {scenes, date} = inputData;
  
  return (
    <div style={{
      width: 1920,
      height: 1080,
      backgroundColor: '#0a0a0f',
      color: '#ffffff',
      overflow: 'hidden',
    }}>
      {scenes.map((scene: SceneData, idx: number) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          <SimpleScene 
            text={`${scene.id}: ${scene.text?.substring(0, 30) || 'No text'}...`}
            bgColor={idx % 2 === 0 ? '#1a1a2e' : '#16213e'}
          />
        </Sequence>
      ))}
    </div>
  );
};

registerRoot(() => (
  <>
    <Composition
      id="TestB"
      component={DailyNewsNoAudio}
      durationInFrames={inputData.totalFrames || 6300}
      fps={inputData.fps || 30}
      width={1920}
      height={1080}
    />
  </>
));
