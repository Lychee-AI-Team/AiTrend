import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 2026-02-06 完整版 - 使用AiTrend获取的完整信息

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置 - 使用完整信息的新数据
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 1052,  // 35.14秒 @ 30fps
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 193,  // 6.44秒
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/2026-02-06/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 193,
      durationFrames: 167,  // 5.58秒
      rank: 1,
      title: 'cognee',
      subtitle: 'AI Agent内存框架',
      text: 'Memory for AI Agents in 6 lines of code',
      description: 'cognee 是一个为AI Agent设计的内存框架，只需6行代码即可实现AI的记忆功能。',
      keyPoint: '⭐11955 | Python',
      platform: 'GitHub',
      platformColor: '#24292E',
      url: 'github.com/topoteretes/cognee',
      audioFile: 'audio/2026-02-06/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 360,
      durationFrames: 145,  // 4.86秒
      rank: 2,
      title: 'anthropics/skills',
      subtitle: 'Agent技能库',
      text: 'Public repository for Agent Skills',
      description: 'Anthropic开源的Agent技能库，提供各种AI Agent技能的实现参考。',
      keyPoint: '⭐64475 | Python',
      platform: 'GitHub',
      platformColor: '#24292E',
      url: 'github.com/anthropics/skills',
      audioFile: 'audio/2026-02-06/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 505,
      durationFrames: 356,  // 11.88秒
      rank: 3,
      title: 'PentestAgent',
      subtitle: 'AI安全测试框架',
      text: 'PentestAgent is an AI agent framework for black-box security testing, supporting bug bounty, red-team, and penetration testing workflows.',
      description: 'PentestAgent是一个AI安全测试框架，支持黑盒安全测试、漏洞赏金、红队和渗透测试工作流。',
      keyPoint: '⭐1415 | Python',
      platform: 'GitHub',
      platformColor: '#24292E',
      url: 'github.com/GH05TCREW/pentestagent',
      audioFile: 'audio/2026-02-06/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 861,
      durationFrames: 191,  // 6.37秒
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/2026-02-06/closing.mp3'
    }
  ]
};

// 主组件
const DailyNewsComplete: React.FC = () => {
  const {scenes} = VIDEO_CONFIG;
  
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
  rank, title, subtitle, text, description, keyPoint, platform, platformColor, url
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
        fontSize: 56,
        fontWeight: 'bold',
        color: '#e6f1ff',
        lineHeight: 1.2,
      }}>
        {title}
      </h2>
    </div>
    
    {/* 原文介绍 */}
    <div style={{
      background: 'rgba(255, 255, 255, 0.05)',
      borderRadius: 16,
      padding: '30px',
      marginBottom: 30,
    }}>
      <p style={{
        fontSize: 32,
        color: '#a8b2d1',
        fontStyle: 'italic',
        lineHeight: 1.6,
      }}>
        "{text}"
      </p>
    </div>
    
    {/* 中文解读 */}
    <p style={{
      fontSize: 38,
      color: '#e6f1ff',
      lineHeight: 1.7,
      marginBottom: 40,
    }}>
      {description}
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
        ⭐ 核心数据
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
      id="DailyNewsComplete"
      component={DailyNewsComplete}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
