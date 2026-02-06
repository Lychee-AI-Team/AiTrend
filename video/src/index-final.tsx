import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio, interpolate, Easing, useCurrentFrame} from 'remotion';

// 最终版视频 - 5选3成功热点 + 开头结尾Logo圆角

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 视频配置
const VIDEO_CONFIG = {
  fps: 30,
  totalFrames: 3699,  // 123.30秒
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 155,  // 5.18秒
      text: '欢迎收看AiTrend，今天AI圈发生了什么？让我们一起来看看最新的AI热点。',
      audioFile: 'audio/final/opening.mp3'
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 155,
      durationFrames: 1139,  // 37.98秒
      rank: 1,
      title: 'SGLang',
      chineseText: 'SGLang是一款高性能的大语言模型和多模态模型服务框架，专为大规模AI应用部署而设计。它提供了极速的模型推理能力，支持多种主流大语言模型架构，能够同时处理文本、图像等多种模态数据。该框架采用先进的推理优化技术，包括动态批处理、智能缓存和并行计算，显著提升了模型服务吞吐量和响应速度。对于需要部署大模型服务的企业和开发者来说，SGLang是一个理想的解决方案，它简化了模型服务化流程，降低了运维复杂度。无论是构建智能客服、内容生成还是多模态AI应用，SGLang都能提供稳定高效的基础架构支持，项目在GitHub上已经获得超过23000个星标。',
      url: 'github.com/sgl-project/sglang',
      screenshot: 'screenshots-final/test_1.png',
      audioFile: 'audio/final/hotspot_1.mp3'
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 1294,
      durationFrames: 1206,  // 40.21秒
      rank: 2,
      title: 'PR Agent',
      chineseText: 'PR Agent是一款开源的AI驱动代码审查工具，专为提升代码质量和团队协作效率而设计。它能够自动分析Pull Request中的代码变更，智能识别潜在的代码缺陷、安全漏洞和性能问题，并提供详细的改进建议。该工具支持多种编程语言和主流代码托管平台，可以无缝集成到现有的开发工作流中。通过AI辅助代码审查，PR Agent大幅减轻了人工审查的工作量，同时提高了问题发现的准确率。对于追求代码质量的开发团队来说，这是一个极具价值的开发效率工具，能够帮助团队建立更完善的代码审查机制，提升整体软件质量，项目在GitHub上已经获得超过10000个星标。',
      url: 'github.com/qodo-ai/pr-agent',
      screenshot: 'screenshots-final/test_2.png',
      audioFile: 'audio/final/hotspot_2.mp3'
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 2500,
      durationFrames: 1058,  // 35.28秒
      rank: 3,
      title: 'Qwen3-Coder',
      chineseText: 'Qwen3-Coder是阿里巴巴通义千问团队开源的代码大模型，专为软件开发场景优化设计。它在代码生成、代码理解、Bug修复和代码重构等任务上表现出色，支持多种主流编程语言。该模型基于海量代码数据训练，深刻理解编程逻辑和软件工程最佳实践，能够为开发者提供智能编程辅助。无论是自动补全、函数生成还是复杂算法实现，Qwen3-Coder都能提供高质量的代码建议。作为国产AI的重要突破，这款代码模型在国际开源社区获得广泛认可，为中文开发者提供了强大的AI编程助手，项目在GitHub上已经获得超过15000个星标。',
      url: 'github.com/QwenLM/Qwen3-Coder',
      screenshot: 'screenshots-final/test_3.png',
      audioFile: 'audio/final/hotspot_3.mp3'
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 3558,
      durationFrames: 141,  // 4.64秒
      text: '以上就是今天的AI热点资讯。点赞关注，AiTrend带你了解最新AI动态。',
      audioFile: 'audio/final/closing.mp3'
    }
  ]
};

// Logo组件 - 带圆角
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
const DailyNewsFinal: React.FC = () => {
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

// 开场场景 - 带Logo圆角
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

// 带缩放动画的截图组件
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

// 结尾场景 - 带Logo圆角
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
    {/* 结尾也加Logo圆角 */}
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
      id="DailyNewsFinal"
      component={DailyNewsFinal}
      durationInFrames={VIDEO_CONFIG.totalFrames}
      fps={VIDEO_CONFIG.fps}
      width={1080}
      height={1920}
    />
  </>
));
