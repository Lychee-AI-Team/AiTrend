import {Composition, staticFile} from 'remotion';
import {DailyNews} from './compositions/DailyNews';

// 加载输入数据（从环境变量或静态文件）
const loadInputData = () => {
  // 优先从环境变量读取
  const inputPath = process.env.REMOTION_INPUT;
  
  if (inputPath) {
    // 如果在 Node 环境，直接读取文件
    if (typeof window === 'undefined') {
      const fs = require('fs');
      const data = fs.readFileSync(inputPath, 'utf-8');
      return JSON.parse(data);
    }
  }
  
  // 默认返回空数据（预览时使用）
  return {
    date: '2026-02-06',
    fps: 30,
    totalFrames: 6300, // 3分30秒 @30fps
    scenes: []
  };
};

const inputData = loadInputData();

export const RemotionRoot: React.FC = () => {
  return (
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
  );
};
