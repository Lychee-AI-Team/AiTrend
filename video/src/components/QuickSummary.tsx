import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface QuickItem {
  rank: number;
  title: string;
  text: string;
  durationMs: number;
}

interface QuickSummaryProps {
  items: QuickItem[];
}

export const QuickSummary: React.FC<QuickSummaryProps> = ({items}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  
  // 标题动画
  const titleOpacity = interpolate(
    frame,
    [0, 15],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      padding: '80px 120px',
      background: 'linear-gradient(180deg, #0f172a 0%, #1e293b 100%)',
      boxSizing: 'border-box',
    }}>
      {/* 标题 */}
      <div style={{
        marginBottom: 50,
        opacity: titleOpacity,
      }}>
        <h2 style={{
          fontSize: 48,
          fontWeight: 'bold',
          margin: 0,
          color: '#e6f1ff',
        }}>
          更多热点
        </h2>
        <div style={{
          width: 120,
          height: 4,
          background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
          marginTop: 20,
        }} />
      </div>
      
      {/* 热点列表 */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        gap: 30,
        justifyContent: 'center',
      }}>
        {items.map((item, index) => {
          // 每个项目的入场动画
          const itemFrame = frame - (index * 10); // 错开动画
          const itemOpacity = interpolate(
            itemFrame,
            [0, 15],
            [0, 1],
            {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
          );
          const itemSlide = interpolate(
            itemFrame,
            [0, 15],
            [50, 0],
            {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
          );
          
          return (
            <div
              key={index}
              style={{
                display: 'flex',
                alignItems: 'flex-start',
                gap: 25,
                padding: '25px 35px',
                background: 'rgba(255, 255, 255, 0.03)',
                borderRadius: 12,
                border: '1px solid rgba(255, 255, 255, 0.08)',
                opacity: itemOpacity,
                transform: `translateY(${itemSlide}px)`,
              }}
            >
              {/* 排名 */}
              <div style={{
                width: 45,
                height: 45,
                borderRadius: '50%',
                background: 'rgba(0, 212, 255, 0.15)',
                border: '1px solid rgba(0, 212, 255, 0.3)',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center',
                fontSize: 22,
                fontWeight: 'bold',
                color: '#00d4ff',
                flexShrink: 0,
              }}>
                {item.rank}
              </div>
              
              {/* 内容 */}
              <div style={{
                flex: 1,
              }}>
                <div style={{
                  fontSize: 28,
                  fontWeight: 600,
                  color: '#e6f1ff',
                  marginBottom: 10,
                  lineHeight: 1.4,
                }}>
                  {item.title}
                </div>
                <div style={{
                  fontSize: 22,
                  color: '#8892b0',
                  lineHeight: 1.5,
                }}>
                  {item.text}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
