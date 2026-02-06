import React from 'react';
import {Composition, Sequence, registerRoot, staticFile, Audio} from 'remotion';
import {Opening} from './components/Opening';
import {DetailedHotspot} from './components/DetailedHotspot';
import {QuickSummary} from './components/QuickSummary';
import {Closing} from './components/Closing';

// 竖屏版本 - 1080x1920 (9:16)

const inputData = {
  date: '2026-02-06',
  fps: 30,
  totalFrames: 6300,
  scenes: [
    {
      id: 'opening',
      type: 'opening',
      startFrame: 0,
      durationFrames: 852,
      text: '大家好，今天是2026年2月6日，欢迎收看AI前哨站。今天的AI圈可谓是迎来了史诗级的震荡，OpenAI终于亮出了大杀器GPT-5预览版，而Meta的开源神作Llama 3.5也紧随其后正面硬刚，全球AI竞赛已经进入白热化阶段。接下来，让我们进入今天的深度播报。',
      audioFile: 'audio/2026-02-06/opening.mp3',
      durationMs: 28404
    },
    {
      id: 'detailed_1',
      type: 'detailed',
      startFrame: 852,
      durationFrames: 1129,
      rank: 1,
      title: 'OpenAI王炸发布：GPT-5预览版降临，推理能力暴涨10倍！',
      text: '就在刚才，OpenAI正式发布了GPT-5的预览版，这回他们不再只是优化对话，而是直接把推理能力拉到了新高度。在被称为「博士级难题」的GPQA测试中，它的准确率直接飙到了87%，几乎是GPT-4的两倍。',
      keyPoint: 'GPQA测试准确率达87%，逻辑推理能力实现10倍量级提升。',
      source: 'Hacker News',
      vendor: 'OpenAI',
      logo: 'logos/openai.svg',
      audioFile: 'audio/2026-02-06/detailed_1.mp3',
      durationMs: 37656
    },
    {
      id: 'detailed_2',
      type: 'detailed',
      startFrame: 1981,
      durationFrames: 1043,
      rank: 2,
      title: '开源界的狂欢！Meta发布Llama 3.5，性能正式超越GPT-4！',
      text: '就在闭源模型疯狂卷性能的时候，小扎带着Llama 3.5杀回来了。这次最让人震惊的是，Llama 3.5在多项核心基准测试中，已经全面超越了昔日的霸主GPT-4。值得一提的是，它依然保持完全开源且可商用。',
      keyPoint: '多项基准测试超越GPT-4，且完全开源可商用。',
      source: 'Hacker News',
      vendor: 'Meta',
      logo: 'logos/meta.svg',
      audioFile: 'audio/2026-02-06/detailed_2.mp3',
      durationMs: 34776
    },
    {
      id: 'detailed_3',
      type: 'detailed',
      startFrame: 3024,
      durationFrames: 1077,
      rank: 3,
      title: 'DeepMind新算法让机器人2小时学会走路！',
      text: 'DeepMind今天发布的最新强化学习算法让机器人可以在陌生环境中自学行走，无需预先编程，仅仅两个小时就能学会像人一样平稳行走。',
      keyPoint: '强化学习新算法实现零预设自学行走。',
      source: 'Hacker News',
      vendor: 'Google DeepMind',
      logo: 'logos/deepmind.svg',
      audioFile: 'audio/2026-02-06/detailed_3.mp3',
      durationMs: 35928
    },
    {
      id: 'quick_summary',
      type: 'quick',
      startFrame: 4101,
      durationFrames: 1065,
      items: [
        {
          rank: 4,
          title: 'AI Agent安全防线在哪里？',
          text: 'Moltbook社区正展开热烈讨论AI Agent权限边界。',
          durationMs: 21000
        },
        {
          rank: 5,
          title: 'ChatPDF 3.0支持千页分析',
          text: 'ChatPDF 3.0能秒读1000页长文档，还能看懂图表。',
          durationMs: 21000
        },
        {
          rank: 6,
          title: 'Claude 3.7挑战GPT-5',
          text: 'Claude 3.7在代码解释细腻度上依然有优势。',
          durationMs: 21000
        }
      ],
      audioFiles: [
        'audio/2026-02-06/quick_1.mp3',
        'audio/2026-02-06/quick_2.mp3',
        'audio/2026-02-06/quick_3.mp3'
      ],
      durationMs: 35532
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 5166,
      durationFrames: 345,
      text: '以上就是今天的AI热点全解析。AI进化的速度已经超乎想象，如果你不想错过任何前沿动态，记得点赞关注。我们明天见！',
      audioFile: 'audio/2026-02-06/closing.mp3',
      durationMs: 11520
    }
  ]
};

interface VideoData {
  date: string;
  fps: number;
  totalFrames: number;
  scenes: SceneData[];
}

interface SceneData {
  id: string;
  type: 'opening' | 'detailed' | 'quick' | 'closing';
  startFrame: number;
  durationFrames: number;
  [key: string]: any;
}

// 竖屏组件
const DailyNewsVertical: React.FC<{data: VideoData}> = ({data}) => {
  const {scenes, date} = data;
  
  return (
    <div style={{
      width: 1080,  // 竖屏宽度
      height: 1920, // 竖屏高度
      backgroundColor: '#0a0a0f',
      fontFamily: '"Noto Sans CJK SC", "Noto Sans SC", sans-serif',
      color: '#ffffff',
      overflow: 'hidden',
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

const renderScene = (scene: SceneData, date: string) => {
  switch (scene.type) {
    case 'opening':
      return (
        <>
          <OpeningVertical text={scene.text} date={date} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    case 'detailed':
      return (
        <>
          <DetailedHotspotVertical
            rank={scene.rank}
            title={scene.title}
            text={scene.text}
            keyPoint={scene.keyPoint}
            source={scene.source}
            vendor={scene.vendor}
            logo={scene.logo}
          />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    case 'quick':
      return (
        <>
          <QuickSummaryVertical items={scene.items} />
          {scene.audioFiles.map((file: string, idx: number) => (
            <Audio
              key={idx}
              src={staticFile(file)}
              startFrom={idx === 0 ? 0 : undefined}
            />
          ))}
        </>
      );
    
    case 'closing':
      return (
        <>
          <ClosingVertical text={scene.text} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    default:
      return null;
  }
};

// 竖屏开场组件
const OpeningVertical: React.FC<{text: string, date: string}> = ({text, date}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0a0a0f 0%, #1a1a2e 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '80px 60px',
  }}>
    <h1 style={{
      fontSize: 80,
      background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
      WebkitBackgroundClip: 'text',
      WebkitTextFillColor: 'transparent',
      marginBottom: 20,
    }}>
      AiTrend
    </h1>
    <p style={{
      fontSize: 40,
      color: '#8892b0',
      marginBottom: 60,
    }}>
      AI 热点日报
    </p>
    <p style={{
      fontSize: 32,
      color: '#64ffda',
      marginBottom: 40,
    }}>
      {date}
    </p>
    <p style={{
      fontSize: 36,
      color: '#e6f1ff',
      lineHeight: 1.6,
      textAlign: 'center',
    }}>
      {text}
    </p>
  </div>
);

// 竖屏详细播报组件（带Logo）
const DetailedHotspotVertical: React.FC<any> = ({
  rank, title, text, keyPoint, source, vendor, logo
}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
    padding: '100px 60px',
    display: 'flex',
    flexDirection: 'column',
  }}>
    {/* Logo区域 */}
    {logo && (
      <div style={{
        width: 120,
        height: 120,
        borderRadius: 20,
        backgroundColor: '#ffffff',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        marginBottom: 40,
        overflow: 'hidden',
      }}>
        <img 
          src={staticFile(logo)} 
          alt={vendor}
          style={{width: 80, height: 80, objectFit: 'contain'}}
          onError={(e) => {e.currentTarget.style.display = 'none'}}
        />
      </div>
    )}
    
    {/* 排名 */}
    <div style={{
      width: 60,
      height: 60,
      borderRadius: '50%',
      background: 'linear-gradient(135deg, #00d4ff, #7b2cbf)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      fontSize: 28,
      fontWeight: 'bold',
      marginBottom: 30,
    }}>
      {rank}
    </div>
    
    {/* 标题 */}
    <h2 style={{
      fontSize: 48,
      fontWeight: 'bold',
      color: '#e6f1ff',
      marginBottom: 40,
      lineHeight: 1.3,
    }}>
      {title}
    </h2>
    
    {/* 正文 */}
    <p style={{
      fontSize: 36,
      color: '#a8b2d1',
      lineHeight: 1.8,
      marginBottom: 40,
    }}>
      {text}
    </p>
    
    {/* 核心观点 */}
    {keyPoint && (
      <div style={{
        background: 'rgba(0, 212, 255, 0.1)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 16,
        padding: 30,
        marginTop: 'auto',
      }}>
        <p style={{fontSize: 24, color: '#64ffda', marginBottom: 10}}>
          核心观点
        </p>
        <p style={{fontSize: 32, color: '#e6f1ff'}}>
          {keyPoint}
        </p>
      </div>
    )}
    
    {/* 来源 */}
    <p style={{
      fontSize: 24,
      color: '#8892b0',
      marginTop: 20,
    }}>
      来源: {source}
    </p>
  </div>
);

// 竖屏快速播报组件
const QuickSummaryVertical: React.FC<any> = ({items}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: '#1e293b',
    padding: '100px 60px',
  }}>
    <h2 style={{
      fontSize: 48,
      fontWeight: 'bold',
      color: '#e6f1ff',
      marginBottom: 60,
    }}>
      更多热点
    </h2>
    
    {items.map((item: any, idx: number) => (
      <div key={idx} style={{
        background: 'rgba(255, 255, 255, 0.05)',
        borderRadius: 16,
        padding: 30,
        marginBottom: 30,
      }}>
        <div style={{
          width: 40,
          height: 40,
          borderRadius: '50%',
          background: 'rgba(0, 212, 255, 0.2)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: 20,
          color: '#00d4ff',
          marginBottom: 15,
        }}>
          {item.rank}
        </div>
        <h3 style={{
          fontSize: 32,
          color: '#e6f1ff',
          marginBottom: 10,
        }}>
          {item.title}
        </h3>
        <p style={{
          fontSize: 28,
          color: '#8892b0',
        }}>
          {item.text}
        </p>
      </div>
    ))}
  </div>
);

// 竖屏结尾组件
const ClosingVertical: React.FC<{text: string}> = ({text}) => (
  <div style={{
    width: 1080,
    height: 1920,
    background: 'linear-gradient(180deg, #1e1b4b 0%, #312e81 100%)',
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    padding: '80px 60px',
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
      fontSize: 36,
      color: '#e6f1ff',
      textAlign: 'center',
      lineHeight: 1.6,
      marginBottom: 60,
    }}>
      {text}
    </p>
    <div style={{
      display: 'flex',
      gap: 20,
    }}>
      <span style={{fontSize: 32, color: '#64ffda'}}>👍 点赞</span>
      <span style={{fontSize: 32, color: '#64ffda'}}>📌 收藏</span>
      <span style={{fontSize: 32, color: '#64ffda'}}>➕ 关注</span>
    </div>
  </div>
);

registerRoot(() => (
  <>
    <Composition
      id="DailyNewsVertical"
      component={DailyNewsVertical}
      durationInFrames={inputData.totalFrames || 6300}
      fps={inputData.fps || 30}
      width={1080}   // 竖屏宽度
      height={1920}  // 竖屏高度
      defaultProps={{
        data: inputData
      }}
    />
  </>
));
