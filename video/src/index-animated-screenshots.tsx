import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio, interpolate, Easing, useCurrentFrame} from 'remotion';

// 带截图动画版视频 - 截图从大到小缩放

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 1542,
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 144,
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/2026-02-06/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 144,
      durationFrames: 372,
      rank: 1,
      title: 'cognee',
      chineseText: 'cognee是一个AI智能体记忆框架，开发者只需6行代码就能为AI Agent添加长期记忆能力。AI可以记住对话历史和用户偏好，大幅提升AI应用的实用性。该项目在GitHub上获得超过11000个星标。',
      url: 'github.com/topoteretes/cognee',
      screenshot: 'screenshots/hotspot_1.png',
      audioFile: 'audio/2026-02-06/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 516,
      durationFrames: 461,
      rank: 2,
      title: 'anthropics/skills',
      chineseText: 'Anthropic开源的AI Agent技能库包含各种实用的Agent技能实现代码，开发者可以直接参考或使用这些技能快速构建AI应用。作为OpenAI的主要竞争对手，Anthropic在AI安全性方面技术领先，该项目获得超过64000个星标。',
      url: 'github.com/anthropics/skills',
      screenshot: 'screenshots/hotspot_2.png',
      audioFile: 'audio/2026-02-06/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 977,
      durationFrames: 412,
      rank: 3,
      title: 'PentestAgent',
      chineseText: 'PentestAgent是一款AI驱动的安全测试工具，能够自动执行黑盒安全测试、漏洞挖掘和渗透测试。为安全研究人员提供AI助手，大幅提升安全测试效率，该项目获得超过1400个星标。',
      url: 'github.com/GH05TCREW/pentestagent',
      screenshot: 'screenshots/hotspot_3.png',
      audioFile: 'audio/2026-02-06/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1389,
      durationFrames: 153,
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/2026-02-06/closing.mp3'
    }
  ]
};

// 主组件
const DailyNewsAnimated: React.FC = () => {
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

// 带缩放动画的截图组件
const AnimatedScreenshot: React.FC<{
  screenshot: string;
  durationFrames: number;
}> = ({ screenshot, durationFrames }) => {
  const frame = useCurrentFrame();
  
  // 截图原始尺寸
  const originalWidth = 1200;
  const originalHeight = 800;
  
  // 目标尺寸（适应视频宽度）
  const targetWidth = 1000;
  const targetScale = targetWidth / originalWidth; // 0.833
  
  // 缩放动画：从 1.2 缩放到 0.833
  const scale = interpolate(
    frame,
    [0, durationFrames],
    [1.2, targetScale],
    {
      easing: Easing.out(Easing.ease),  // 先快后慢
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  const containerWidth = targetWidth;
  const containerHeight = (targetWidth / originalWidth) * originalHeight; // 667px
  
  return (
    <div style={{
      width: containerWidth,
      height: containerHeight,
      overflow: 'hidden',
      borderRadius: 16,
      border: '3px solid rgba(0, 212, 255, 0.3)',
      backgroundColor: '#1a1a2e',
      position: 'relative',
    }}>
      <img 
        src={staticFile(screenshot)} 
        alt="screenshot"
        style={{
          width: originalWidth * scale,
          height: originalHeight * scale,
          objectFit: 'cover',
          transformOrigin: 'top left',
        }}
      />
    </div>
  );
};

// 热点详情场景 - 带截图动画
const HotspotScene: React.FC<any> = ({
  rank, title, chineseText, url, screenshot, durationFrames
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '50px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* 排名和项目名称 */}
    <div style={{
      display: 'flex',
      alignItems: 'center',
      marginBottom: 30,
    }}>
      <div style={{
        width: 80,
        height: 80,
        borderRadius: '50%',
        background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: 40,
        fontWeight: 'bold',
        marginRight: 30,
        boxShadow: '0 8px 20px rgba(0, 212, 255, 0.4)',
      }}>
        {rank}
      </div>
      <div style={{
        fontSize: 44,
        color: '#64ffda',
        fontWeight: 'bold',
      }}>
        {title}
      </div>
    </div>
    
    {/* 中文解读 */}
    <div style={{
      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(123, 44, 191, 0.08))',
      borderRadius: 20,
      padding: '35px',
      marginBottom: 25,
      border: '2px solid rgba(0, 212, 255, 0.2)',
    }}>
      <p style={{
        fontSize: 38,
        color: '#e6f1ff',
        lineHeight: 1.7,
        fontWeight: 'bold',
        margin: 0,
      }}>
        {chineseText}
      </p>
    </div>
    
    {/* 截图区域 - 带缩放动画 */}
    <div style={{
      flex: 1,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      overflow: 'hidden',
    }}>
      <AnimatedScreenshot 
        screenshot={screenshot} 
        durationFrames={durationFrames}
      />
    </div>
    
    {/* URL */}
    <div style={{
      background: 'rgba(0, 0, 0, 0.4)',
      borderRadius: 12,
      padding: '20px',
      border: '2px solid rgba(100, 255, 218, 0.3)',
      marginTop: 20,
    }}>
      <p style={{
        fontSize: 28,
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
      id="DailyNewsAnimated"
      component={DailyNewsAnimated}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
