import React from 'react';
import {Composition, registerRoot} from 'remotion';

// 简化的测试组件
export const TestVideo: React.FC = () => {
  return (
    <div style={{
      width: 1920,
      height: 1080,
      backgroundColor: '#0a0a0f',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      color: '#ffffff',
      fontFamily: 'sans-serif',
    }}>
      <h1 style={{
        fontSize: 80,
        marginBottom: 40,
        color: '#00d4ff',
      }}>
        AiTrend
      </h1>
      <p style={{
        fontSize: 40,
        color: '#e6f1ff',
      }}>
        AI 热点日报
      </p>
      <p style={{
        fontSize: 30,
        color: '#8892b0',
        marginTop: 60,
      }}>
        2026-02-06
      </p>
    </div>
  );
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="TestVideo"
        component={TestVideo}
        durationInFrames={90}
        fps={30}
        width={1920}
        height={1080}
      />
    </>
  );
};

registerRoot(RemotionRoot);
