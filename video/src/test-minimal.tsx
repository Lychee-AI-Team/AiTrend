import React from 'react';
import {Composition, registerRoot} from 'remotion';

// 最小化测试 - 单个简单组件
const MinimalTest = () => (
  <div style={{
    width: 1920,
    height: 1080,
    backgroundColor: '#ff0000', // 红色背景
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
  }}>
    <h1 style={{
      color: '#ffffff',
      fontSize: 100,
      fontFamily: '"Noto Sans CJK SC", sans-serif',
    }}>
      测试文字 TEST
    </h1>
  </div>
);

registerRoot(() => (
  <Composition
    id="MinimalTest"
    component={MinimalTest}
    durationInFrames={90}
    fps={30}
    width={1920}
    height={1080}
  />
));
