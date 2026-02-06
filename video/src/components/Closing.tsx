import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface ClosingProps {
  text: string;
}

export const Closing: React.FC<ClosingProps> = ({text}) => {
  const frame = useCurrentFrame();
  const {fps, durationInFrames} = useVideoConfig();
  
  // 淡入动画
  const opacity = interpolate(
    frame,
    [0, 20],
    [0, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  // Logo 缩放
  const logoScale = interpolate(
    frame,
    [0, 30],
    [0.8, 1],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  // 结束前的淡出
  const endOpacity = interpolate(
    frame,
    [durationInFrames - 20, durationInFrames],
    [1, 0],
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
      background: 'linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #312e81 100%)',
      opacity: Math.min(opacity, endOpacity),
    }}>
      {/* Logo */}
      <div style={{
        transform: `scale(${logoScale})`,
        marginBottom: 50,
      }}>
        <h1 style={{
          fontSize: 100,
          fontWeight: 'bold',
          margin: 0,
          background: 'linear-gradient(90deg, #00d4ff, #7b2cbf)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          textShadow: '0 0 60px rgba(0, 212, 255, 0.3)',
        }}>
          AiTrend
        </h1>
      </div>
      
      {/* 结束语 */}
      <div style={{
        maxWidth: 1200,
        textAlign: 'center',
        fontSize: 42,
        lineHeight: 1.6,
        color: '#e6f1ff',
        padding: '0 100px',
        marginBottom: 80,
      }}>
        {text}
      </div>
      
      {/* 关注提示 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 20,
        padding: '20px 50px',
        background: 'rgba(0, 212, 255, 0.1)',
        border: '1px solid rgba(0, 212, 255, 0.3)',
        borderRadius: 50,
      }}>
        <span style={{
          fontSize: 28,
          color: '#64ffda',
        }}>
          👍 点赞
        </span>
        <span style={{
          fontSize: 28,
          color: '#64ffda',
        }}>
          📌 收藏
        </span>
        <span style={{
          fontSize: 28,
          color: '#64ffda',
        }}>
          ➕ 关注
        </span>
      </div>
      
      {/* 装饰元素 */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: 4,
        background: 'linear-gradient(90deg, transparent, #00d4ff, #7b2cbf, transparent)',
      }} />
      
      <div style={{
        position: 'absolute',
        bottom: 0,
        left: 0,
        right: 0,
        height: 4,
        background: 'linear-gradient(90deg, transparent, #7b2cbf, #00d4ff, transparent)',
      }} />
    </div>
  );
};
