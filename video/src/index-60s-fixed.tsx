import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 60秒竖屏版本 - 修复版（单一音频文件）

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
      title: 'Molt Beach - AI新工具',
      text: 'Molt Beach在Product Hunt发布，获得18个赞。这是一个新的AI产品，值得关注。',
      keyPoint: 'Product Hunt新品',
      vendor: 'Molt',
      logo: 'logos/default.svg',
      url: 'https://www.producthunt.com/products/molt-beach',
      useScreenshot: true,
      screenshot: 'screenshots/hotspot_1.png'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 630,
      durationFrames: 540,
      rank: 2,
      title: 'Claude Opus 4.6发布',
      text: 'Anthropic在Product Hunt发布Claude Opus 4.6，获得7个赞。Anthropic继续推动大模型发展。',
      keyPoint: 'Anthropic新品',
      vendor: 'Anthropic',
      logo: 'logos/anthropic.svg',
      url: 'https://www.producthunt.com/products/anthropic-5',
      useScreenshot: true,
      screenshot: 'screenshots/hotspot_2.png'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 1170,
      durationFrames: 540,
      rank: 3,
      title: '阿里Qwen3-Coder开源',
      text: '阿里Qwen团队开源Qwen3-Coder代码模型，GitHub获得15328星。这是国产AI的重大突破。',
      keyPoint: '15328星开源项目',
      vendor: 'Alibaba',
      logo: 'logos/default.svg',
      url: 'https://github.com/QwenLM/Qwen3-Coder',
      useScreenshot: true,
      screenshot: 'screenshots/hotspot_3.png'
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
  const {scenes, date} = VIDEO_DATA;
  
  return (
    <div style={{
      width: 1080,
      height: 1920,
      backgroundColor: '#0a0a0f',
      fontFamily: CHINESE_FONT,
      color: '#ffffff',
    }}>
      {/* 单一音频文件（避免多音轨冲突） */}
      <Audio src={staticFile('audio/2026-02-06/full_audio.mp3')} />
      
      {scenes.map((scene: any) => (
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

// 渲染场景
const renderScene = (scene: any, date: string) => {
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
    background: 'linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '60px',
  }}>
    <h1 style={{
      fontSize: 80,
      background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: 30,
    }}>
      AiTrend
    </h1>
    <p style={{
      fontSize: 56,
      color: '#e6f1ff',
      textAlign: 'center',
      fontWeight: 'bold',
    }}>
      {text}
    </p>
  </div>
);

// 热点详情场景
const HotspotScene: React.FC<any> = ({
  rank, title, text, keyPoint, vendor, logo, url, useScreenshot, screenshot
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '60px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* 排名 */}
    <div style={{
      width: 70,
      height: 70,
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: 32,
      fontWeight: 'bold',
      marginBottom: 40,
    }}>
      {rank}
    </div>
    
    {/* Logo */}
    <div style={{
      width: 140,
      height: 140,
      borderRadius: 24,
      backgroundColor: '#ffffff',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      marginBottom: 50,
      overflow: 'hidden',
    }}>
      <img 
        src={staticFile(logo)} 
        alt={vendor}
        style={{width: 100, height: 100, objectFit: 'contain'}}
        onError={(e) => {e.currentTarget.style.display = 'none'}}
      />
    </div>
    
    {/* 标题 */}
    <h2 style={{
      fontSize: 52,
      fontWeight: 'bold',
      color: '#e6f1ff',
      marginBottom: 40,
      lineHeight: 1.3,
    }}>
      {title}
    </h2>
    
    {/* 正文 */}
    <p style={{
      fontSize: 42,
      color: '#a8b2d1',
      lineHeight: 1.6,
      marginBottom: 50,
    }}>
      {text}
    </p>
    
    {/* 截图区域 */}
    {useScreenshot && (
      <div style={{
        width: '100%',
        height: 400,
        backgroundColor: '#2d3748',
        borderRadius: 16,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 40,
        overflow: 'hidden',
        position: 'relative',
      }}>
        {screenshot && (
          <img 
            src={staticFile(screenshot)} 
            alt="screenshot"
            style={{width: '100%', height: '100%', objectFit: 'cover'}}
            onError={(e) => {e.currentTarget.style.display = 'none'}}
          />
        )}
        
        {/* URL显示 */}
        <div style={{
          position: 'absolute',
          bottom: 20,
          left: 20,
          right: 20,
          background: 'rgba(0,0,0,0.7)',
          padding: '10px 15px',
          borderRadius: 8,
        }}>
          <p style={{
            fontSize: 24,
            color: '#64ffda',
            margin: 0,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {url}
          </p>
        </div>
      </div>
    )}
    
    {/* 核心亮点 */}
    <div style={{
      background: 'rgba(0, 212, 255, 0.1)',
      border: '2px solid rgba(0, 212, 255, 0.3)',
      borderRadius: 16,
      padding: 30,
      marginTop: 'auto',
    }}>
      <p style={{fontSize: 28, color: '#64ffda', marginBottom: 10}}>
        核心亮点
      </p>
      <p style={{fontSize: 40, color: '#e6f1ff', fontWeight: 'bold'}}>
        {keyPoint}
      </p>
    </div>
  </div>
);

// 结尾场景
const ClosingScene: React.FC<{text: string}> = ({text}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #1e1b4b 0%, #312e81 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '60px',
  }}>
    <h1 style={{
      fontSize: 72,
      background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: 40,
    }}>
      AiTrend
    </h1>
    <p style={{
      fontSize: 44,
      color: '#e6f1ff',
      textAlign: 'center',
      fontWeight: 'bold',
    }}>
      {text}
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
