import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface OpeningProps {
  text: string;
  date: string;
}

export const Opening: React.FC<OpeningProps> = ({text, date}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  
  // 淡入动画
  const opacity = interpolate(
    frame,
    [0, 30],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  // 标题缩放
  const scale = interpolate(
    frame,
    [0, 30],
    [0.8, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  return (
    <div style={{
      width: '100%',
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      background: 'linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 50%, #16213e 100%)',
      opacity,
    }}>
      {/* Logo/标题 */}
      <div style={{
        transform: `scale(${scale})`,
        textAlign: 'center',
      }}>
        <h1 style={{
          fontSize: 120,
          fontWeight: 'bold',
          margin: 0,
          background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0 0 60px rgba(0, 212, 255, 0.3)',
        }}>
          AiTrend
        </h1>
        
        <p style={{
          fontSize: 36,
          color: '#8892b0',
          marginTop: 20,
          letterSpacing: 8,
        }}>
          AI 热点日报
        </p>
      </div>
      
      {/* 日期 */}
      <div style={{
        position: 'absolute',
        top: 60,
        right: 80,
        fontSize: 28,
        color: '#64ffda',
        fontWeight: 500,
      }}>
        {date}
      </div>
      
      {/* 开场文字 */}
      <div style={{
        position: 'absolute',
        bottom: 150,
        left: '50%',
        transform: 'translateX(-50%)',
        maxWidth: 1400,
        textAlign: 'center',
        fontSize: 42,
        lineHeight: 1.6,
        color: '#e6f1ff',
        padding: '0 100px',
      }}>
        {text}
      </div>
      
      {/* 装饰元素 */}
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 4,
        background: 'linear-gradient(90deg, transparent, #00d4ff, #7b2cbf, transparent)',
      }} />
    </div>
  );
};
