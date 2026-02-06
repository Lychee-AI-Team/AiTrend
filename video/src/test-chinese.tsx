import React from 'react';
import {Composition, registerRoot} from 'remotion';

// 中文显示测试 - 验证中文字体
const ChineseTest = () => (
  <div style={{
    width: 1920,
    height: 1080,
    backgroundColor: '#0a0a0f',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    color: '#ffffff',
  }}>
    <h1 style={{
      fontSize: 100,
      fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", sans-serif',
      marginBottom: 40,
      color: '#00d4ff',
    }}>
      AiTrend
    </h1>
    <p style={{
      fontSize: 60,
      fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", sans-serif',
      color: '#e6f1ff',
    }}>
      AI 热点日报
    </p>
    <p style={{
      fontSize: 40,
      fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", sans-serif',
      color: '#8892b0',
      marginTop: 60,
    }}>
      2026年2月6日
    </p>
    <p style={{
      fontSize: 30,
      fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", sans-serif',
      color: '#64ffda',
      marginTop: 40,
    }}>
      中文显示测试：GPT-5 预览版发布
    </p>
  </div>
);

registerRoot(() => (
  <>
    <Composition
      id="ChineseTest"
      component={ChineseTest}
      durationInFrames={90}
      fps={30}
      width={1920}
      height={1080}
    />
  </>
));
