import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio, interpolate, Easing, useCurrentFrame} from 'remotion';

// 生产版视频 - 修复emoji显示 + 多平台内容

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 3182,
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 159,
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/balanced/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 159,
      durationFrames: 945,
      rank: 1,
      title: 'Overlead',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      chineseText: 'Overlead是一款智能化的销售线索管理工具，专为现代企业销售团队打造。它能够自动抓取和整理来自多个渠道的销售线索，利用AI技术对线索进行智能评分和优先级排序，帮助销售人员专注于最有价值的潜在客户。该工具还提供自动化的邮件跟进、客户关系管理和销售数据分析功能，大幅提升销售团队的转化率和工作效率。对于需要管理大量销售线索的企业来说，Overlead是一个强大的销售助手，能够优化整个销售流程，提高成单率，在Product Hunt上获得了95个赞的认可。',
      url: 'producthunt.com/products/overlead',
      screenshot: 'screenshots-balanced/hotspot_1.png',
      audioFile: 'audio/balanced/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 1104,
      durationFrames: 1003,
      rank: 2,
      title: 'PentestAgent',
      platform: 'GitHub',
      platformColor: '#24292E',
      chineseText: 'PentestAgent是一款革命性的AI驱动安全测试框架，专为网络安全研究人员、白帽黑客和渗透测试工程师设计。它能够自动执行复杂的黑盒安全测试、智能漏洞挖掘和自动化渗透测试任务，大幅提升安全测试的效率和覆盖率。该工具利用先进的AI算法分析目标系统架构，自动识别潜在安全漏洞，生成详细的测试报告，为安全团队提供全方位的AI助手支持。相比传统的手动测试方式，PentestAgent能够节省大量人力成本，同时提高测试的准确性和全面性，在GitHub上已经获得超过1400个星标。',
      url: 'github.com/GH05TCREW/pentestagent',
      screenshot: 'screenshots-balanced/hotspot_2.png',
      audioFile: 'audio/balanced/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 2107,
      durationFrames: 909,
      rank: 3,
      title: 'BayesLab',
      platform: 'Product Hunt',
      platformColor: '#DA552F',
      chineseText: 'BayesLab是一款基于贝叶斯统计的机器学习实验平台，专为数据科学家和研究人员设计。它提供了可视化的贝叶斯模型构建工具，让用户无需编写复杂代码就能构建和训练概率模型。该平台支持多种贝叶斯推断算法，包括MCMC采样和变分推断，适用于不确定性建模、A/B测试、因果推断等场景。对于需要进行概率推理和不确定性分析的项目，BayesLab提供了直观高效的解决方案，降低了贝叶斯统计的学习门槛，在Product Hunt上获得了129个赞的关注。',
      url: 'producthunt.com/products/bayeslab-2',
      screenshot: 'screenshots-balanced/hotspot_3.png',
      audioFile: 'audio/balanced/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 3016,
      durationFrames: 165,
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/balanced/closing.mp3'
    }
  ]
};

// Logo组件
const LogoWithRoundedCorners: React.FC<{size?: number}> = ({size = 240}) => (
  <div style={{
    width: size,
    height: size,
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
);

// 主组件
const DailyNewsProduction: React.FC = () => {
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
    <div style={{marginBottom: 60}}>
      <LogoWithRoundedCorners size={240} />
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

// 截图动画组件
const AnimatedScreenshot: React.FC<{screenshot: string; durationFrames: number}> = ({screenshot, durationFrames}) => {
  const frame = useCurrentFrame();
  
  const originalWidth = 1200;
  const originalHeight = 800;
  const targetWidth = 1000;
  const targetScale = targetWidth / originalWidth;
  
  const scale = interpolate(frame, [0, durationFrames], [1.2, targetScale], {
    easing: Easing.out(Easing.ease),
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });
  
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

// 热点场景 - 修复emoji为真实链接图标
const HotspotScene: React.FC<any> = ({
  rank, title, platform, platformColor, chineseText, url, screenshot, durationFrames
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '50px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* 排名、平台和名称 */}
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
        marginRight: 20,
        boxShadow: '0 8px 20px rgba(0, 212, 255, 0.4)',
      }}>
        {rank}
      </div>
      
      <div style={{flex: 1}}>
        <div style={{
          fontSize: 44,
          color: '#64ffda',
          fontWeight: 'bold',
          marginBottom: 8,
        }}>
          {title}
        </div>
        <div style={{
          display: 'inline-block',
          backgroundColor: platformColor,
          padding: '6px 16px',
          borderRadius: 20,
          fontSize: 24,
          fontWeight: 'bold',
          color: '#ffffff',
        }}>
          {platform}
        </div>
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
        fontSize: 36,
        color: '#e6f1ff',
        lineHeight: 1.7,
        fontWeight: 'bold',
        margin: 0,
      }}>
        {chineseText}
      </p>
    </div>
    
    {/* 截图动画 */}
    <div style={{
      flex: 1,
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      overflow: 'hidden',
    }}>
      <AnimatedScreenshot screenshot={screenshot} durationFrames={durationFrames} />
    </div>
    
    {/* URL - 使用SVG链接图标 */}
    <div style={{
      background: 'rgba(0, 0, 0, 0.4)',
      borderRadius: 12,
      padding: '20px',
      border: '2px solid rgba(100, 255, 218, 0.3)',
      marginTop: 20,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
    }}>
      {/* SVG链接图标 */}
      <svg 
        width="28" 
        height="28" 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="#64ffda" 
        strokeWidth="2" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        style={{marginRight: 12}}
      >
        <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
        <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
      </svg>
      <p style={{
        fontSize: 28,
        color: '#64ffda',
        margin: 0,
        fontFamily: 'monospace',
      }}>
        {url}
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
    <div style={{marginBottom: 50}}>
      <LogoWithRoundedCorners size={180} />
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
      id="DailyNewsProduction"
      component={DailyNewsProduction}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
