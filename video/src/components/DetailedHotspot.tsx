import React from 'react';
import {useCurrentFrame, useVideoConfig, interpolate} from 'remotion';

interface DetailedHotspotProps {
  rank: number;
  title: string;
  text: string;
  keyPoint?: string;
  source?: string;
}

export const DetailedHotspot: React.FC<DetailedHotspotProps> = ({
  rank,
  title,
  text,
  keyPoint,
  source,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  
  // 入场动画
  const slideIn = interpolate(
    frame,
    [0, 20],
    [-100, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}
  );
  
  const opacity = interpolate(
    frame,
    [0, 20],
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
      background: 'linear-gradient(180deg, #0a0a0f 0%, #0f172a 100%)',
      boxSizing: 'border-box',
    }}>
      {/* 排名标识 */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        marginBottom: 40,
        transform: `translateX(${slideIn}px)`,
        opacity,
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
          boxShadow: '0 0 40px rgba(0, 212, 255, 0.4)',
        }}>
          {rank}
        </div>
        
        <div style={{
          fontSize: 20,
          color: '#64ffda',
          textTransform: 'uppercase',
          letterSpacing: 4,
        }}>
          热点 #{rank}
        </div>
      </div>
      
      {/* 标题 */}
      <h2 style={{
        fontSize: 56,
        fontWeight: 'bold',
        margin: '0 0 40px 0',
        lineHeight: 1.3,
        color: '#e6f1ff',
        transform: `translateX(${slideIn}px)`,
        opacity,
      }}>
        {title}
      </h2>
      
      {/* 主要内容 */}
      <div style={{
        flex: 1,
        display: 'flex',
        gap: 60,
      }}>
        {/* 左侧：正文 */}
        <div style={{
          flex: 1.5,
          fontSize: 36,
          lineHeight: 1.8,
          color: '#a8b2d1',
        }}>
          {text}
        </div>
        
        {/* 右侧：关键信息 */}
        <div style={{
          flex: 1,
          display: 'flex',
          flexDirection: 'column',
          gap: 30,
        }}>
          {keyPoint && (
            <div style={{
              background: 'rgba(0, 212, 255, 0.1)',
              border: '1px solid rgba(0, 212, 255, 0.3)',
              borderRadius: 12,
              padding: 30,
            }}>
              <div style={{
                fontSize: 18,
                color: '#64ffda',
                marginBottom: 12,
                textTransform: 'uppercase',
                letterSpacing: 2,
              }}>
                核心观点
              </div>
              <div style={{
                fontSize: 28,
                color: '#e6f1ff',
                lineHeight: 1.5,
              }}>
                {keyPoint}
              </div>
            </div>
          )}
          
          {source && (
            <div style={{
              fontSize: 20,
              color: '#8892b0',
            }}>
              来源: {source}
            </div>
          )}
        </div>
      </div>
      
      {/* 装饰线 */}
      <div style={{
        position: 'absolute',
        bottom: 60,
        left: 120,
        right: 120,
        height: 2,
        background: 'linear-gradient(90deg, #00d4ff, transparent)',
      }} />
    </div>
  );
};
