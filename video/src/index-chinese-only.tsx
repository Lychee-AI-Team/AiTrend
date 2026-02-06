import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 纯中文解读版 - 只显示中文解读和URL

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置 - 只使用中文解读
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 1575,  // 52.60秒 @ 30fps
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 159,  // 5.33秒
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/2026-02-06/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 159,
      durationFrames: 390,  // 13.03秒
      rank: 1,
      title: 'cognee',
      chineseText: 'cognee是一个AI智能体记忆框架，开发者只需6行代码就能为AI Agent添加长期记忆能力，让AI能够记住对话历史和用户偏好，大幅提升AI应用的实用性。',
      url: 'github.com/topoteretes/cognee',
      audioFile: 'audio/2026-02-06/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 549,
      durationFrames: 380,  // 12.67秒
      rank: 2,
      title: 'anthropics/skills',
      chineseText: 'Anthropic开源的AI Agent技能库，包含各种实用的Agent技能实现，开发者可以直接参考或使用这些技能来构建自己的AI应用，是学习和开发AI Agent的宝贵资源。',
      url: 'github.com/anthropics/skills',
      audioFile: 'audio/2026-02-06/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 929,
      durationFrames: 466,  // 15.55秒
      rank: 3,
      title: 'PentestAgent',
      chineseText: 'PentestAgent是一款AI驱动的安全测试工具，能够自动进行黑盒安全测试、漏洞挖掘和渗透测试，为安全研究人员和黑客提供AI助手，大幅提升安全测试效率。',
      url: 'github.com/GH05TCREW/pentestagent',
      audioFile: 'audio/2026-02-06/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1395,
      durationFrames: 180,  // 6.01秒
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/2026-02-06/closing.mp3'
    }
  ]
};

// 主组件
const DailyNewsChinese: React.FC = () => {
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

// 热点详情场景 - 只显示中文解读和URL
const HotspotScene: React.FC<any> = ({
  rank, title, chineseText, url
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
      width: 100,
      height: 100,
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: 48,
      fontWeight: 'bold',
      marginBottom: 50,
      boxShadow: '0 10px 30px rgba(0, 212, 255, 0.4)',
    }}>
      {rank}
    </div>
    
    {/* 项目名称（仅显示，不生成语音） */}
    <div style={{
      fontSize: 40,
      color: '#64ffda',
      marginBottom: 30,
      opacity: 0.7,
    }}>
      {title}
    </div>
    
    {/* 中文解读（核心内容） */}
    <div style={{
      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(123, 44, 191, 0.1))',
      borderRadius: 24,
      padding: '50px',
      marginBottom: 50,
      border: '2px solid rgba(0, 212, 255, 0.3)',
      flex: 1,
    }}>
      <p style={{
        fontSize: 48,
        color: '#e6f1ff',
        lineHeight: 1.8,
        fontWeight: 'bold',
      }}>
        {chineseText}
      </p>
    </div>
    
    {/* URL（底部） */}
    <div style={{
      background: 'rgba(0, 0, 0, 0.4)',
      borderRadius: 16,
      padding: '30px',
      border: '2px solid rgba(100, 255, 218, 0.3)',
    }}>
      <p style={{
        fontSize: 32,
        color: '#64ffda',
        margin: 0,
        fontFamily: 'monospace',
        textAlign: 'center',
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
      id="DailyNewsChinese"
      component={DailyNewsChinese}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
