import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio, interpolate, Easing, useCurrentFrame} from 'remotion';

// 新内容版 - 增加一倍文字量 + Logo圆角

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置 - 新内容
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 4204,  // 140.22秒
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 153,
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/2026-02-06-new/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 153,
      durationFrames: 1263,
      rank: 1,
      title: 'PentestAgent',
      chineseText: 'PentestAgent是一款革命性的AI驱动安全测试框架，专为网络安全研究人员、白帽黑客和渗透测试工程师设计。它能够自动执行复杂的黑盒安全测试、智能漏洞挖掘和自动化渗透测试任务，大幅提升安全测试的效率和覆盖率。该工具利用先进的AI算法分析目标系统架构，自动识别潜在安全漏洞，生成详细的测试报告，为安全团队提供全方位的AI助手支持。相比传统的手动测试方式，PentestAgent能够节省大量人力成本，同时提高测试的准确性和全面性。在网络安全威胁日益严峻的今天，这款AI驱动的安全测试工具为企业和组织提供了强有力的安全保障，项目在GitHub上已经获得超过1400个星标，受到安全社区的广泛关注。',
      url: 'github.com/GH05TCREW/pentestagent',
      screenshot: 'screenshots-new/hotspot_1.png',
      audioFile: 'audio/2026-02-06-new/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 1416,
      durationFrames: 1325,
      rank: 2,
      title: 'X-AnyLabeling',
      chineseText: 'X-AnyLabeling是一款强大的AI辅助数据标注工具，专为机器学习和计算机视觉领域的数据预处理而设计。它集成了Segment Anything等先进的AI模型，能够自动识别图像中的对象边界，大幅简化数据标注工作流程。用户只需简单的点击操作，AI就能自动完成复杂的分割和标注任务，标注效率相比传统手工方式提升数倍。该工具支持多种标注格式导出，兼容主流深度学习框架，是CV工程师和数据科学家的得力助手。无论是目标检测、语义分割还是实例分割任务，X-AnyLabeling都能提供精准的AI辅助标注功能，大幅降低数据准备成本，加速AI模型开发周期。项目在GitHub上已经获得超过8000个星标，是数据标注领域的优秀开源工具。',
      url: 'github.com/CVHub520/X-AnyLabeling',
      screenshot: 'screenshots-new/hotspot_2.png',
      audioFile: 'audio/2026-02-06-new/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 2741,
      durationFrames: 1317,
      rank: 3,
      title: 'FinanceDatabase',
      chineseText: 'FinanceDatabase是一个全面的金融数据数据库，收录了超过30万种金融产品的详细信息，涵盖股票、ETF、基金、指数、货币、加密货币和货币市场等多个资产类别。这个数据库为量化投资者、金融分析师和数据科学家提供了丰富的金融数据资源，支持全球主要金融市场的数据查询和分析。用户可以通过简单的API调用获取特定资产的详细信息，包括历史价格、财务指标、风险评估等多维度数据。该数据库定期更新维护，确保数据的准确性和时效性，是构建量化交易策略、进行投资组合分析和风险管理的理想数据源。无论是学术研究还是商业应用，FinanceDatabase都能提供可靠的金融数据支持，项目在GitHub上已经获得超过6900个星标。',
      url: 'github.com/JerBouma/FinanceDatabase',
      screenshot: 'screenshots-new/hotspot_3.png',
      audioFile: 'audio/2026-02-06-new/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 4058,
      durationFrames: 146,
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/2026-02-06-new/closing.mp3'
    }
  ]
};

// 主组件
const DailyNewsNewContent: React.FC = () => {
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

// 开场场景 - Logo带圆角
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
    {/* Logo图片 - 带圆角 */}
    <div style={{
      width: 240,
      height: 240,
      marginBottom: 60,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      borderRadius: 40,
      overflow: 'hidden',
      boxShadow: '0 20px 60px rgba(0, 212, 255, 0.3)',
    }}>
      <img 
        src={staticFile('logos/logo.png')} 
        alt="AiTrend Logo"
        style={{
          width: '100%',
          height: '100%',
          objectFit: 'contain',
          borderRadius: 40,
        }}
        onError={(e) => {
          e.currentTarget.style.display = 'none';
          const parent = e.currentTarget.parentElement;
          if (parent) {
            parent.innerHTML = '<span style="font-size: 80px; font-weight: bold; color: #00d4ff;">AI</span>';
          }
        }}
      />
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

// 带缩放动画的截图组件 - 水平居中
const AnimatedScreenshot: React.FC<{
  screenshot: string;
  durationFrames: number;
}> = ({ screenshot, durationFrames }) => {
  const frame = useCurrentFrame();
  
  const originalWidth = 1200;
  const originalHeight = 800;
  const targetWidth = 1000;
  const targetScale = targetWidth / originalWidth;
  
  const scale = interpolate(
    frame,
    [0, durationFrames],
    [1.2, targetScale],
    {
      easing: Easing.out(Easing.ease),
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );
  
  const containerWidth = targetWidth;
  const containerHeight = (targetWidth / originalWidth) * originalHeight;
  const scaledWidth = originalWidth * scale;
  const scaledHeight = originalHeight * scale;
  const offsetX = (containerWidth - scaledWidth) / 2;
  const offsetY = (containerHeight - scaledHeight) / 2;
  
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
          width: scaledWidth,
          height: scaledHeight,
          objectFit: 'cover',
          position: 'absolute',
          left: offsetX,
          top: offsetY,
        }}
      />
    </div>
  );
};

// 热点详情场景
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
    
    {/* 中文解读 - 扩展版 */}
    <div style={{
      background: 'linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(123, 44, 191, 0.08))',
      borderRadius: 20,
      padding: '35px',
      marginBottom: 25,
      border: '2px solid rgba(0, 212, 255, 0.2)',
    }}>
      <p style={{
        fontSize: 36,
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
      id="DailyNewsNewContent"
      component={DailyNewsNewContent}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
