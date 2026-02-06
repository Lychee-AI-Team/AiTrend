import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 76秒竖屏版本 - 场景时长跟随音频长度

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置 - 场景时长跟随音频
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 2293,  // 76.54秒 @ 30fps
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 185,  // 6.19秒
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看。',
      audioFile: 'audio/2026-02-06/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 185,
      durationFrames: 579,  // 19.33秒
      rank: 1,
      title: 'Molt Beach',
      subtitle: 'Product Hunt新品',
      text: 'Molt Beach在Product Hunt发布，获得18个赞。这是一个全新的AI产品，致力于提供创新的AI解决方案。Product Hunt是科技产品发布的重要平台，能获得用户认可意味着产品具有潜力。',
      keyPoint: '18⭐新品发布',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/molt-beach',
      audioFile: 'audio/2026-02-06/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 764,
      durationFrames: 557,  // 18.58秒
      rank: 2,
      title: 'Claude Opus 4.6',
      subtitle: 'Anthropic新品',
      text: 'Anthropic发布Claude Opus 4.6，获得7个赞。作为OpenAI的主要竞争对手，Anthropic一直在推动大模型技术发展。Claude系列以安全性和可靠性著称，新版本标志着技术持续领先。',
      keyPoint: '大模型竞争',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/anthropic-5',
      audioFile: 'audio/2026-02-06/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 1321,
      durationFrames: 695,  // 23.18秒
      rank: 3,
      title: 'Qwen3-Coder',
      subtitle: '阿里开源代码模型',
      text: '阿里Qwen团队开源Qwen3-Coder，GitHub获得15328星。这是国产AI的重大突破，代表了中国AI技术在国际舞台获得广泛认可。Qwen3-Coder专门针对代码生成优化，是开发者的强大助手。',
      keyPoint: '15328⭐开源',
      platform: 'GitHub',
      platformColor: '#24292E',
      url: 'github.com/QwenLM/Qwen3-Coder',
      audioFile: 'audio/2026-02-06/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 2016,
      durationFrames: 277,  // 9.25秒
      text: '以上就是今天的AI热点。点赞关注，AiTrend每天60秒带你了解最新AI动态。我们下期再见！',
      audioFile: 'audio/2026-02-06/closing.mp3'
    }
  ]
};

// 主组件
const DailyNews: React.FC = () => {
  const {scenes, fps, totalFrames} = VIDEO_CONFIG;
  
  return (
    <div style={{
      width: 1080,
      height: 1920,
      backgroundColor: '#0a0a0f',
      fontFamily: CHINESE_FONT,
      color: '#ffffff',
    }}>
      {scenes.map((scene: any) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          {renderScene(scene)}
          {scene.audioFile && <Audio src={staticFile(scene.audioFile)} />}
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
      marginTop: 60,
      opacity: 0.8,
    }}>
      2026.02.06
    </p>
  </div>
);

// 热点详情场景
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
      marginBottom: 40,
    }}>
      <div style={{
        width: 90,
        height: 90,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: 44,
        fontWeight: 'bold',
        boxShadow: '0 10px 30px rgba(0, 212, 255, 0.4)',
      }}>
        {rank}
      </div>
      
      <div style={{
        backgroundColor: platformColor,
        padding: '14px 28px',
        borderRadius: 30,
        fontSize: 30,
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
      padding: '40px',
      marginBottom: 40,
      border: '2px solid rgba(0, 212, 255, 0.3)',
    }}>
      <p style={{
        fontSize: 32,
        color: '#64ffda',
        marginBottom: 16,
        fontWeight: 'bold',
      }}>
        {subtitle}
      </p>
      <h2 style={{
        fontSize: 60,
        fontWeight: 'bold',
        color: '#e6f1ff',
        lineHeight: 1.2,
      }}>
        {title}
      </h2>
    </div>
    
    {/* 描述文字 */}
    <p style={{
      fontSize: 40,
      color: '#a8b2d1',
      lineHeight: 1.7,
      marginBottom: 40,
    }}>
      {text}
    </p>
    
    {/* 核心亮点 */}
    <div style={{
      background: 'rgba(0, 212, 255, 0.15)',
      border: '3px solid rgba(0, 212, 255, 0.5)',
      borderRadius: 20,
      padding: '35px',
      marginTop: 'auto',
      marginBottom: 30,
    }}>
      <p style={{fontSize: 30, color: '#64ffda', marginBottom: 12}}>
        ⭐ 核心亮点
      </p>
      <p style={{fontSize: 48, color: '#e6f1ff', fontWeight: 'bold'}}>
        {keyPoint}
      </p>
    </div>
    
    {/* URL */}
    <div style={{
      background: 'rgba(255, 255, 255, 0.1)',
      borderRadius: 12,
      padding: '20px 28px',
    }}>
      <p style={{
        fontSize: 26,
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
      fontSize: 48,
      color: '#e6f1ff',
      textAlign: 'center',
      fontWeight: 'bold',
      lineHeight: 1.5,
    }}>
      {text}
    </p>
    
    <p style={{
      fontSize: 36,
      color: '#64ffda',
      marginTop: 80,
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
      id="DailyNews"
      component={DailyNews}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
