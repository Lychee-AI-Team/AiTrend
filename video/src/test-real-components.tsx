import React from 'react';
import {Composition, Sequence, registerRoot} from 'remotion';
import {Opening} from './components/Opening';
import {DetailedHotspot} from './components/DetailedHotspot';
import {QuickSummary} from './components/QuickSummary';
import {Closing} from './components/Closing';

// 测试：使用真实组件，但无Audio

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
    },
    {
      id: 'closing',
      type: 'closing',
      startFrame: 1981,
      durationFrames: 345,
      text: '以上就是今天的AI热点全解析。AI进化的速度已经超乎想象，如果你不想错过任何前沿动态，记得点赞关注。我们明天见！',
    }
  ]
};

interface SceneData {
  id: string;
  type: 'opening' | 'detailed' | 'quick' | 'closing';
  startFrame: number;
  durationFrames: number;
  [key: string]: any;
}

const TestRealComponents: React.FC = () => {
  const {scenes, date} = inputData;
  
  return (
    <div style={{
      width: 1920,
      height: 1080,
      backgroundColor: '#0a0a0f',
      color: '#ffffff',
      overflow: 'hidden',
    }}>
      {scenes.map((scene: SceneData) => (
        <Sequence
          key={scene.id}
          from={scene.startFrame}
          durationInFrames={scene.durationFrames}
        >
          {scene.type === 'opening' && <Opening text={scene.text} date={date} />}
          {scene.type === 'detailed' && (
            <DetailedHotspot
              rank={scene.rank}
              title={scene.title}
              text={scene.text}
              keyPoint={scene.keyPoint}
              source={scene.source}
            />
          )}
          {scene.type === 'closing' && <Closing text={scene.text} />}
        </Sequence>
      ))}
    </div>
  );
};

registerRoot(() => (
  <>
    <Composition
      id="TestReal"
      component={TestRealComponents}
      durationInFrames={inputData.totalFrames}
      fps={inputData.fps}
      width={1920}
      height={1080}
    />
  </>
));
