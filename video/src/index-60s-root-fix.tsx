import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 60秒竖屏版本 - 根本修复版（不使用截图，避免Cloudflare）

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 真实数据（今天推送到Discord的AI热点）
const VIDEO_DATA = {
  date: '2026-02-06',
  fps: 30,
  totalFrames: 1800,
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 90,
      text: '今天AI圈发生了什么？'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 90,
      durationFrames: 540,
      rank: 1,
      title: 'Molt Beach',
      subtitle: 'AI新工具',
      text: 'Molt Beach在Product Hunt发布，获得18个赞。这是一个值得关注的全新AI产品，可能带来创新功能。',
      keyPoint: 'Product Hunt 18⭐新品',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/molt-beach'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 630,
      durationFrames: 540,
      rank: 2,
      title: 'Claude Opus 4.6',
      subtitle: 'Anthropic大模型',
      text: 'Anthropic在Product Hunt发布Claude Opus 4.6，获得7个赞。Anthropic继续推动大模型技术边界。',
      keyPoint: 'Anthropic新品发布',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/anthropic-5'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 1170,
      durationFrames: 540,
      rank: 3,
      title: 'Qwen3-Coder',
      subtitle: '阿里开源代码模型',
      text: '阿里Qwen团队开源Qwen3-Coder代码模型，GitHub获得15328星。这是国产AI的重大突破，值得关注。',
      keyPoint: 'GitHub 15328⭐开源',
      platform: 'GitHub',
      platformColor: '#24292E',
      url: 'github.com/QwenLM/Qwen3-Coder'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1710,
      durationFrames: 90,
      text: '点赞关注，每天60秒了解AI热点！'
    }
  ]
};

// 主组件
const DailyNews60s: React.FC = () => {
  const {scenes} = VIDEO_DATA;
  
  return (
    <div style={{
      width: 1080,
      height: 1920,
      backgroundColor: '#0a0a0f',
      fontFamily: CHINESE_FONT,
      color: '#ffffff',
    }}>
      {/* 单一音频文件 */}
      <Audio src={staticFile('audio/2026-02-06/full_audio.mp3')} />
      
      {scenes.map((scene: any) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          {renderScene(scene)}
        </Sequence>
      ))}
    </div>
  );
};

// 渲染场景
const renderScene = (scene: any) => {
  switch (scene.type) {
    case 'opening':
      return <OpeningScene text={scene.text} />;
    case 'hotspot':
      return <HotspotScene {...scene} />;
    case 'closing':
      return <ClosingScene text={scene.text} />;
    default:
      return null;
  }
};

// 开场场景
const OpeningScene: React.FC<{text: string}> = ({text}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '80px',
  }}>
    {/* Logo */}
    <div style={{
      width: 200,
      height: 200,
      borderRadius: 40,
      background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 60,
      boxShadow: '0 20px 60px rgba(0, 212, 255, 0.3)',
    }}>
      <span style={{fontSize: 80, fontWeight: 'bold'}}>AI</span>
    </div>
    
    <h1 style={{
      fontSize: 96,
      background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: 40,
      fontWeight: 'bold',
    }}>
      AiTrend
    </h1>
    
    <p style={{
      fontSize: 64,
      color: '#e6f1ff',
      textAlign: 'center',
      fontWeight: 'bold',
      textShadow: '0 4px 20px rgba(0,0,0,0.5)',
    }}>
      {text}
    </p>
    
    <p style={{
      fontSize: 36,
      color: '#64ffda',
      marginTop: 80,
      opacity: 0.8,
    }}>
      2026.02.06
    </p>
  </div>
);

// 热点详情场景 - 不使用截图，使用卡片式设计
const HotspotScene: React.FC<any> = ({
  rank, title, subtitle, text, keyPoint, platform, platformColor, url
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '60px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* 顶部：排名和平台 */}
    <div style={{
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: 50,
    }}>
      {/* 排名 */}
      <div style={{
        width: 100,
        height: 100,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: 48,
        fontWeight: 'bold',
        boxShadow: '0 10px 30px rgba(0, 212, 255, 0.4)',
      }}>
        {rank}
      </div>
      
      {/* 平台标签 */}
      <div style={{
        backgroundColor: platformColor,
        padding: '16px 32px',
        borderRadius: 30,
        fontSize: 32,
        fontWeight: 'bold',
        color: '#ffffff',
      }}>
        {platform}
      </div>
    </div>
    
    {/* 标题区域 */}
    <div style={{
      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1))',
      borderRadius: 24,
      padding: '50px',
      marginBottom: 50,
      border: '2px solid rgba(0, 212, 255, 0.3)',
    }}>
      <p style={{
        fontSize: 36,
        color: '#64ffda',
        marginBottom: 20,
        fontWeight: 'bold',
      }}>
        {subtitle}
      </p>
      <h2 style={{
        fontSize: 64,
        fontWeight: 'bold',
        color: '#e6f1ff',
        lineHeight: 1.2,
      }}>
        {title}
      </h2>
    </div>
    
    {/* 描述文字 */}
    <p style={{
      fontSize: 44,
      color: '#a8b2d1',
      lineHeight: 1.6,
      marginBottom: 50,
    }}>
      {text}
    </p>
    
    {/* 核心亮点 */}
    <div style={{
      background: 'rgba(0, 212, 255, 0.15)',
      border: '3px solid rgba(0, 212, 255, 0.5)',
      borderRadius: 20,
      padding: '40px',
      marginTop: 'auto',
      marginBottom: 40,
    }}>
      <p style={{fontSize: 32, color: '#64ffda', marginBottom: 16}}>
        ⭐ 核心亮点
      </p>
      <p style={{fontSize: 52, color: '#e6f1ff', fontWeight: 'bold'}}>
        {keyPoint}
      </p>
    </div>
    
    {/* URL */}
    <div style={{
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: 12,
      padding: '24px 32px',
    }}>
      <p style={{
        fontSize: 28,
        color: '#64ffda',
        margin: 0,
        fontFamily: 'monospace',
      }}>
        🔗 {url}
      </p>
    </div>
  </div>
);

// 结尾场景
const ClosingScene: React.FC<{text: string}> = ({text}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #1e1b4b 0%, #312e81 50%, #1e1b4b 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '80px',
  }}>
    {/* Logo */}
    <div style={{
      width: 180,
      height: 180,
      borderRadius: 36,
      background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 60,
      boxShadow: '0 20px 60px rgba(0, 212, 255, 0.3)',
    }}>
      <span style={{fontSize: 72, fontWeight: 'bold'}}>AI</span>
    </div>
    
    <h1 style={{
      fontSize: 84,
      background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: 50,
      fontWeight: 'bold',
    }}>
      AiTrend
    </h1>
    
    <p style={{
      fontSize: 52,
      color: '#e6f1ff',
      textAlign: 'center',
      fontWeight: 'bold',
      lineHeight: 1.4,
    }}>
      {text}
    </p>
    
    <p style={{
      fontSize: 36,
      color: '#64ffda',
      marginTop: 100,
      opacity: 0.8,
    }}>
      每天60秒 · 掌握AI前沿
    </p>
  </div>
);

// 注册
registerRoot(() => (
  <>
    <Composition
      id="DailyNews60s"
      component={DailyNews60s}
      durationInFrames={VIDEO_DATA.totalFrames}
      fps={VIDEO_DATA.fps}
      width={1080}
      height={1920}
    />
  </>
));
