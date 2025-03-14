import React, { useState, useRef, useEffect } from 'react';
import { Button } from '../../../ui/Button';
import { Play, Pause, SkipForward } from 'lucide-react';

interface OnboardingVideoProps {
  onComplete: () => void;
  onSkip: () => void;
}

const OnboardingVideo: React.FC<OnboardingVideoProps> = ({ onComplete, onSkip }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [progress, setProgress] = useState(0);
  const [videoDuration, setVideoDuration] = useState(0);
  const [canComplete, setCanComplete] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Video source - replace with your actual onboarding video
  const videoSrc = "https://storage.googleapis.com/webfundamentals-assets/videos/chrome.mp4";

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      const currentProgress = (video.currentTime / video.duration) * 100;
      setProgress(currentProgress);
      
      // Allow completion after watching 80% of the video
      if (currentProgress > 80 && !canComplete) {
        setCanComplete(true);
      }
    };

    const handleLoadedMetadata = () => {
      setVideoDuration(video.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCanComplete(true);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('ended', handleEnded);
    };
  }, [canComplete]);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs < 10 ? '0' : ''}${secs}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-sm p-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold mb-2">Welcome to triggrHub</h1>
        <p className="text-gray-600">
          Watch this short video to learn how to use the platform
        </p>
      </div>

      <div className="space-y-6">
        <div className="relative rounded-lg overflow-hidden bg-black aspect-video">
          <video
            ref={videoRef}
            src={videoSrc}
            className="w-full h-full"
            onClick={togglePlayPause}
          />
          
          {/* Video controls */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
            <div className="flex items-center gap-4">
              <button 
                onClick={togglePlayPause}
                className="text-white hover:text-emerald-400 transition-colors"
              >
                {isPlaying ? <Pause size={24} /> : <Play size={24} />}
              </button>
              
              <div className="flex-1 space-y-1">
                {/* Progress bar */}
                <div className="h-1 bg-gray-600 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-emerald-400" 
                    style={{ width: `${progress}%` }}
                  />
                </div>
                
                {/* Time display */}
                <div className="flex justify-between text-xs text-white">
                  <span>{formatTime(videoRef.current?.currentTime || 0)}</span>
                  <span>{formatTime(videoDuration)}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="flex gap-4">
          <Button
            onClick={onSkip}
            variant="outline"
            className="flex-1"
          >
            <SkipForward size={16} className="mr-2" />
            Skip
          </Button>
          
          <Button
            onClick={onComplete}
            className="flex-1"
            disabled={!canComplete}
          >
            {canComplete ? 'Continue' : 'Please watch the video'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default OnboardingVideo;
