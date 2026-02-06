import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';

// 60秒竖屏版本 - 精简模板
// 时长分配：开场3s + 热点1(18s) + 热点2(18s) + 热点3(18s) + 结尾3s = 60s

const CHINESE_FONT = '"Noto Sans CJK SC", "Noto Sans SC", sans-serif';

// 60秒硬编码数据
const VIDEO_DATA = {
  date: '2026-02-06',
  fps: 30,
  totalFrames: 1800, // 60秒 @30fps
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 90, // 3秒
      text: '今天AI圈发生了什么？',
    },
    {
      id: 'hotspot_1',
      type: 'hotspot',
      startFrame: 90,
      durationFrames: 540, // 18秒
      rank: 1,
      title: 'OpenAI发布GPT-5预览版',
      text: 'GPT-5在GPQA测试中准确率达到87%，几乎是GPT-4的两倍。推理能力暴涨10倍，数学和代码能力接近人类顶级专家。',
      keyPoint: '推理能力提升10倍',
      vendor: 'OpenAI',
      logo: 'logos/openai.svg',
      url: 'https://openai.com',
      useScreenshot: false,
      audioFile: 'audio/60s/opening.mp3',
    },
    {
      id: 'hotspot_2',
      type: 'hotspot',
      startFrame: 630,
      durationFrames: 540, // 18秒
      rank: 2,
      title: 'Meta发布Llama 3.5',
      text: 'Llama 3.5在多项基准测试中超越GPT-4，且完全开源可商用。开源力量足以抗衡顶尖闭源模型。',
      keyPoint: '开源超越GPT-4',
      vendor: 'Meta',
      logo: 'logos/meta.svg',
      url: 'https://ai.meta.com',
      useScreenshot: false,
      audioFile: 'audio/60s/hotspot_1.mp3',
    },
    {
      id: 'hotspot_3',
      type: 'hotspot',
      startFrame: 1170,
      durationFrames: 540, // 18秒
      rank: 3,
      title: 'DeepMind机器人自学走路',
      text: '新算法让机器人2小时学会在陌生环境行走，无需预设编程。通过自我尝试和错误修正掌握技能。',
      keyPoint: '2小时自学走路',
      vendor: 'Google DeepMind',
      logo: 'logos/deepmind.svg',
      url: 'https://deepmind.google',
      useScreenshot: false,
      audioFile: 'audio/60s/hotspot_2.mp3',
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1710,
      durationFrames: 90, // 3秒
      text: '点赞关注，每天60秒了解AI热点！',
      audioFile: 'audio/60s/closing.mp3',
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
      {scenes.map((scene) => (
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
      return (
        <>
          <OpeningScene text={scene.text} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    case 'hotspot':
      return (
        <>
          <HotspotScene {...scene} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    case 'closing':
      return (
        <>
          <ClosingScene text={scene.text} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    default:
      return null;
  }
};

// 极简开场 - 3秒
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

// 热点详情 - 18秒（带Logo和截图区域）
const HotspotScene: React.FC<any> = ({
  rank, title, text, keyPoint, vendor, logo, useScreenshot
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '60px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* 排名标识 */}
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
    
    {/* 截图区域（预留） */}
    {useScreenshot && (
      <div style={{
        width: '100%',
        height: 400,
        backgroundColor: '#2d3748',
        borderRadius: 16,
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        color: '#8892b0',
        fontSize: 28,
        marginBottom: 40,
      }}>
        [网站截图]
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

// 极简结尾 - 3秒
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
      durationInFrames={1800}
      fps={30}
      width={1080}
      height={1920}
    />
  </>
));
