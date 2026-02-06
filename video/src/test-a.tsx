import React from 'react';
import {Composition, registerRoot} from 'remotion';

// 测试A: 最简化版本 - 纯红色背景+白色文字
const TestA = () => (
  <div style={{
    width: 1920,
    height: 1080,
    backgroundColor: '#ff0000', // 红色背景
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }}>
    <h1 style={{color: '#ffffff', fontSize: 100, fontFamily: 'sans-serif'}}>
      TEST A - RED BG
    </h1>
  </div>
);

registerRoot(() => (
  <>
    <Composition
      id="TestA"
      component={TestA}
      durationInFrames={30}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
));
