import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 2026-02-06 最终版 - 1.2倍语速，时长不限制

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 今天最新3条热点数据（来自sent_articles.json）
const VIDEO_CONFIG = {
  fps: 30,
  // 总帧数根据音频实际长度计算
  totalFrames: 1215,  // 40.50秒 @ 30fps
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 189,  // 6.30秒
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/2026-02-06/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 189,
      durationFrames: 248,  // 8.28秒
      rank: 1,
      title: 'ClawApp',
      subtitle: 'Product Hunt新品',
      text: 'ClawApp在Product Hunt发布，获得81个赞。这是一个新的AI工具产品，正在获得用户关注。',
      keyPoint: '81⭐ 新品发布',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/clawapp',
      originalTitle: '[Product Hunt] ClawApp ⭐81',
      audioFile: 'audio/2026-02-06/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 437,
      durationFrames: 274,  // 9.14秒
      rank: 2,
      title: 'OpenAI Frontier',
      subtitle: 'OpenAI新品',
      text: 'OpenAI Frontier在Product Hunt发布，获得85个赞。OpenAI继续在AI领域推出新产品。',
      keyPoint: '85⭐ OpenAI',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/openai',
      originalTitle: '[Product Hunt] OpenAI Frontier ⭐85',
      audioFile: 'audio/2026-02-06/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 711,
      durationFrames: 312,  // 10.40秒
      rank: 3,
      title: 'Obi',
      subtitle: 'AI产品',
      text: 'Obi在Product Hunt发布，获得97个赞。这是一个备受关注的AI产品，获得了很高的用户认可。',
      keyPoint: '97⭐ 高关注度',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      url: 'producthunt.com/products/obi-3',
      originalTitle: '[Product Hunt] Obi ⭐97',
      audioFile: 'audio/2026-02-06/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1023,
      durationFrames: 191,  // 6.37秒
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。我们下期再见！',
      audioFile: 'audio/2026-02-06/closing.mp3'
    }
  ]
};

// 主组件
const DailyNewsFinal: React.FC = () => {
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
  rank, title, subtitle, text, keyPoint, platform, platformColor, url, originalTitle
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
    
    {/* 原标题（小字） */}
    <p style={{
      fontSize: 24,
      color: '#64ffda',
      marginBottom: 16,
      opacity: 0.7,
    }}>
      {originalTitle}
    </p>
    
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
      每天带你了解最新AI动态
    </p>
  </div>
);

// 注册
registerRoot(() => (
  <>
    <Composition
      id="DailyNewsFinal"
      component={DailyNewsFinal}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
