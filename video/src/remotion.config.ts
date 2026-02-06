import {Config} from '@remotion/cli/config';

export const config: Config = {
  // 视频默认设置
  defaults: {
    width: 1920,
    height: 1080,
    fps: 30,
  },
  
  // 预览设置
  preview: {
    // 预览端口
    port: 3000,
  },
  
  // 渲染设置
  render: {
    // 并发渲染
    concurrency: 4,
    // 图片格式
    imageFormat: 'jpeg',
    // 图片质量
    jpegQuality: 90,
  },
  
  // 日志级别
  logLevel: 'verbose',
  
  // 超时设置（毫秒）
  timeout: 300000, // 5分钟
};
