import React from 'react';
import {Composition, registerRoot, staticFile, Sequence, Audio} from 'remotion';
import {Opening} from './components/Opening';
import {DetailedHotspot} from './components/DetailedHotspot';
import {QuickSummary} from './components/QuickSummary';
import {Closing} from './components/Closing';

// ✅ 修复方案: 直接内联数据（避免fs模块问题）
// 数据直接嵌入代码，不依赖文件系统

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
      text: '就在刚才，OpenAI正式发布了GPT-5的预览版，这回他们不再只是优化对话，而是直接把推理能力拉到了新高度。在被称为「博士级难题」的GPQA测试中，它的准确率直接飙到了87%，几乎是GPT-4的两倍。这意味着，无论是解复杂的数学题还是写底层架构代码，GPT-5现在的表现已经无限接近人类顶级专家了。那么，我们离真正的通用人工智能，是不是又近了一大步呢？',
      keyPoint: 'GPQA测试准确率达87%，逻辑推理能力实现10倍量级提升。',
      source: 'Hacker News',
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
      text: '就在闭源模型疯狂卷性能的时候，小扎带着Llama 3.5杀回来了。这次最让人震惊的是，Llama 3.5在多项核心基准测试中，已经全面超越了昔日的霸主GPT-4。值得一提的是，它依然保持完全开源且可商用，这无疑是给全球开发者送上了一份厚礼。可以说，Meta再次用实力证明了，开源力量足以和顶尖的闭源模型分庭抗礼，开发者们的春天又来了。',
      keyPoint: '多项基准测试超越GPT-4，且完全开源可商用。',
      source: 'Hacker News',
      audioFile: 'audio/2026-02-06/detailed_2.mp3',
      durationMs: 34776
    },
    {
      id: 'detailed_3',
      type: 'detailed',
      startFrame: 3024,
      durationFrames: 1077,
      rank: 3,
      title: '机器人也会"自学成才"？DeepMind新算法让机器人2小时学会走路！',
      text: '想象一下，一个完全没有经过编程的机器人，把它扔进陌生环境里，仅仅两个小时就能学会像人一样平稳行走。DeepMind今天发布的最新强化学习算法就做到了这一点。它不再依赖人类预设的指令，而是通过不断的自我尝试和错误修正来掌握运动技能。这项技术的突破，意味着未来的服务机器人可以更快速地适应各种复杂的现实生活场景，离科幻电影里的机器人管家又近了一点。',
      keyPoint: '强化学习新算法实现零预设自学行走，环境适应效率极高。',
      source: 'Hacker News',
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
          text: '针对AI Agent在实际应用中的权限失控隐患，Moltbook社区正展开热烈讨论，试图为AI代理的行为设定清晰的安全边界。',
          durationMs: 21000
        },
        {
          rank: 5,
          title: '文献党福利：ChatPDF 3.0支持千页分析',
          text: 'ChatPDF 3.0正式上线，现在它不仅能秒读1000页的长文档，还能看懂图表并进行多文档对比，简直是学术研究的神器。',
          durationMs: 21000
        },
        {
          rank: 6,
          title: '编程巅峰对决：Claude 3.7挑战GPT-5',
          text: '最新实测显示，虽然GPT-5推理极强，但Claude 3.7在代码解释的细腻程度和逻辑连贯性上，依然对开发者有着极强的吸引力。',
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

interface DailyNewsProps {
  data: VideoData;
}

export const DailyNews: React.FC<DailyNewsProps> = ({data}) => {
  const {scenes, date} = data;
  
  return (
    <div style={{
      width: 1920,
      height: 1080,
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
          <Opening text={scene.text} date={date} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    case 'detailed':
      return (
        <>
          <DetailedHotspot
            rank={scene.rank}
            title={scene.title}
            text={scene.text}
            keyPoint={scene.keyPoint}
            source={scene.source}
          />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    case 'quick':
      return (
        <>
          <QuickSummary items={scene.items} />
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
          <Closing text={scene.text} />
          <Audio src={staticFile(scene.audioFile)} />
        </>
      );
    
    default:
      return null;
  }
};

registerRoot(() => (
  <>
    <Composition
      id="DailyNews"
      component={DailyNews}
      durationInFrames={inputData.totalFrames || 6300}
      fps={inputData.fps || 30}
      width={1920}
      height={1080}
      defaultProps={{
        data: inputData
      }}
    />
  </>
));
